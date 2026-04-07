#!/usr/bin/env python3
"""
Vela Matrix Pipeline Runner

Runs run_vela_pipeline.py for every combination of system configuration and
memory mode defined in config/ambiq_final.ini across all primary TFLite models
found in the example_models directory.

Output for each combination is stored under:
  example_models/<model_dir>/<sys_config>_<mem_mode>/

Generated C file prefixes embed the configuration:
  <model_stem>_<sys_config>_<mem_mode>_cmd_data.h  (and companion files)

Usage:
  # Run all models with all config combinations
  python run_matrix.py

  # Restrict to specific models or configs
  python run_matrix.py --models ic fc_in__200__o_32_relu
  python run_matrix.py --sys-configs AmbiqLP_SRAM AmbiqHP_SRAM
  python run_matrix.py --mem-modes Sram_Only Shared_Sram

  # Dry-run (print commands without executing)
  python run_matrix.py --dry-run
"""

import argparse
import configparser
import subprocess
import sys
from pathlib import Path


# Default accelerator config used for all runs
DEFAULT_ACCELERATOR = "ethos-u85-256"

# Map from model directory name to the primary TFLite file stem within it.
# Each model directory may contain multiple .tflite files; this pinpoints the
# canonical one to use for matrix generation.
PRIMARY_MODELS: dict[str, str] = {
    "conlarge_xl":               "conlarge_xl",
    "efficientnet_lite0_s8_lg":  "efficientnet_lite0_s8_lg",
    "fc_in__200__o_32_relu":     "fc_in__200__o_32_relu",
    "ic":                        "ic",
    "mobilenet_v3_sm_min_s8_md": "mobilenet_v3_sm_min_s8_md",
    "resnet_v1_8_32_tfs_int8":   "resnet_v1_8_32_tfs_int8_17",
}


def parse_ini_configs(
    ini_path: Path,
) -> tuple[list[str], list[str], dict[str, str], dict[str, str]]:
    """
    Parse system configs and memory modes from the given .ini file.

    Returns:
        sys_configs   – list of system config names
        mem_modes     – list of memory mode names
        axi1_port_map – {sys_config_name: axi1_port_type}  (e.g. 'Sram' or 'Dram')
        const_area_map– {mem_mode_name: resolved const_mem_area}  (e.g. 'Axi0' or 'Axi1')
    """
    cfg = configparser.ConfigParser()
    cfg.read(ini_path)

    sys_configs: list[str] = []
    mem_modes: list[str] = []
    axi1_port_map: dict[str, str] = {}
    const_area_map: dict[str, str] = {}

    # First pass – collect raw values
    raw_const_area: dict[str, str | None] = {}
    raw_inherit: dict[str, str | None] = {}

    for section in cfg.sections():
        if section.startswith("System_Config."):
            name = section[len("System_Config."):]
            sys_configs.append(name)
            axi1_port_map[name] = cfg[section].get("axi1_port", "Sram")
        elif section.startswith("Memory_Mode."):
            name = section[len("Memory_Mode."):]
            mem_modes.append(name)
            raw_const_area[name] = cfg[section].get("const_mem_area")
            # Handle the `inherit` keyword (e.g. "Memory_Mode.Shared_Sram")
            inherit_val = cfg[section].get("inherit")
            if inherit_val and "." in inherit_val:
                raw_inherit[name] = inherit_val.split(".", 1)[1]
            else:
                raw_inherit[name] = None

    # Second pass – resolve inheritance for const_mem_area
    def resolve_const(name: str, seen: set[str]) -> str:
        if name in seen:
            return "Axi0"  # cycle guard – fall back to safe default
        seen.add(name)
        area = raw_const_area.get(name)
        if area is not None:
            return area
        parent = raw_inherit.get(name)
        if parent:
            return resolve_const(parent, seen)
        return "Axi0"  # default

    for name in mem_modes:
        const_area_map[name] = resolve_const(name, set())

    return sys_configs, mem_modes, axi1_port_map, const_area_map


def is_compatible(
    sys_config: str,
    mem_mode: str,
    axi1_port_map: dict[str, str],
    const_area_map: dict[str, str],
) -> bool:
    """
    Return False if the combination is known to be invalid for Vela.

    Vela rejects configurations where const_mem_area maps to Sram
    (it must be Dram, OnChipFlash, or OffChipFlash).  This happens when
    a memory mode places constants on Axi1 and the system config maps
    Axi1 to Sram.
    """
    axi1_port = axi1_port_map.get(sys_config, "Sram")
    const_area = const_area_map.get(mem_mode, "Axi0")
    if const_area == "Axi1" and axi1_port == "Sram":
        return False
    return True


def discover_models(example_models_dir: Path, primary_map: dict[str, str]) -> list[tuple[Path, str]]:
    """
    Return a list of (tflite_path, model_dir_name) for each entry in primary_map
    whose .tflite file actually exists.
    """
    results: list[tuple[Path, str]] = []
    for dir_name, tflite_stem in primary_map.items():
        tflite_path = example_models_dir / dir_name / f"{tflite_stem}.tflite"
        if tflite_path.exists():
            results.append((tflite_path, dir_name))
        else:
            print(f"[WARN] TFLite not found, skipping: {tflite_path}", file=sys.stderr)
    return results


def run_pipeline(
    *,
    script: Path,
    tflite_path: Path,
    output_dir: Path,
    prefix: str,
    accelerator: str,
    vela_config: Path,
    sys_config: str,
    mem_mode: str,
    dry_run: bool,
) -> bool:
    """
    Invoke run_vela_pipeline.py for a single (model, sys_config, mem_mode) triple.
    Returns True on success, False on failure.
    """
    cmd = [
        sys.executable,
        str(script),
        str(tflite_path),
        "--output-dir", str(output_dir),
        "--vela-prefix", prefix,
        "--accelerator-config", accelerator,
        "--vela-config", str(vela_config),
        "--system-config", sys_config,
        "--memory-mode", mem_mode,
        "--skip-c-arrays",   # tensorflow not required; skips generate_c_arrays.py
    ]

    if dry_run:
        print("  DRY-RUN:", " ".join(cmd))
        return True

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[FAIL] sys={sys_config} mem={mem_mode}", file=sys.stderr)
        print(result.stdout[-2000:] if result.stdout else "", file=sys.stderr)
        print(result.stderr[-2000:] if result.stderr else "", file=sys.stderr)
        return False
    return True


def main() -> None:
    script_dir = Path(__file__).parent.absolute()

    parser = argparse.ArgumentParser(
        description="Run vela pipeline over all sys-config × mem-mode combinations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--ini",
        default=str(script_dir / "config" / "ambiq_final.ini"),
        help="Path to ambiq_final.ini (default: config/ambiq_final.ini)",
    )
    parser.add_argument(
        "--example-models-dir",
        default=str(script_dir / "example_models"),
        help="Path to example_models directory (default: example_models/)",
    )
    parser.add_argument(
        "--accelerator",
        default=DEFAULT_ACCELERATOR,
        help=f"Vela accelerator config (default: {DEFAULT_ACCELERATOR})",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        metavar="MODEL_DIR",
        help="Restrict to these model directory names (default: all primary models)",
    )
    parser.add_argument(
        "--sys-configs",
        nargs="*",
        metavar="SYS_CONFIG",
        help="Restrict to these system configs (default: all from ini)",
    )
    parser.add_argument(
        "--mem-modes",
        nargs="*",
        metavar="MEM_MODE",
        help="Restrict to these memory modes (default: all from ini)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them",
    )

    args = parser.parse_args()

    ini_path = Path(args.ini)
    example_models_dir = Path(args.example_models_dir)
    pipeline_script = script_dir / "run_vela_pipeline.py"
    vela_config = ini_path

    if not ini_path.exists():
        print(f"Error: ini file not found: {ini_path}", file=sys.stderr)
        sys.exit(1)
    if not pipeline_script.exists():
        print(f"Error: run_vela_pipeline.py not found: {pipeline_script}", file=sys.stderr)
        sys.exit(1)

    # Parse configs from ini
    all_sys_configs, all_mem_modes, axi1_port_map, const_area_map = parse_ini_configs(ini_path)

    sys_configs = args.sys_configs if args.sys_configs else all_sys_configs
    mem_modes   = args.mem_modes   if args.mem_modes   else all_mem_modes

    # Validate requested configs exist in ini
    unknown_sys = set(sys_configs) - set(all_sys_configs)
    unknown_mem = set(mem_modes)   - set(all_mem_modes)
    if unknown_sys:
        print(f"Error: Unknown system configs: {sorted(unknown_sys)}", file=sys.stderr)
        sys.exit(1)
    if unknown_mem:
        print(f"Error: Unknown memory modes: {sorted(unknown_mem)}", file=sys.stderr)
        sys.exit(1)

    # Determine which model dirs to process
    primary_map = (
        {k: v for k, v in PRIMARY_MODELS.items() if k in args.models}
        if args.models
        else PRIMARY_MODELS
    )
    if not primary_map:
        print("Error: No matching models found.", file=sys.stderr)
        sys.exit(1)

    models = discover_models(example_models_dir, primary_map)
    if not models:
        print("Error: No TFLite files found.", file=sys.stderr)
        sys.exit(1)

    total   = len(models) * len(sys_configs) * len(mem_modes)
    success = 0
    failure = 0
    skipped = 0

    print(f"\nMatrix run: {len(models)} model(s) × {len(sys_configs)} sys_config(s)"
          f" × {len(mem_modes)} mem_mode(s) = {total} total runs")
    print(f"System configs : {sys_configs}")
    print(f"Memory modes   : {mem_modes}")
    print(f"Models         : {[m[1] for m in models]}")
    print()

    run_num = 0
    for tflite_path, model_dir_name in models:
        model_stem = tflite_path.stem
        for sc in sys_configs:
            for mm in mem_modes:
                run_num += 1
                combo    = f"{sc}_{mm}"
                prefix   = f"{model_stem}_{combo}"
                out_dir  = example_models_dir / model_dir_name / combo

                # Skip incompatible sys_config + mem_mode combinations
                if not is_compatible(sc, mm, axi1_port_map, const_area_map):
                    print(f"[{run_num:3d}/{total}] {model_dir_name}  sys={sc}  mem={mm}  → SKIP (incompatible)")
                    skipped += 1
                    continue

                print(f"[{run_num:3d}/{total}] {model_dir_name}  sys={sc}  mem={mm}")

                ok = run_pipeline(
                    script       = pipeline_script,
                    tflite_path  = tflite_path,
                    output_dir   = out_dir,
                    prefix       = prefix,
                    accelerator  = args.accelerator,
                    vela_config  = vela_config,
                    sys_config   = sc,
                    mem_mode     = mm,
                    dry_run      = args.dry_run,
                )

                if ok:
                    success += 1
                else:
                    failure += 1

    print(f"\n{'='*60}")
    print(f"Matrix run complete: {success} succeeded, {failure} failed"
          + (f", {skipped} skipped" if skipped else ""))
    print(f"{'='*60}\n")

    if failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
