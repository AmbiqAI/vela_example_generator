#!/usr/bin/env python3
"""
Vela Pipeline Runner

Runs vela, vela_raw_to_c.py, and generate_c_arrays.py in sequence,
with all outputs stored in the same directory.
"""

import argparse
import subprocess
import sys
from pathlib import Path
import shutil


def run_command(cmd, description, check=True):
    """Run a shell command and print output."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, check=check, capture_output=False)
    
    if result.returncode != 0 and check:
        print(f"\nError: {description} failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(1)
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Run vela pipeline: vela -> vela_raw_to_c.py -> generate_c_arrays.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults
  python run_vela_pipeline.py example_models/ic/ic.tflite

  # Custom output directory
  python run_vela_pipeline.py ic.tflite --output-dir output/ic

  # Custom vela arguments
  python run_vela_pipeline.py ic.tflite \\
      --accelerator-config ethos-u55-128 \\
      --system-config Ethos_U55_High_End_Embedded \\
      --memory-mode Shared_Sram

  # Full customization
  python run_vela_pipeline.py ic.tflite \\
      --output-dir output/ic \\
      --vela-prefix ic \\
      --vela-config config/ambiq.ini \\
      --vela-verbose
        """
    )
    
    # Input file
    parser.add_argument(
        'tflite_file',
        type=str,
        help='Path to input TFLite model file'
    )
    
    # Output directory
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for all generated files (default: <model_dir>/<model_name>_output)'
    )
    
    # Vela arguments
    parser.add_argument(
        '--accelerator-config',
        type=str,
        default='ethos-u85-256',
        help='Vela accelerator config (default: ethos-u85-256)'
    )
    
    parser.add_argument(
        '--vela-config',
        type=str,
        default='config/ambiq_final.ini',
        help='Vela config file path (default: config/ambiq_final.ini)'
    )
    
    parser.add_argument(
        '--system-config',
        type=str,
        default='AmbiqLP_SRAM',
        help='Vela system config (default: AmbiqLP_SRAM)'
    )
    
    parser.add_argument(
        '--memory-mode',
        type=str,
        default='Sram_Only',
        help='Vela memory mode (default: Sram_Only)'
    )
    
    parser.add_argument(
        '--vela-verbose',
        action='store_true',
        help='Enable verbose allocation in vela (adds --verbose-allocation flag)'
    )
    
    parser.add_argument(
        '--vela-prefix',
        type=str,
        default=None,
        help='Prefix for vela_raw_to_c.py output files (default: <model_name>)'
    )
    
    # vela_raw_to_c.py arguments
    parser.add_argument(
        '--raw-to-c-prefix',
        type=str,
        default=None,
        help='Prefix for vela_raw_to_c.py (overrides --vela-prefix if set)'
    )
    
    # generate_c_arrays.py arguments
    parser.add_argument(
        '--c-arrays-output',
        type=str,
        default=None,
        help='Output filename for generate_c_arrays.py (default: <model_name>_data.h)'
    )
    
    # Tool paths
    parser.add_argument(
        '--vela-cmd',
        type=str,
        default='vela',
        help='Vela command (default: vela)'
    )
    
    parser.add_argument(
        '--python-dir',
        type=str,
        default='python',
        help='Directory containing Python scripts (default: python)'
    )
    
    # Options
    parser.add_argument(
        '--skip-vela',
        action='store_true',
        help='Skip vela step (use existing .npz file)'
    )
    
    parser.add_argument(
        '--skip-raw-to-c',
        action='store_true',
        help='Skip vela_raw_to_c.py step'
    )
    
    parser.add_argument(
        '--skip-c-arrays',
        action='store_true',
        help='Skip generate_c_arrays.py step'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean output directory before running'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = Path(__file__).parent.absolute()
    tflite_path = Path(args.tflite_file)
    
    if not tflite_path.is_absolute():
        tflite_path = script_dir / tflite_path
    
    if not tflite_path.exists():
        print(f"Error: TFLite file not found: {tflite_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output directory
    if args.output_dir is None:
        model_name = tflite_path.stem
        output_dir = tflite_path.parent / f"{model_name}_output"
    else:
        output_dir = Path(args.output_dir)
        if not output_dir.is_absolute():
            output_dir = script_dir / output_dir
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.clean and output_dir.exists():
        print(f"Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("Vela Pipeline Configuration")
    print(f"{'='*60}")
    print(f"Input TFLite:  {tflite_path}")
    print(f"Output dir:    {output_dir}")
    print(f"Accelerator:   {args.accelerator_config}")
    print(f"System config: {args.system_config}")
    print(f"Memory mode:   {args.memory_mode}")
    print(f"Vela config:   {args.vela_config}")
    
    # Determine prefix
    model_name = tflite_path.stem
    prefix = args.raw_to_c_prefix or args.vela_prefix or model_name
    
    # Step 1: Run vela
    vela_output_npz = output_dir / f"{model_name}_vela.npz"
    
    if not args.skip_vela:
        vela_config_path = Path(args.vela_config)
        if not vela_config_path.is_absolute():
            vela_config_path = script_dir / vela_config_path
        
        if not vela_config_path.exists():
            print(f"Error: Vela config file not found: {vela_config_path}", file=sys.stderr)
            sys.exit(1)
        
        vela_cmd = [
            args.vela_cmd,
            '--accelerator-config', args.accelerator_config,
            str(tflite_path),
            '--output-format', 'raw',
            '--config', str(vela_config_path),
            '--system-config', args.system_config,
            '--memory-mode', args.memory_mode,
            '--output', str(vela_output_npz)
        ]
        
        if args.vela_verbose:
            vela_cmd.append('--verbose-allocation')
        
        success = run_command(vela_cmd, "Step 1: Running Vela")
        
        if not success:
            print("Error: Vela failed", file=sys.stderr)
            sys.exit(1)
        
        if not vela_output_npz.exists():
            print(f"Error: Vela output file not found: {vela_output_npz}", file=sys.stderr)
            sys.exit(1)
        
        print(f"\n✓ Vela output: {vela_output_npz}")
    else:
        if not vela_output_npz.exists():
            print(f"Error: NPZ file not found (use --skip-vela only if file exists): {vela_output_npz}", file=sys.stderr)
            sys.exit(1)
        print(f"\n⏭ Skipping vela step, using existing: {vela_output_npz}")
    
    # Step 2: Run vela_raw_to_c.py
    if not args.skip_raw_to_c:
        python_dir = Path(args.python_dir)
        if not python_dir.is_absolute():
            python_dir = script_dir / python_dir
        
        vela_raw_to_c_script = python_dir / "vela_raw_to_c.py"
        
        if not vela_raw_to_c_script.exists():
            print(f"Error: vela_raw_to_c.py not found: {vela_raw_to_c_script}", file=sys.stderr)
            sys.exit(1)
        
        raw_to_c_cmd = [
            sys.executable,
            str(vela_raw_to_c_script),
            str(vela_output_npz),
            '--out-dir', str(output_dir),
            '--prefix', prefix
        ]
        
        success = run_command(raw_to_c_cmd, f"Step 2: Running vela_raw_to_c.py (prefix: {prefix})")
        
        if not success:
            print("Error: vela_raw_to_c.py failed", file=sys.stderr)
            sys.exit(1)
        
        print(f"\n✓ vela_raw_to_c.py output in: {output_dir}")
    else:
        print(f"\n⏭ Skipping vela_raw_to_c.py step")
    
    # Step 3: Run generate_c_arrays.py
    if not args.skip_c_arrays:
        python_dir = Path(args.python_dir)
        if not python_dir.is_absolute():
            python_dir = script_dir / python_dir
        
        generate_c_arrays_script = python_dir / "generate_c_arrays.py"
        
        if not generate_c_arrays_script.exists():
            print(f"Error: generate_c_arrays.py not found: {generate_c_arrays_script}", file=sys.stderr)
            sys.exit(1)
        
        if args.c_arrays_output is None:
            c_arrays_output = output_dir / f"{model_name}_data.h"
        else:
            c_arrays_output = Path(args.c_arrays_output)
            if not c_arrays_output.is_absolute():
                c_arrays_output = output_dir / c_arrays_output
        
        generate_cmd = [
            sys.executable,
            str(generate_c_arrays_script),
            str(tflite_path),
            '-o', str(c_arrays_output)
        ]
        
        success = run_command(generate_cmd, f"Step 3: Running generate_c_arrays.py")
        
        if not success:
            print("Error: generate_c_arrays.py failed", file=sys.stderr)
            sys.exit(1)
        
        print(f"\n✓ generate_c_arrays.py output: {c_arrays_output}")
    else:
        print(f"\n⏭ Skipping generate_c_arrays.py step")
    
    # Summary
    print(f"\n{'='*60}")
    print("Pipeline Complete!")
    print(f"{'='*60}")
    print(f"All outputs saved to: {output_dir}")
    print(f"\nGenerated files:")
    
    if not args.skip_raw_to_c:
        print(f"  - {prefix}_cmd_data.h")
        print(f"  - {prefix}_weights.h")
        print(f"  - {prefix}_meta.h")
        print(f"  - {prefix}_buffers.h")
        print(f"  - {prefix}_buffers.c")
        print(f"  - {prefix}_run.c")
    
    if not args.skip_c_arrays:
        c_arrays_file = args.c_arrays_output or f"{model_name}_data.h"
        print(f"  - {c_arrays_file}")
    
    if not args.skip_vela:
        print(f"  - {model_name}_vela.npz")
    
    print()


if __name__ == "__main__":
    main()

