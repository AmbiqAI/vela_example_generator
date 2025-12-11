#!/usr/bin/env python3
import argparse
import copy
import os
import subprocess
import sys
from pathlib import Path

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


def run_vela_pipeline_for_slice(
    slice_path: str,
    slice_dir: str,
    pipeline_args: dict,
    script_dir: Path,
) -> bool:
    """Run vela pipeline for a slice."""
    pipeline_script = script_dir / "run_vela_pipeline.py"
    
    if not pipeline_script.exists():
        print(f"Warning: run_vela_pipeline.py not found at {pipeline_script}", file=sys.stderr)
        return False
    
    # Build command
    cmd = [sys.executable, str(pipeline_script), slice_path]
    
    # Add output directory (use slice_dir/output)
    output_subdir = os.path.join(slice_dir, "output")
    cmd.extend(["--output-dir", output_subdir])
    
    # Add vela pipeline arguments
    if pipeline_args.get("accelerator_config"):
        cmd.extend(["--accelerator-config", pipeline_args["accelerator_config"]])
    if pipeline_args.get("vela_config"):
        # Resolve vela_config path relative to script_dir
        vela_config = pipeline_args["vela_config"]
        vela_config_path = Path(vela_config)
        if not vela_config_path.is_absolute():
            vela_config_path = script_dir / vela_config_path
        cmd.extend(["--vela-config", str(vela_config_path)])
    if pipeline_args.get("system_config"):
        cmd.extend(["--system-config", pipeline_args["system_config"]])
    if pipeline_args.get("memory_mode"):
        cmd.extend(["--memory-mode", pipeline_args["memory_mode"]])
    if pipeline_args.get("vela_verbose"):
        cmd.append("--vela-verbose")
    if pipeline_args.get("skip_vela"):
        cmd.append("--skip-vela")
    if pipeline_args.get("skip_raw_to_c"):
        cmd.append("--skip-raw-to-c")
    if pipeline_args.get("skip_c_arrays"):
        cmd.append("--skip-c-arrays")
    if pipeline_args.get("skip_array_to_txt"):
        cmd.append("--skip-array-to-txt")
    
    print(f"\n{'='*60}")
    print(f"Running vela pipeline for slice: {os.path.basename(slice_path)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print(f"✓ Pipeline completed successfully for slice")
            return True
        else:
            print(f"✗ Pipeline failed for slice (exit code: {result.returncode})", file=sys.stderr)
            return False
    except Exception as e:
        print(f"✗ Error running pipeline: {e}", file=sys.stderr)
        return False


def chunk_tflite(
    input_path: str,
    step: int = 5,
    subgraph_index: int = 0,
    output_dir: str = None,
    run_pipeline: bool = False,
    pipeline_args: dict = None,
    script_dir: Path = None,
) -> None:
    """
    Chunk the input TFLite model into multiple models:
    first `step` ops, first `2*step` ops, first `3*step` ops, etc.

    Output files are saved in separate subfolders:
      slice_1/<basename>_1.tflite  (first step ops)
      slice_2/<basename>_2.tflite  (first 2*step ops)
      ...
    
    If run_pipeline is True, runs vela pipeline for each slice:
      slice_1/output/  (pipeline outputs for slice 1)
      slice_2/output/  (pipeline outputs for slice 2)
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

    # Determine output base directory
    if output_dir is None:
        output_base_dir = base_dir
    else:
        output_base_dir = output_dir
        os.makedirs(output_base_dir, exist_ok=True)

    print(f"Total operators in subgraph {subgraph_index}: {num_ops}")

    iteration = 1
    current_ops = step

    while current_ops <= num_ops:
        prefix_model = make_prefix_model(model, current_ops, subgraph_index=subgraph_index)
        
        # Create subfolder for this slice
        slice_dir = os.path.join(output_base_dir, f"slice_{iteration}")
        os.makedirs(slice_dir, exist_ok=True)
        
        out_name = f"{name}_{iteration}{ext}"
        out_path = os.path.join(slice_dir, out_name)

        save_tflite_model(prefix_model, out_path)
        print(f"Saved {out_path}  (first {current_ops} operators)")
        
        # Run vela pipeline for this slice if requested
        if run_pipeline:
            run_vela_pipeline_for_slice(out_path, slice_dir, pipeline_args or {}, script_dir or Path(__file__).parent.parent)

        iteration += 1
        current_ops += step

    # If num_ops is not an exact multiple of step, ensure we have a full model chunk as last file
    if (num_ops % step) != 0 and current_ops - step != num_ops:
        prefix_model = make_prefix_model(model, num_ops, subgraph_index=subgraph_index)
        
        # Create subfolder for this slice
        slice_dir = os.path.join(output_base_dir, f"slice_{iteration}")
        os.makedirs(slice_dir, exist_ok=True)
        
        out_name = f"{name}_{iteration}{ext}"
        out_path = os.path.join(slice_dir, out_name)

        save_tflite_model(prefix_model, out_path)
        print(f"Saved {out_path}  (first {num_ops} operators / full model)")
        
        # Run vela pipeline for this slice if requested
        if run_pipeline:
            run_vela_pipeline_for_slice(out_path, slice_dir, pipeline_args or {}, script_dir or Path(__file__).parent.parent)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Chunk a TFLite model into multiple models containing "
            "prefixes of its operator sequence. Optionally runs vela "
            "pipeline for each slice."
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
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=None,
        help="Output directory for slice subfolders (default: same directory as input model)",
    )
    parser.add_argument(
        "--run-pipeline",
        action="store_true",
        help="Run vela pipeline for each slice after creating it",
    )
    
    # Vela pipeline arguments (passed through)
    parser.add_argument(
        "--accelerator-config",
        type=str,
        default="ethos-u85-256",
        help="Vela accelerator config (default: ethos-u85-256)",
    )
    parser.add_argument(
        "--vela-config",
        type=str,
        default="config/ambiq_final.ini",
        help="Vela config file path (default: config/ambiq_final.ini)",
    )
    parser.add_argument(
        "--system-config",
        type=str,
        default="AmbiqLP_SRAM",
        help="Vela system config (default: AmbiqLP_SRAM)",
    )
    parser.add_argument(
        "--memory-mode",
        type=str,
        default="Sram_Only",
        help="Vela memory mode (default: Sram_Only)",
    )
    parser.add_argument(
        "--vela-verbose",
        action="store_true",
        help="Enable verbose allocation in vela",
    )
    parser.add_argument(
        "--skip-vela",
        action="store_true",
        help="Skip vela step in pipeline (use existing .npz files)",
    )
    parser.add_argument(
        "--skip-raw-to-c",
        action="store_true",
        help="Skip vela_raw_to_c.py step in pipeline",
    )
    parser.add_argument(
        "--skip-c-arrays",
        action="store_true",
        help="Skip generate_c_arrays.py step in pipeline",
    )
    parser.add_argument(
        "--skip-array-to-txt",
        action="store_true",
        help="Skip array_2_txt.py step in pipeline",
    )

    args = parser.parse_args()
    
    # Prepare pipeline arguments
    pipeline_args = {
        "accelerator_config": args.accelerator_config,
        "vela_config": args.vela_config,
        "system_config": args.system_config,
        "memory_mode": args.memory_mode,
        "vela_verbose": args.vela_verbose,
        "skip_vela": args.skip_vela,
        "skip_raw_to_c": args.skip_raw_to_c,
        "skip_c_arrays": args.skip_c_arrays,
        "skip_array_to_txt": args.skip_array_to_txt,
    } if args.run_pipeline else None
    
    script_dir = Path(__file__).parent.parent
    
    chunk_tflite(
        args.model,
        step=args.step,
        subgraph_index=args.subgraph,
        output_dir=args.output_dir,
        run_pipeline=args.run_pipeline,
        pipeline_args=pipeline_args,
        script_dir=script_dir,
    )


if __name__ == "__main__":
    main()
