#!/usr/bin/env python3
"""
TFLite Model C Array Generator

This script executes a TFLite model with random input data and generates
C header files containing uint8_t arrays for both input and output tensors.
Supports 8-bit and 16-bit quantized models.
"""

import argparse
import numpy as np
import tensorflow as tf
import sys
from pathlib import Path


def generate_random_input(input_details):
    """Generate random input data based on tensor details."""
    shape = input_details['shape']
    dtype = input_details['dtype']

    # Generate random data in the appropriate range
    if dtype == np.uint8:
        return np.random.randint(0, 256, size=shape, dtype=np.uint8)
    elif dtype == np.int8:
        return np.random.randint(-128, 128, size=shape, dtype=np.int8)
    elif dtype == np.int16:
        return np.random.randint(-32768, 32768, size=shape, dtype=np.int16)
    elif dtype == np.float32:
        return np.random.randn(*shape).astype(np.float32)
    else:
        raise ValueError(f"Unsupported input dtype: {dtype}")


def load_input_npy(input_npy_path, input_details):
    """Load an input tensor from .npy and validate it against the model input."""
    input_data = np.load(input_npy_path, allow_pickle=False)
    expected_shape = tuple(input_details['shape'])
    expected_dtype = input_details['dtype']

    if tuple(input_data.shape) != expected_shape:
        raise ValueError(
            f"Input NPY shape mismatch: expected {expected_shape}, got {tuple(input_data.shape)}"
        )

    if input_data.dtype != expected_dtype:
        raise ValueError(
            f"Input NPY dtype mismatch: expected {expected_dtype}, got {input_data.dtype}"
        )

    return input_data


def load_output_npy(output_npy_path, output_details):
    """Load an output tensor from .npy and validate it against the model output."""
    output_data = np.load(output_npy_path, allow_pickle=False)
    expected_shape = tuple(output_details['shape'])
    expected_dtype = output_details['dtype']

    if tuple(output_data.shape) != expected_shape:
        raise ValueError(
            f"Output NPY shape mismatch: expected {expected_shape}, got {tuple(output_data.shape)}"
        )

    if output_data.dtype != expected_dtype:
        raise ValueError(
            f"Output NPY dtype mismatch: expected {expected_dtype}, got {output_data.dtype}"
        )

    return output_data


def array_to_c_format(data, name, array_type="uint8_t"):
    """Convert numpy array to C array format."""
    flat_data = data.flatten()

    # Convert data to appropriate C type
    if array_type == "int8_t":
        c_values = [f"{int(val)}" for val in flat_data]
    elif array_type == "int16_t":
        c_values = [f"{int(val)}" for val in flat_data]
    elif array_type == "uint8_t":
        c_values = [f"{int(val) & 0xFF}" for val in flat_data]
    else:
        c_values = [f"{int(val) & 0xFF}" for val in flat_data]

    # Format as C array with 12 values per line for readability
    lines = []
    lines.append(f"const {array_type} {name}[{len(flat_data)}] = {{")

    for i in range(0, len(c_values), 12):
        chunk = c_values[i:i+12]
        line = "    " + ", ".join(chunk)
        if i + 12 < len(c_values):
            line += ","
        lines.append(line)

    lines.append("};")
    return "\n".join(lines)


def get_c_type_for_dtype(dtype):
    """Map numpy dtype to C type."""
    if dtype == np.uint8:
        return "uint8_t"
    elif dtype == np.int8:
        return "int8_t"
    elif dtype == np.int16:
        return "int16_t"
    raise ValueError(f"Unsupported tensor dtype for C generation: {dtype}")


def validate_path_count(label, paths, tensor_details):
    """Require an optional path list to cover every corresponding tensor."""
    if paths and len(paths) != len(tensor_details):
        raise ValueError(
            f"{label} count mismatch: expected {len(tensor_details)}, got {len(paths)}"
        )


def run_tflite_inference(
    tflite_path,
    output_path=None,
    input_npy_paths=None,
    output_npy_paths=None,
    source_output_npy_paths=None,
    expected_output_npy_paths=None,
):
    """Run inference on TFLite model and generate C arrays."""

    input_npy_paths = list(input_npy_paths or [])
    output_npy_paths = list(output_npy_paths or [])
    source_output_npy_paths = list(source_output_npy_paths or [])
    expected_output_npy_paths = list(expected_output_npy_paths or [])

    # Load TFLite model
    interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    interpreter.allocate_tensors()

    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    if not input_details:
        raise ValueError("Model has no input tensors")
    if not output_details:
        raise ValueError("Model has no output tensors")

    validate_path_count("Input NPY", input_npy_paths, input_details)
    validate_path_count("Output NPY", output_npy_paths, output_details)
    validate_path_count("Source output NPY", source_output_npy_paths, output_details)
    validate_path_count("Expected output NPY", expected_output_npy_paths, output_details)

    print(f"\n{'='*60}")
    print(f"Model: {tflite_path.name}")
    print(f"{'='*60}")

    input_data = []
    for index, details in enumerate(input_details):
        print(f"\nInput {index} Details:")
        print(f"  Shape: {details['shape']}")
        print(f"  Type: {details['dtype']}")
        print(f"  Quantization: {details['quantization']}")

        if input_npy_paths:
            data = load_input_npy(input_npy_paths[index], details)
            print(f"  Loaded from NPY: {input_npy_paths[index]}")
        else:
            data = generate_random_input(details)
            print(f"  Generated random input with shape: {data.shape}")
        input_data.append(data)

    for index, details in enumerate(output_details):
        print(f"\nOutput {index} Details:")
        print(f"  Shape: {details['shape']}")
        print(f"  Type: {details['dtype']}")
        print(f"  Quantization: {details['quantization']}")

    # Run inference
    for details, data in zip(input_details, input_data):
        interpreter.set_tensor(details['index'], data)
    interpreter.invoke()

    output_data = [interpreter.get_tensor(details['index']) for details in output_details]

    if expected_output_npy_paths:
        for index, (path, details, data) in enumerate(
            zip(expected_output_npy_paths, output_details, output_data)
        ):
            expected = load_output_npy(path, details)
            if not np.array_equal(data, expected):
                raise ValueError(
                    f"Model output {index} does not match expected output NPY: {path}"
                )
            print(f"Verified output {index} against NPY: {path}")

    if source_output_npy_paths:
        output_data = [
            load_output_npy(path, details)
            for path, details in zip(source_output_npy_paths, output_details)
        ]
        for index, path in enumerate(source_output_npy_paths):
            print(f"Loaded output {index} from NPY: {path}")

    if output_npy_paths:
        for index, (path, data) in enumerate(zip(output_npy_paths, output_data)):
            path.parent.mkdir(parents=True, exist_ok=True)
            np.save(path, data, allow_pickle=False)
            print(f"Saved output tensor {index} to NPY: {path}")

    # Generate C file content
    model_name = tflite_path.stem.replace('-', '_').replace('.', '_')

    input_sections = []
    input_metadata = []
    for index, (details, data) in enumerate(zip(input_details, input_data)):
        suffix = "" if len(input_details) == 1 else f"_{index}"
        array_name = f"{model_name}_input{suffix}"
        input_sections.append(
            f"/* Input tensor {index} data */\n"
            + array_to_c_format(data, array_name, get_c_type_for_dtype(details['dtype']))
        )
        input_metadata.append(
            f"#define {model_name.upper()}_INPUT{suffix.upper()}_SIZE {data.size}"
        )

    output_sections = []
    output_metadata = []
    for index, (details, data) in enumerate(zip(output_details, output_data)):
        suffix = "" if len(output_details) == 1 else f"_{index}"
        array_name = f"{model_name}_output{suffix}"
        output_sections.append(
            f"/* Output tensor {index} data */\n"
            + array_to_c_format(data, array_name, get_c_type_for_dtype(details['dtype']))
        )
        output_metadata.append(
            f"#define {model_name.upper()}_OUTPUT{suffix.upper()}_SIZE {data.size}"
        )

    input_sources = [path.name for path in input_npy_paths] or ["generated-random"]
    if source_output_npy_paths:
        output_sources = [path.name for path in source_output_npy_paths]
    elif expected_output_npy_paths:
        output_sources = [path.name for path in expected_output_npy_paths]
    else:
        output_sources = ["inference-output"]

    c_content = f"""/*
 * Generated C arrays for TFLite model: {tflite_path.name}
 *
 * Input files: {', '.join(input_sources)}
 * Output files: {', '.join(output_sources)}
 */

#ifndef {model_name.upper()}_DATA_H
#define {model_name.upper()}_DATA_H

#include <stdint.h>

{chr(10).join(input_sections)}

{chr(10).join(output_sections)}

/* Metadata */
{chr(10).join(input_metadata)}
{chr(10).join(output_metadata)}

#endif /* {model_name.upper()}_DATA_H */
"""

    # Determine output file path
    if output_path is None:
        output_path = tflite_path.parent / f"{model_name}_data.h"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    with open(output_path, 'w') as f:
        f.write(c_content)

    print(f"\n✓ Generated C header file: {output_path}")
    print(f"  Input arrays: {len(input_data)}")
    print(f"  Output arrays: {len(output_data)}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Execute TFLite model and generate C arrays for input/output'
    )
    parser.add_argument(
        'tflite_file',
        type=str,
        help='Path to TFLite model file'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output C header file path (default: <model_name>_data.h)'
    )
    parser.add_argument(
        '--input-npy',
        type=str,
        action='append',
        default=[],
        help='Optional input tensor .npy file. Repeat in model input order.'
    )
    parser.add_argument(
        '--output-npy',
        type=str,
        action='append',
        default=[],
        help='Optional output tensor .npy file to write. Repeat in model output order.'
    )
    parser.add_argument(
        '--source-output-npy',
        type=str,
        action='append',
        default=[],
        help='Optional output tensor .npy file to use as golden data. Repeat in output order.'
    )
    parser.add_argument(
        '--expected-output-npy',
        type=str,
        action='append',
        default=[],
        help='Optional expected output tensor .npy file. Repeat in model output order.'
    )

    args = parser.parse_args()

    tflite_path = Path(args.tflite_file)

    if not tflite_path.exists():
        print(f"Error: TFLite file not found: {tflite_path}", file=sys.stderr)
        sys.exit(1)

    input_npy_paths = [Path(path) for path in args.input_npy]
    output_npy_paths = [Path(path) for path in args.output_npy]
    source_output_npy_paths = [Path(path) for path in args.source_output_npy]
    expected_output_npy_paths = [Path(path) for path in args.expected_output_npy]

    for label, paths in (
        ("input NPY", input_npy_paths),
        ("source output NPY", source_output_npy_paths),
        ("expected output NPY", expected_output_npy_paths),
    ):
        for path in paths:
            if not path.is_file():
                print(f"Error: {label} file not found: {path}", file=sys.stderr)
                sys.exit(1)

    try:
        run_tflite_inference(
            tflite_path,
            args.output,
            input_npy_paths,
            output_npy_paths,
            source_output_npy_paths,
            expected_output_npy_paths,
        )
    except Exception as e:
        print(f"\nError processing model: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
