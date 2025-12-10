#!/usr/bin/env python3
import argparse
import copy
import os

import flatbuffers
from tensorflow.lite.python import schema_py_generated as schema_fb

# TFLite flatbuffer file identifier
_FILE_IDENTIFIER = b"TFL3"


def load_tflite_model(path: str) -> schema_fb.ModelT:
    """Load a .tflite file into a mutable ModelT object."""
    with open(path, "rb") as f:
        data = f.read()

    model_fb = schema_fb.Model.GetRootAsModel(data, 0)
    model = schema_fb.ModelT.InitFromObj(model_fb)
    return model


def save_tflite_model(model: schema_fb.ModelT, path: str) -> None:
    """Save a ModelT object back to a .tflite file."""
    builder = flatbuffers.Builder(1024)
    model_offset = model.Pack(builder)
    builder.Finish(model_offset, file_identifier=_FILE_IDENTIFIER)
    buf = builder.Output()

    with open(path, "wb") as f:
        f.write(buf)


def make_prefix_model(
    base_model: schema_fb.ModelT,
    num_ops: int,
    subgraph_index: int = 0,
) -> schema_fb.ModelT:
    """
    Create a new model that contains only the first `num_ops` operators
    of the specified subgraph.

    Outputs are set to the outputs of the last remaining operator.
    """
    model = copy.deepcopy(base_model)

    if subgraph_index >= len(model.subgraphs):
        raise IndexError(
            f"Subgraph index {subgraph_index} out of range "
            f"(model has {len(model.subgraphs)} subgraph(s))"
        )

    sg = model.subgraphs[subgraph_index]

    total_ops = len(sg.operators or [])
    if total_ops == 0:
        raise ValueError("Model subgraph has no operators")

    if num_ops > total_ops:
        num_ops = total_ops

    # Keep only the first `num_ops` operators
    sg.operators = sg.operators[:num_ops]

    # Set outputs = outputs of the last operator in this prefix
    last_op = sg.operators[-1]
    if last_op.outputs is not None and len(last_op.outputs) > 0:
        sg.outputs = list(last_op.outputs)
    else:
        # Fallback: use original inputs as outputs if last op provides none
        sg.outputs = list(sg.inputs)

    return model


def chunk_tflite(
    input_path: str,
    step: int = 5,
    subgraph_index: int = 0,
) -> None:
    """
    Chunk the input TFLite model into multiple models:
    first `step` ops, first `2*step` ops, first `3*step` ops, etc.

    Output files are:
      <basename>_1.tflite  (first step ops)
      <basename>_2.tflite  (first 2*step ops)
      ...
    """
    if step <= 0:
        raise ValueError("step must be > 0")

    model = load_tflite_model(input_path)

    sg = model.subgraphs[subgraph_index]
    num_ops = len(sg.operators or [])
    if num_ops == 0:
        raise ValueError("Model has no operators to chunk")

    base_dir, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = ".tflite"

    print(f"Total operators in subgraph {subgraph_index}: {num_ops}")

    iteration = 1
    current_ops = step

    while current_ops <= num_ops:
        prefix_model = make_prefix_model(model, current_ops, subgraph_index=subgraph_index)
        out_name = f"{name}_{iteration}{ext}"
        out_path = os.path.join(base_dir, out_name)

        save_tflite_model(prefix_model, out_path)
        print(f"Saved {out_path}  (first {current_ops} operators)")

        iteration += 1
        current_ops += step

    # If num_ops is not an exact multiple of step, ensure we have a full model chunk as last file
    if (num_ops % step) != 0 and current_ops - step != num_ops:
        prefix_model = make_prefix_model(model, num_ops, subgraph_index=subgraph_index)
        out_name = f"{name}_{iteration}{ext}"
        out_path = os.path.join(base_dir, out_name)

        save_tflite_model(prefix_model, out_path)
        print(f"Saved {out_path}  (first {num_ops} operators / full model)")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Chunk a TFLite model into multiple models containing "
            "prefixes of its operator sequence."
        )
    )
    parser.add_argument("model", help="Path to the input .tflite model")
    parser.add_argument(
        "--step",
        "-s",
        type=int,
        default=5,
        help="Number of operators per chunk step (default: 5)",
    )
    parser.add_argument(
        "--subgraph",
        type=int,
        default=0,
        help="Subgraph index to use (default: 0)",
    )

    args = parser.parse_args()
    chunk_tflite(args.model, step=args.step, subgraph_index=args.subgraph)


if __name__ == "__main__":
    main()
