#!/usr/bin/env python3
"""
Convert C Array to Text File

Extracts array values from a C header file and writes them to a text file,
one value per line.
"""

import argparse
import re
import sys
from pathlib import Path


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
    
    # Regex pattern to find the array content inside braces { ... }
    # Handles: const type array_name[size] = { ... };
    pattern = rf"{re.escape(array_name)}\s*\[[^\]]*\]\s*=\s*\{{([^}}]+)\}}"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"Error: Could not find array '{array_name}' in {input_file}", file=sys.stderr)
        return False
    
    # Extract data between braces
    data_str = match.group(1)
    
    # Split on commas, remove whitespace
    raw_values = [x.strip() for x in data_str.split(",") if x.strip()]
    
    numbers = []
    for val in raw_values:
        try:
            # Automatically detect hex (0x..) or decimal
            num = int(val, 0)
            numbers.append(num)
        except ValueError:
            print(f"Warning: Skipping invalid value: {val}", file=sys.stderr)
    
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
    
    print(f"Extracted {len(numbers)} values from '{array_name}' → {output_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Extract array values from C header file and write to text file'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to input C/header file'
    )
    parser.add_argument(
        'array_name',
        type=str,
        help='Name of the array variable to extract'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output text file path (default: <input_file>.txt)'
    )
    
    args = parser.parse_args()
    
    # Determine output file
    if args.output is None:
        input_path = Path(args.input_file)
        output_file = str(input_path.parent / f"{input_path.stem}.txt")
    else:
        output_file = args.output
    
    success = extract_array_to_txt(args.input_file, output_file, args.array_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
