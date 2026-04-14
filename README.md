# Vela Bare-Metal Example Generator

This repository converts Arm Ethos-U Vela raw output into a small bare-metal C integration package:

- Vela `raw` output (`*_vela.npz`)
- generated driver-facing C headers and sources
- generated reference input/output arrays from the original `.tflite`
- optional `.txt` exports for test harnesses

It also includes example generated outputs, Ethos-U driver snapshots, and NeuralSPOT-oriented integration examples.

## What This Repo Produces

Given a `.tflite` model, the pipeline can generate:

- `*_vela.npz`: Vela raw output
- `*_cmd_data.h`: command stream payload for the driver
- `*_weights.h`: model weights blob
- `*_meta.h`: tensor region and size metadata
- `*_buffers.h` and `*_buffers.c`: scratch and tensor region allocations
- `*_run.c`: minimal direct-driver invocation example
- `*_data.h`: reference input/output arrays from TFLite inference
- `src/*_input.txt`, `src/*_golden_output.txt`, `src/*_weights.txt`, `src/*_cmd_data.txt`: one-value-per-line text dumps

## Limitations

- Only single-command-stream models are supported.
- Models that require CPU fallback are not supported by `python/vela_raw_to_c.py`.
- The helper inference script currently assumes a single input tensor and a single output tensor.
- The generated code is intended for direct Ethos-U driver integration, not TFLM.
- GCC-based embedded builds are the documented path in this repository.
- The examples here are compile-oriented; hardware validation is not documented in this repo.

## Requirements

- Python 3.11+
- Arm Vela CLI available as `vela`
- TensorFlow and NumPy for reference array generation

The repo already declares Python dependencies in [`pyproject.toml`](/Users/mohammed.abuhussein/workspace/vela_example_generator/pyproject.toml). A typical setup is:

```bash
uv sync
```

If you are not using `uv`, install the equivalent packages manually.

## Recommended Flow

The main entrypoint is [`run_vela_pipeline.py`](/Users/mohammed.abuhussein/workspace/vela_example_generator/run_vela_pipeline.py). It runs:

1. Vela with `--output-format raw`
2. `python/vela_raw_to_c.py`
3. `python/generate_c_arrays.py`
4. `python/array_2_txt.py`

### Basic Usage

```bash
python3 run_vela_pipeline.py example_models/kws_ref_model/kws_ref_model.tflite
```

By default this writes output to:

```text
example_models/kws_ref_model/kws_ref_model_output/
```

### Common Customization

```bash
python3 run_vela_pipeline.py example_models/kws_ref_model/kws_ref_model.tflite \
    --output-dir output/kws \
    --accelerator-config ethos-u85-256 \
    --vela-config config/ambiq_final.ini \
    --system-config AmbiqLP_SRAM \
    --memory-mode Sram_Only_256KB
```

### Useful Options

- `--output-dir`: output directory for generated artifacts
- `--vela-config`: Vela `.ini` file
- `--accelerator-config`: NPU target, for example `ethos-u85-256`
- `--system-config`: Vela system config name from the `.ini`
- `--memory-mode`: Vela memory mode name from the `.ini`
- `--vela-prefix`: prefix for generated direct-driver C files
- `--raw-to-c-prefix`: explicit override for the raw-to-C prefix
- `--c-arrays-output`: custom path for the generated `*_data.h`
- `--skip-vela`: reuse an existing `*_vela.npz`
- `--skip-raw-to-c`: skip direct-driver C generation
- `--skip-c-arrays`: skip reference input/output generation
- `--skip-array-to-txt`: skip `.txt` exports
- `--clean`: remove the output directory before running

## Manual Steps

### 1. Run Vela

Example:

```bash
vela \
    --accelerator-config ethos-u85-256 \
    example_models/mobilenet_v2_1.0_224_INT8/mobilenet_v2_1.0_224_INT8.tflite \
    --output-format raw \
    --config config/ambiq_final.ini \
    --system-config AmbiqLP_SRAM \
    --memory-mode Sram_Only_256KB \
    --output-dir output/mobilenet
```

This produces a `*_vela.npz` file in the selected output directory.

### 2. Convert Vela Raw Output to C

[`python/vela_raw_to_c.py`](/Users/mohammed.abuhussein/workspace/vela_example_generator/python/vela_raw_to_c.py) turns the Vela `.npz` into direct-driver integration code:

```bash
python3 python/vela_raw_to_c.py \
    output/mobilenet/mobilenet_v2_1.0_224_INT8_vela.npz \
    --out-dir output/mobilenet \
    --prefix mobilenet_v2_1_0_224_INT8
```

### 3. Generate Reference Input and Output Arrays

[`python/generate_c_arrays.py`](/Users/mohammed.abuhussein/workspace/vela_example_generator/python/generate_c_arrays.py) runs the original TFLite model with generated random input and emits a header containing:

- `<model>_input`
- `<model>_output`

Example:

```bash
python3 python/generate_c_arrays.py \
    example_models/mobilenet_v2_1.0_224_INT8/mobilenet_v2_1.0_224_INT8.tflite \
    -o output/mobilenet/mobilenet_v2_1.0_224_INT8_data.h
```

### 4. Convert Generated Arrays to Text

[`python/array_2_txt.py`](/Users/mohammed.abuhussein/workspace/vela_example_generator/python/array_2_txt.py) extracts relevant arrays from generated headers and writes text files suitable for external harnesses.

Example:

```bash
python3 python/array_2_txt.py \
    output/mobilenet/mobilenet_v2_1.0_224_INT8_data.h \
    output/mobilenet/mobilenet_v2_1.0_224_INT8_cmd_data.h \
    output/mobilenet/mobilenet_v2_1.0_224_INT8_weights.h \
    -o output/mobilenet/src \
    --prefix mobilenet_v2_1_0_224_INT8
```

This generates:

- `mobilenet_v2_1_0_224_INT8_input.txt`
- `mobilenet_v2_1_0_224_INT8_golden_output.txt`
- `mobilenet_v2_1_0_224_INT8_weights.txt`
- `mobilenet_v2_1_0_224_INT8_cmd_data.txt`

## Slicing Models

[`python/slice_tflite.py`](/Users/mohammed.abuhussein/workspace/vela_example_generator/python/slice_tflite.py) creates prefix slices of a TFLite model by operator count. This is useful for bring-up and debugging.

### Create Slices Only

```bash
python3 python/slice_tflite.py \
    example_models/resnet_v1_8_32_tfs_int8/resnet_v1_8_32_tfs_int8.tflite \
    --step 5
```

This creates:

```text
slice_1/<model>_1.tflite
slice_2/<model>_2.tflite
...
```

### Create Slices and Run the Full Pipeline

```bash
python3 python/slice_tflite.py \
    example_models/resnet_v1_8_32_tfs_int8/resnet_v1_8_32_tfs_int8.tflite \
    --step 5 \
    --run-pipeline
```

Each slice gets its own `output/` directory under the slice folder.

## Configuration Files

The `config/` directory contains sample Vela configuration files, including:

- [`config/ambiq.ini`](/Users/mohammed.abuhussein/workspace/vela_example_generator/config/ambiq.ini)
- [`config/ambiq_debug.ini`](/Users/mohammed.abuhussein/workspace/vela_example_generator/config/ambiq_debug.ini)
- [`config/ambiq_final.ini`](/Users/mohammed.abuhussein/workspace/vela_example_generator/config/ambiq_final.ini)
- [`config/vela.ini`](/Users/mohammed.abuhussein/workspace/vela_example_generator/config/vela.ini)

Use the file and the matching `--system-config` and `--memory-mode` names that correspond to your target.

## Driver and Integration Examples

This repository also contains:

- Ethos-U driver snapshots under [`ethos-u-core-driver-real`](/Users/mohammed.abuhussein/workspace/vela_example_generator/ethos-u-core-driver-real) and [`bobby_ethos-u-core-driver-real`](/Users/mohammed.abuhussein/workspace/vela_example_generator/bobby_ethos-u-core-driver-real)
- example integration projects under [`example/vela`](/Users/mohammed.abuhussein/workspace/vela_example_generator/example/vela) and [`example/vela_for_neuralspot`](/Users/mohammed.abuhussein/workspace/vela_example_generator/example/vela_for_neuralspot)

Those directories are useful as reference integration points; the Python pipeline itself does not depend on building them.

## Repository Layout

```text
config/                  Vela configuration files
example/                 integration examples
example_models/          input models and sample generated outputs
performance/             performance notes/data
python/                  helper scripts
run_vela_pipeline.py     end-to-end pipeline runner
```
