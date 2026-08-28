#!/usr/bin/env python3
"""Prepare the attached WAV for the attached int8 TFLite KWS model.

This script contains a small NumPy reference executor for the seven built-in
operators used by this particular model. It avoids requiring TensorFlow or a
TFLite runtime in the host environment.
"""

from __future__ import annotations

import csv
import json
import struct
import wave
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "upload" / "p1_lin_12k_s1_pool.tflite"
WAV_PATH = ROOT / "upload" / "sample_13_spd0.93_p1.36_e1.09_d1.10.wav"
OUT_DIR = ROOT / "kws_results"


class FlatBuffer:
    def __init__(self, path: Path):
        self.data = path.read_bytes()

    def unpack(self, fmt: str, offset: int):
        return struct.unpack_from(fmt, self.data, offset)[0]

    def u16(self, offset: int) -> int:
        return self.unpack("<H", offset)

    def u32(self, offset: int) -> int:
        return self.unpack("<I", offset)

    def i32(self, offset: int) -> int:
        return self.unpack("<i", offset)

    def root(self) -> int:
        return self.u32(0)

    def field(self, table: int, index: int):
        vtable = table - self.i32(table)
        entry = 4 + 2 * index
        if entry >= self.u16(vtable):
            return None
        relative = self.u16(vtable + entry)
        return table + relative if relative else None

    def indirect(self, offset: int) -> int:
        return offset + self.u32(offset)

    def scalar(self, table: int, index: int, fmt: str, default=0):
        offset = self.field(table, index)
        return default if offset is None else self.unpack(fmt, offset)

    def vector_positions(self, table: int, index: int, element_size: int = 4):
        offset = self.field(table, index)
        if offset is None:
            return []
        vector = self.indirect(offset)
        return [vector + 4 + i * element_size for i in range(self.u32(vector))]

    def vector_i32(self, table: int, index: int):
        return [self.i32(p) for p in self.vector_positions(table, index)]

    def vector_tables(self, table: int, index: int):
        return [self.indirect(p) for p in self.vector_positions(table, index)]

    def string(self, table: int, index: int):
        offset = self.field(table, index)
        if offset is None:
            return None
        start = self.indirect(offset)
        size = self.u32(start)
        return self.data[start + 4 : start + 4 + size].decode("utf-8")

    def vector_bytes(self, table: int, index: int) -> bytes:
        offset = self.field(table, index)
        if offset is None:
            return b""
        start = self.indirect(offset)
        size = self.u32(start)
        return self.data[start + 4 : start + 4 + size]


def round_away_from_zero(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))


class Model:
    TYPE_TO_DTYPE = {2: np.int32, 9: np.int8}

    def __init__(self, path: Path):
        self.fb = FlatBuffer(path)
        root = self.fb.root()
        if self.fb.data[4:8] != b"TFL3":
            raise ValueError("Not a TFLite FlatBuffer")
        self.description = self.fb.string(root, 3)
        self.opcode_tables = self.fb.vector_tables(root, 1)
        self.subgraph = self.fb.vector_tables(root, 2)[0]
        self.tensor_tables = self.fb.vector_tables(self.subgraph, 0)
        self.operator_tables = self.fb.vector_tables(self.subgraph, 3)
        self.inputs = self.fb.vector_i32(self.subgraph, 1)
        self.outputs = self.fb.vector_i32(self.subgraph, 2)
        self.buffer_tables = self.fb.vector_tables(root, 4)

    def tensor_info(self, index: int):
        table = self.tensor_tables[index]
        quant_field = self.fb.field(table, 4)
        quant = self.fb.indirect(quant_field) if quant_field is not None else None
        scales = [] if quant is None else [self.fb.unpack("<f", p) for p in self.fb.vector_positions(quant, 2)]
        zps = [] if quant is None else [self.fb.unpack("<q", p) for p in self.fb.vector_positions(quant, 3, 8)]
        return {
            "name": self.fb.string(table, 3),
            "shape": self.fb.vector_i32(table, 0),
            "type": self.fb.scalar(table, 1, "<b"),
            "buffer": self.fb.scalar(table, 2, "<I"),
            "scales": np.asarray(scales, dtype=np.float64),
            "zero_points": np.asarray(zps, dtype=np.int64),
            "quantized_dimension": 0 if quant is None else self.fb.scalar(quant, 6, "<i"),
        }

    def constant(self, index: int):
        info = self.tensor_info(index)
        payload = self.fb.vector_bytes(self.buffer_tables[info["buffer"]], 0)
        if not payload:
            return None
        dtype = self.TYPE_TO_DTYPE[info["type"]]
        return np.frombuffer(payload, dtype=dtype).reshape(info["shape"])

    def opcode(self, operator: int) -> int:
        op = self.operator_tables[operator]
        opcode_index = self.fb.scalar(op, 0, "<I")
        code = self.opcode_tables[opcode_index]
        return self.fb.scalar(code, 3, "<i", self.fb.scalar(code, 0, "<b"))

    def operator_io(self, operator: int):
        op = self.operator_tables[operator]
        return self.fb.vector_i32(op, 1), self.fb.vector_i32(op, 2)


def quant_params(model: Model, tensor_index: int):
    info = model.tensor_info(tensor_index)
    scales = info["scales"]
    zps = info["zero_points"]
    if scales.size == 0:
        return None, None
    return scales, zps if zps.size else np.zeros_like(scales, dtype=np.int64)


def quantize_real(values, model: Model, output_index: int):
    scales, zps = quant_params(model, output_index)
    if scales.size != 1:
        raise ValueError("Expected per-tensor output quantization")
    q = round_away_from_zero(np.asarray(values) / scales[0] + zps[0])
    return np.clip(q, -128, 127).astype(np.int8)


def conv2d_int8(x, weights, bias, model: Model, x_index: int, w_index: int, out_index: int):
    # TFLite weight layout is OHWI. All Conv2D operations in this model use
    # stride 1 and VALID padding; output dimensions make this unambiguous.
    out_shape = model.tensor_info(out_index)["shape"]
    _, out_h, out_w, out_c = out_shape
    _, filter_h, filter_w, _ = weights.shape
    acc = np.zeros(out_shape, dtype=np.int64)
    for kh in range(filter_h):
        for kw in range(filter_w):
            x_slice = x[:, kh : kh + out_h, kw : kw + out_w, :].astype(np.int32)
            w_slice = weights[:, kh, kw, :].astype(np.int32)
            acc += np.tensordot(x_slice, w_slice, axes=([-1], [-1])).astype(np.int64)
    acc += bias.reshape(1, 1, 1, out_c).astype(np.int64)
    x_scales, _ = quant_params(model, x_index)
    w_scales, _ = quant_params(model, w_index)
    out_scales, out_zps = quant_params(model, out_index)
    multipliers = x_scales[0] * w_scales / out_scales[0]
    q = round_away_from_zero(acc * multipliers.reshape(1, 1, 1, out_c)) + out_zps[0]
    return np.clip(q, -128, 127).astype(np.int8)


def depthwise_int8(x, weights, bias, model: Model, x_index: int, w_index: int, out_index: int):
    out_shape = model.tensor_info(out_index)["shape"]
    _, out_h, out_w, channels = out_shape
    _, filter_h, filter_w, _ = weights.shape
    acc = np.zeros(out_shape, dtype=np.int64)
    for kh in range(filter_h):
        for kw in range(filter_w):
            acc += x[:, kh : kh + out_h, kw : kw + out_w, :].astype(np.int64) * weights[0, kh, kw, :].astype(np.int64)
    acc += bias.reshape(1, 1, 1, channels).astype(np.int64)
    x_scales, _ = quant_params(model, x_index)
    w_scales, _ = quant_params(model, w_index)
    out_scales, out_zps = quant_params(model, out_index)
    multipliers = x_scales[0] * w_scales / out_scales[0]
    q = round_away_from_zero(acc * multipliers.reshape(1, 1, 1, channels)) + out_zps[0]
    return np.clip(q, -128, 127).astype(np.int8)


def execute(model: Model, model_input: np.ndarray):
    tensors = {model.inputs[0]: model_input}
    for index in range(len(model.tensor_tables)):
        value = model.constant(index)
        if value is not None:
            tensors[index] = value

    for op_index in range(len(model.operator_tables)):
        code = model.opcode(op_index)
        inputs, outputs = model.operator_io(op_index)
        out = outputs[0]
        if code == 3:  # CONV_2D
            tensors[out] = conv2d_int8(tensors[inputs[0]], tensors[inputs[1]], tensors[inputs[2]], model, inputs[0], inputs[1], out)
        elif code == 4:  # DEPTHWISE_CONV_2D
            tensors[out] = depthwise_int8(tensors[inputs[0]], tensors[inputs[1]], tensors[inputs[2]], model, inputs[0], inputs[1], out)
        elif code == 101:  # ABS
            tensors[out] = np.clip(np.abs(tensors[inputs[0]].astype(np.int16)), 0, 127).astype(np.int8)
        elif code == 28:  # TANH
            in_scales, in_zps = quant_params(model, inputs[0])
            real = (tensors[inputs[0]].astype(np.float64) - in_zps[0]) * in_scales[0]
            tensors[out] = quantize_real(np.tanh(real), model, out)
        elif code == 22:  # RESHAPE
            tensors[out] = tensors[inputs[0]].reshape(model.tensor_info(out)["shape"])
        elif code == 34:  # PAD
            pads = tensors[inputs[1]].astype(int)
            tensors[out] = np.pad(tensors[inputs[0]], [(int(a), int(b)) for a, b in pads], constant_values=0)
        elif code == 0:  # ADD
            a_scales, a_zps = quant_params(model, inputs[0])
            b_scales, b_zps = quant_params(model, inputs[1])
            real = ((tensors[inputs[0]].astype(np.float64) - a_zps[0]) * a_scales[0] +
                    (tensors[inputs[1]].astype(np.float64) - b_zps[0]) * b_scales[0])
            tensors[out] = quantize_real(real, model, out)
        else:
            raise NotImplementedError(f"Unsupported builtin operator code {code}")
    return tensors[model.outputs[0]], tensors


def load_wav_int16(path: Path):
    with wave.open(str(path), "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("Expected mono, 16-bit PCM WAV")
        rate = wav.getframerate()
        samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
    return rate, samples


def main():
    OUT_DIR.mkdir(exist_ok=True)
    model = Model(MODEL_PATH)
    input_info = model.tensor_info(model.inputs[0])
    output_info = model.tensor_info(model.outputs[0])
    sample_rate, pcm = load_wav_int16(WAV_PATH)
    if sample_rate != 16000:
        raise ValueError(f"Expected 16 kHz audio, got {sample_rate} Hz")

    required = int(np.prod(input_info["shape"]))
    if pcm.size > required:
        pcm = pcm[-required:]
    padded = np.zeros(required, dtype=np.int16)
    padded[-pcm.size :] = pcm

    # int16 PCM normalized by 32768, then quantized with scale 1/128:
    # q = round((pcm / 32768) / (1 / 128)) = round(pcm / 256).
    input_flat = np.clip(round_away_from_zero(padded.astype(np.float64) / 256.0), -128, 127).astype(np.int8)
    model_input = input_flat.reshape(input_info["shape"])
    output, _ = execute(model, model_input)

    input_path = OUT_DIR / "sample_13_model_input_int8.bin"
    output_path = OUT_DIR / "sample_13_model_output_int8.bin"
    float_path = OUT_DIR / "sample_13_model_output_float32.bin"
    csv_path = OUT_DIR / "sample_13_model_output.csv"
    manifest_path = OUT_DIR / "manifest.json"
    readme_path = OUT_DIR / "README.md"

    input_path.write_bytes(model_input.tobytes(order="C"))
    output_path.write_bytes(output.tobytes(order="C"))
    out_scale = float(output_info["scales"][0])
    out_zp = int(output_info["zero_points"][0])
    output_float = (output.astype(np.float32) - out_zp) * out_scale
    float_path.write_bytes(output_float.astype("<f4").tobytes(order="C"))

    with csv_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "int8", "dequantized"])
        for i, (q, value) in enumerate(zip(output.reshape(-1), output_float.reshape(-1))):
            writer.writerow([i, int(q), f"{float(value):.9g}"])

    manifest = {
        "model": MODEL_PATH.name,
        "wav": WAV_PATH.name,
        "wav_sample_rate_hz": sample_rate,
        "wav_samples": int(pcm.size),
        "wav_duration_seconds": pcm.size / sample_rate,
        "input_shape": input_info["shape"],
        "input_dtype": "int8",
        "input_scale": float(input_info["scales"][0]),
        "input_zero_point": int(input_info["zero_points"][0]),
        "input_samples": required,
        "input_duration_seconds": required / sample_rate,
        "placement": "right-aligned; leading silence",
        "leading_zero_samples": required - int(pcm.size),
        "output_shape": output_info["shape"],
        "output_dtype": "int8",
        "output_scale": out_scale,
        "output_zero_point": out_zp,
        "output_int8": [int(v) for v in output.reshape(-1)],
        "output_dequantized": [float(v) for v in output_float.reshape(-1)],
        "execution_note": "Generated by a NumPy reference executor; integer requantization can differ by 1 LSB from a platform TFLite kernel.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    readme_path.write_text(
        "# Wake-word model input and outputs\n\n"
        "- `sample_13_model_input_int8.bin`: 65,792 raw int8 bytes in TFLite row-major order for `[1,257,1,256]`.\n"
        "- `sample_13_model_output_int8.bin`: 16 raw int8 output bytes for `[1,16,1,1]`.\n"
        "- `sample_13_model_output_float32.bin`: 16 little-endian float32 dequantized output values.\n"
        "- `sample_13_model_output.csv`: human-readable output values.\n"
        "- `manifest.json`: shapes, quantization, padding, and values.\n\n"
        "The 0.697-second WAV was right-aligned in the model's 4.112-second input window and padded with leading silence. "
        "PCM conversion was `q = round(pcm_int16 / 256)`, clipped to `[-128,127]`.\n\n"
        "The stored output was produced by the included NumPy reference executor. A native TFLite runtime may differ by one least-significant bit "
        "because optimized kernels can use slightly different fixed-point rounding.\n"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
