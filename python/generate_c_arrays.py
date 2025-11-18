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
    else:
        return "uint8_t"  # Default fallback


def run_tflite_inference(tflite_path, output_path=None):
    """Run inference on TFLite model and generate C arrays."""

    # Load TFLite model
    interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    interpreter.allocate_tensors()

    # Get input and output details
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    print(f"\n{'='*60}")
    print(f"Model: {tflite_path.name}")
    print(f"{'='*60}")
    print(f"\nInput Details:")
    print(f"  Shape: {input_details['shape']}")
    print(f"  Type: {input_details['dtype']}")
    print(f"  Quantization: {input_details['quantization']}")

    print(f"\nOutput Details:")
    print(f"  Shape: {output_details['shape']}")
    print(f"  Type: {output_details['dtype']}")
    print(f"  Quantization: {output_details['quantization']}")

    # Generate random input
    input_data = generate_random_input(input_details)
    print(f"\nGenerated random input with shape: {input_data.shape}")

    # Run inference
    interpreter.set_tensor(input_details['index'], input_data)
    interpreter.invoke()

    # Get output
    output_data = interpreter.get_tensor(output_details['index'])
    print(f"Output shape: {output_data.shape}")

    # Determine C types
    input_c_type = get_c_type_for_dtype(input_details['dtype'])
    output_c_type = get_c_type_for_dtype(output_details['dtype'])

    # Generate C file content
    model_name = tflite_path.stem.replace('-', '_').replace('.', '_')

    c_content = f"""/*
 * Generated C arrays for TFLite model: {tflite_path.name}
 *
 * Input shape: {list(input_details['shape'])}
 * Input type: {input_details['dtype']}
 * Output shape: {list(output_details['shape'])}
 * Output type: {output_details['dtype']}
 */

#ifndef {model_name.upper()}_DATA_H
#define {model_name.upper()}_DATA_H

#include <stdint.h>

/* Input tensor data */
{array_to_c_format(input_data, f"{model_name}_input", input_c_type)}

/* Output tensor data */
{array_to_c_format(output_data, f"{model_name}_output", output_c_type)}

/* Metadata */
#define {model_name.upper()}_INPUT_SIZE {input_data.size}
#define {model_name.upper()}_OUTPUT_SIZE {output_data.size}

#endif /* {model_name.upper()}_DATA_H */
"""

    # Determine output file path
    if output_path is None:
        output_path = tflite_path.parent / f"{model_name}_data.h"

    # Write to file
    with open(output_path, 'w') as f:
        f.write(c_content)

    print(f"\n✓ Generated C header file: {output_path}")
    print(f"  Input array: {model_name}_input[{input_data.size}]")
    print(f"  Output array: {model_name}_output[{output_data.size}]")

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

    args = parser.parse_args()

    tflite_path = Path(args.tflite_file)

    if not tflite_path.exists():
        print(f"Error: TFLite file not found: {tflite_path}", file=sys.stderr)
        sys.exit(1)

    try:
        run_tflite_inference(tflite_path, args.output)
    except Exception as e:
        print(f"\nError processing model: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
