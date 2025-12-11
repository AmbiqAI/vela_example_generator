#!/usr/bin/env python3
"""
CIFAR-10 Image to C Array Generator

This script loads a single image from CIFAR-10, transforms it for the ResNet model,
runs inference, and generates C header files containing int8_t arrays for both
input and output tensors, similar to generate_c_arrays.py.
"""

import argparse
import numpy as np
import tensorflow as tf
import sys
from pathlib import Path
import pickle


def load_cifar10_batch(batch_file):
    """Load a CIFAR-10 batch file."""
    with open(batch_file, 'rb') as f:
        batch = pickle.load(f, encoding='bytes')
    
    # CIFAR-10 format: data is uint8, shape is (10000, 3072)
    # 3072 = 32*32*3 (RGB channels)
    data = batch[b'data']
    labels = batch[b'labels']
    
    # Reshape to (10000, 32, 32, 3)
    images = data.reshape(10000, 3, 32, 32).transpose(0, 2, 3, 1)
    
    return images, labels


def download_cifar10():
    """Download CIFAR-10 dataset if not present."""
    cifar10_url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
    data_dir = Path.home() / ".keras" / "datasets" / "cifar-10-batches-py"
    
    if data_dir.exists() and (data_dir / "data_batch_1").exists():
        return data_dir
    
    # Try to use tensorflow to download
    try:
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
        # Save manually if needed
        print("CIFAR-10 dataset loaded via TensorFlow")
        return None  # We'll use the loaded data directly
    except Exception as e:
        print(f"Could not load CIFAR-10 via TensorFlow: {e}")
        print(f"Please download CIFAR-10 manually to: {data_dir}")
        print(f"Or from: {cifar10_url}")
        sys.exit(1)


def load_cifar10_image(image_index=0, use_test_set=False):
    """Load a single CIFAR-10 image."""
    try:
        # Try to load via TensorFlow/Keras
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
        
        if use_test_set:
            images = x_test
            labels = y_test
            dataset_name = "test"
        else:
            images = x_train
            labels = y_train
            dataset_name = "train"
        
        if image_index >= len(images):
            print(f"Warning: image_index {image_index} >= {len(images)}, using index 0")
            image_index = 0
        
        image = images[image_index]
        label = labels[image_index][0]  # Unwrap from array
        
        # CIFAR-10 class names
        class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 
                      'dog', 'frog', 'horse', 'ship', 'truck']
        
        print(f"Loaded image {image_index} from {dataset_name} set")
        print(f"  Label: {label} ({class_names[label]})")
        print(f"  Image shape: {image.shape}")
        print(f"  Image dtype: {image.dtype}")
        print(f"  Image range: [{image.min()}, {image.max()}]")
        
        return image, label, class_names[label]
        
    except Exception as e:
        print(f"Error loading CIFAR-10: {e}")
        print("Trying alternative method with pickle files...")
        
        # Alternative: try to load from pickle files
        data_dir = Path.home() / ".keras" / "datasets" / "cifar-10-batches-py"
        if not data_dir.exists():
            print(f"Error: CIFAR-10 data directory not found: {data_dir}")
            sys.exit(1)
        
        if use_test_set:
            batch_file = data_dir / "test_batch"
        else:
            batch_file = data_dir / "data_batch_1"
        
        if not batch_file.exists():
            print(f"Error: CIFAR-10 batch file not found: {batch_file}")
            sys.exit(1)
        
        images, labels = load_cifar10_batch(batch_file)
        
        if image_index >= len(images):
            print(f"Warning: image_index {image_index} >= {len(images)}, using index 0")
            image_index = 0
        
        image = images[image_index]
        label = labels[image_index]
        
        class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 
                      'dog', 'frog', 'horse', 'ship', 'truck']
        
        print(f"Loaded image {image_index} from {dataset_name} set")
        print(f"  Label: {label} ({class_names[label]})")
        
        return image, label, class_names[label]


def transform_image_for_model(image, input_details):
    """Transform CIFAR-10 image to match model input requirements."""
    # CIFAR-10 images are uint8 [0, 255], shape (32, 32, 3)
    # Model expects int8 with quantization (scale=1.0, zero_point=-128)
    # But we'll return uint8 for the C array generation
    
    # Get quantization parameters
    quant_params = input_details['quantization']
    scale = quant_params[0] if len(quant_params) > 0 else 1.0
    zero_point = quant_params[1] if len(quant_params) > 1 else -128
    
    # Ensure image is in correct shape [1, 32, 32, 3]
    if len(image.shape) == 3:
        image = np.expand_dims(image, axis=0)
    
    # Keep as uint8 [0, 255] for C array generation
    if image.dtype == np.uint8:
        image_uint8 = image.astype(np.uint8)
    else:
        # If float, convert to uint8
        image_float = image.astype(np.float32)
        image_uint8 = np.clip(np.round(image_float), 0, 255).astype(np.uint8)
    
    return image_uint8


def array_to_c_format(data, name, array_type="int8_t"):
    """Convert numpy array to C array format (same as generate_c_arrays.py)."""
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
        return "int8_t"  # Default fallback


def run_cifar10_inference(tflite_path, image_index=0, use_test_set=False, output_path=None):
    """Load CIFAR-10 image, run inference, and generate C arrays."""
    
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
    
    # Load CIFAR-10 image
    print(f"\n{'='*60}")
    print("Loading CIFAR-10 Image")
    print(f"{'='*60}")
    image, label, class_name = load_cifar10_image(image_index, use_test_set)
    
    # Transform image for model (returns uint8 for C array)
    print(f"\n{'='*60}")
    print("Transforming Image")
    print(f"{'='*60}")
    input_data_uint8 = transform_image_for_model(image, input_details)
    print(f"  Transformed shape: {input_data_uint8.shape}")
    print(f"  Transformed dtype: {input_data_uint8.dtype}")
    print(f"  Transformed range: [{input_data_uint8.min()}, {input_data_uint8.max()}]")
    
    # Convert to int8 for model inference (if model expects int8)
    if input_details['dtype'] == np.int8:
        # Convert uint8 [0, 255] to int8 [-128, 127] for model
        quant_params = input_details['quantization']
        zero_point = quant_params[1] if len(quant_params) > 1 else -128
        input_data_for_model = input_data_uint8.astype(np.int32) - 128
        input_data_for_model = np.clip(input_data_for_model, -128, 127).astype(np.int8)
    else:
        input_data_for_model = input_data_uint8
    
    # Run inference
    print(f"\n{'='*60}")
    print("Running Inference")
    print(f"{'='*60}")
    interpreter.set_tensor(input_details['index'], input_data_for_model)
    interpreter.invoke()
    
    # Get output
    output_data = interpreter.get_tensor(output_details['index'])
    print(f"  Output shape: {output_data.shape}")
    print(f"  Output dtype: {output_data.dtype}")
    print(f"  Output range: [{output_data.min()}, {output_data.max()}]")
    
    # Get predicted class
    predicted_class = np.argmax(output_data)
    class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 
                  'dog', 'frog', 'horse', 'ship', 'truck']
    print(f"  Predicted class: {predicted_class} ({class_names[predicted_class]})")
    print(f"  True class: {label} ({class_name})")
    print(f"  Match: {'✓' if predicted_class == label else '✗'}")
    
    # Determine C types - use uint8_t for input array
    input_c_type = "uint8_t"  # Always use uint8_t for CIFAR-10 input
    output_c_type = get_c_type_for_dtype(output_details['dtype'])
    
    # Generate C file content
    model_name = tflite_path.stem.replace('-', '_').replace('.', '_')
    
    c_content = f"""/*
 * Generated C arrays for TFLite model: {tflite_path.name}
 * CIFAR-10 Image Index: {image_index} ({'test' if use_test_set else 'train'} set)
 * True Label: {label} ({class_name})
 * Predicted Label: {predicted_class} ({class_names[predicted_class]})
 *
 * Input shape: {list(input_details['shape'])}
 * Input type: uint8_t (CIFAR-10 format [0, 255])
 * Output shape: {list(output_details['shape'])}
 * Output type: {output_details['dtype']}
 */

#ifndef {model_name.upper()}_DATA_H
#define {model_name.upper()}_DATA_H

#include <stdint.h>

/* Input tensor data (CIFAR-10 image) */
{array_to_c_format(input_data_uint8, f"{model_name}_input", input_c_type)}

/* Output tensor data */
{array_to_c_format(output_data, f"{model_name}_output", output_c_type)}

/* Metadata */
#define {model_name.upper()}_INPUT_SIZE {input_data_uint8.size}
#define {model_name.upper()}_OUTPUT_SIZE {output_data.size}
#define {model_name.upper()}_TRUE_LABEL {label}
#define {model_name.upper()}_PREDICTED_LABEL {predicted_class}

#endif /* {model_name.upper()}_DATA_H */
"""
    
    # Determine output file path
    if output_path is None:
        output_path = tflite_path.parent / f"{model_name}_cifar10_{image_index}_data.h"
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(c_content)
    
    print(f"\n{'='*60}")
    print("Generated Files")
    print(f"{'='*60}")
    print(f"✓ Generated C header file: {output_path}")
    print(f"  Input array: {model_name}_input[{input_data_uint8.size}] (uint8_t)")
    print(f"  Output array: {model_name}_output[{output_data.size}]")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Load CIFAR-10 image, run inference on TFLite model, and generate C arrays'
    )
    parser.add_argument(
        'tflite_file',
        type=str,
        help='Path to TFLite model file'
    )
    parser.add_argument(
        '-i', '--image-index',
        type=int,
        default=0,
        help='Index of CIFAR-10 image to use (default: 0)'
    )
    parser.add_argument(
        '--test-set',
        action='store_true',
        help='Use test set instead of training set'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output C header file path (default: <model_name>_cifar10_<index>_data.h)'
    )
    
    args = parser.parse_args()
    
    tflite_path = Path(args.tflite_file)
    
    if not tflite_path.exists():
        print(f"Error: TFLite file not found: {tflite_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        run_cifar10_inference(
            tflite_path, 
            args.image_index, 
            args.test_set,
            args.output
        )
    except Exception as e:
        print(f"\nError processing model: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

