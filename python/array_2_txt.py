#!/usr/bin/env python3
"""
Convert C Array to Text File

Extracts array values from C header files and writes them to text files,
one value per line. Can extract multiple arrays and generate:
- input.txt (from *_input array)
- golden_output.txt (from *_output array)
- weights.txt (from *_weights array)
- cmd_data.txt (from *_cmd_data array)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def extract_array_from_content(content: str, array_name: str) -> Optional[List[int]]:
    """Extract array values from C file content."""
    # Regex pattern to find the array content inside braces { ... }
    # Handles: const type array_name[size] = { ... };
    # Also handles: static const type array_name[size] = { ... };
    pattern = rf"(?:static\s+)?const\s+\w+\s+{re.escape(array_name)}\s*\[[^\]]*\]\s*=\s*\{{([^}}]+)\}}"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    # Extract data between braces
    data_str = match.group(1)
    
    # Handle multi-line arrays with hex values (0xAB format)
    # Remove line breaks and split on commas
    data_str = re.sub(r'\s+', ' ', data_str)  # Normalize whitespace
    
    # Split on commas, remove whitespace
    raw_values = [x.strip() for x in data_str.split(",") if x.strip()]
    
    numbers = []
    for val in raw_values:
        try:
            # Automatically detect hex (0x..) or decimal
            # int(val, 0) handles both decimal and hex (0x prefix)
            num = int(val, 0)
            numbers.append(num)
        except ValueError:
            print(f"Warning: Skipping invalid value: {val}", file=sys.stderr)
    
    return numbers


def find_arrays_in_file(file_path: Path) -> Dict[str, List[int]]:
    """Find all extractable arrays in a C header file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return {}
    
    arrays = {}
    
    # Find all array declarations
    # Pattern: (static)? const type name[size] = { ... };
    array_pattern = r"(?:static\s+)?const\s+\w+\s+(\w+)\s*\[[^\]]*\]\s*=\s*\{"
    matches = re.finditer(array_pattern, content, re.MULTILINE)
    
    for match in matches:
        array_name = match.group(1)
        numbers = extract_array_from_content(content, array_name)
        if numbers is not None:
            arrays[array_name] = numbers
    
    return arrays


def get_output_filename(array_name: str, prefix: Optional[str] = None) -> Optional[str]:
    """Map array name to output filename with optional prefix."""
    # Map array name patterns to output filenames
    name = None
    if array_name.endswith("_input"):
        name = "input.txt"
    elif array_name.endswith("_output"):
        name = "golden_output.txt"
    elif array_name.endswith("_weights"):
        name = "weights.txt"
    elif array_name.endswith("_cmd_data"):
        name = "cmd_data.txt"
    
    if name and prefix:
        return f"{prefix}_{name}"
    return name


def extract_array_to_txt(input_file, output_file, array_name):
    """Extract array values from C file and write to text file."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        return False
    
    # Read the file
    try:
        with open(input_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        return False
    
    numbers = extract_array_from_content(content, array_name)
    
    if numbers is None:
        print(f"Error: Could not find array '{array_name}' in {input_file}", file=sys.stderr)
        return False
    
    # Write numbers to text file (one per line)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, "w") as f:
            for n in numbers:
                f.write(f"{n}\n")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        return False
    
    print(f"Extracted {len(numbers)} values from '{array_name}' → {output_path}")
    return True


def extract_all_arrays(input_files: List[Path], output_dir: Path, prefix: Optional[str] = None) -> bool:
    """Extract all relevant arrays from input files and generate txt files."""
    all_arrays = {}
    
    # Collect arrays from all input files
    for input_file in input_files:
        if not input_file.exists():
            print(f"Warning: Input file not found: {input_file}", file=sys.stderr)
            continue
        
        arrays = find_arrays_in_file(input_file)
        all_arrays.update(arrays)
    
    if not all_arrays:
        print("Error: No arrays found in input files", file=sys.stderr)
        return False
    
    # Generate output files
    output_dir.mkdir(parents=True, exist_ok=True)
    success_count = 0
    
    for array_name, numbers in all_arrays.items():
        output_filename = get_output_filename(array_name, prefix)
        if output_filename is None:
            # Skip arrays that don't match our patterns
            continue
        
        output_path = output_dir / output_filename
        
        try:
            with open(output_path, "w") as f:
                for n in numbers:
                    f.write(f"{n}\n")
            print(f"Extracted {len(numbers)} values from '{array_name}' → {output_path}")
            success_count += 1
        except Exception as e:
            print(f"Error writing {output_path}: {e}", file=sys.stderr)
    
    if success_count == 0:
        print("Warning: No matching arrays found (looking for *_input, *_output, *_weights, *_cmd_data)", file=sys.stderr)
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Extract array values from C header files and write to text files. '
                    'Automatically generates input.txt, golden_output.txt, weights.txt, and cmd_data.txt'
    )
    parser.add_argument(
        'input_files',
        type=str,
        nargs='+',
        help='Path(s) to input C/header file(s) (e.g., *_data.h, *_cmd_data.h, *_weights.h)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default=None,
        help='Output directory for txt files (default: same as first input file directory)'
    )
    parser.add_argument(
        '--prefix',
        type=str,
        default=None,
        help='Prefix for output txt filenames (e.g., "kws" -> kws_input.txt)'
    )
    parser.add_argument(
        '--array-name',
        type=str,
        default=None,
        help='Extract specific array name (legacy mode: single array extraction)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (legacy mode: only used with --array-name)'
    )
    
    args = parser.parse_args()
    
    input_paths = [Path(f) for f in args.input_files]
    
    # Legacy mode: single array extraction
    if args.array_name:
        if len(input_paths) != 1:
            print("Error: --array-name requires exactly one input file", file=sys.stderr)
            sys.exit(1)
        
        if args.output is None:
            input_path = input_paths[0]
            prefix = args.prefix + "_" if args.prefix else ""
            output_file = str(input_path.parent / f"{prefix}{input_path.stem}.txt")
        else:
            output_file = args.output
        
        success = extract_array_to_txt(str(input_paths[0]), output_file, args.array_name)
        sys.exit(0 if success else 1)
    
    # New mode: extract all arrays
    if args.output_dir is None:
        output_dir = input_paths[0].parent
    else:
        output_dir = Path(args.output_dir)
    
    success = extract_all_arrays(input_paths, output_dir, args.prefix)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
