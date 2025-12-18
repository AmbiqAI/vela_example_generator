# Vela Bare-Metal Example Generator
This repo contains:
- a script that converts the raw output provided by Vela into C that directly invokes the Ethos driver
- A proof-of-concept example output for the MLPerf Tiny KWS model
- A snapshot of the ethos driver and a customer toolchain file to compile it for Ambiqsuite-compatible binaries
- A neuralspot-compatible wrapper that gets that compiling

## Limitations
- Only single-command-stream models are supported. Any model that requires CPU fallback will fail to convert.
- Only GCC (arm-none-eabi-gcc, specifically) is supported
- This has not been tested on real hardware. We only know that it compiles.

## Process
1. Compile the model using Vela
2. Convert the resulting raw output file (a serialized numpy file) into C
3. Compile the resulting C as needed (at minimum you need a main() and a pointer to the Ethos register base)

## Pipeline Runner (Recommended)
The `run_vela_pipeline.py` script automates the entire process: running Vela, converting raw output to C, generating reference input/output arrays, and extracting them to text files.

### Basic Usage
```bash
python3 run_vela_pipeline.py example_models/ic/ic.tflite
```

This will generate all files in a default output directory `example_models/ic/ic_output/`.

### Custom Configuration
```bash
python3 run_vela_pipeline.py ic.tflite \
    --output-dir output/ic \
    --accelerator-config ethos-u85-256 \
    --system-config AmbiqLP_SRAM \
    --memory-mode Sram_Only_256KB
```

### Options
- `--output-dir`: Custom output directory for all generated files.
- `--vela-config`: Path to Vela configuration file (default: `config/ambiq_final.ini`).
- `--skip-array-to-txt`: Skip generating the `.txt` files in `src/`.
- `--clean`: Clean the output directory before running.

## Manual Steps
The following sections describe how to run each step of the pipeline manually.

## Compiling your model using Vela
Vela needs to be told about memory and other HW configuration in a *.ini file. See /configs for several examples. Here we'll use bobby.ini:
```bash
pip install ethos-u-vela
vela --accelerator-config ethos-u85-256 mobilenet_v3_sm_min_s8_md.tflite --output-format raw --config ambiq_final.ini --system-config AmbiqLP_SRAM --memory-mode Sram_Only_256KB
```

## Converting model to C
```bash
python3 vela_raw_to_c.py ../output/kws_ref_model_aligned_vela.npz --out-dir . --prefix foo
```
## Run generate_c_arrays.py
Run generate_c_arrays.py to get the reference inputs and outputs as a header file. If -o,--output is not set will generate <model_name>_data.h in the same path as the tflite model.
```bash
python3 python/generate_c_arrays.py ../<path to tflite>/kws_ref_model.tflite
```

## Converting C to txt
The `array_2_txt.py` script automatically extracts arrays from C header files and generates text files:
- `input.txt` (from `*_input` array)
- `golden_output.txt` (from `*_output` array)
- `weights.txt` (from `*_weights` array)
- `cmd_data.txt` (from `*_cmd_data` array)

The script is automatically run as part of the pipeline, but can also be run manually:
```bash
python3 python/array_2_txt.py model_data.h model_cmd_data.h model_weights.h -o src/
```

## Slicing Models
The `slice_tflite.py` script can split a TFLite model into multiple slices (prefixes of the operator sequence) for incremental testing or debugging. Each slice contains the first N operators of the model.

### Basic Usage
```bash
# Slice model into chunks of 5 operators each
python3 python/slice_tflite.py example_models/resnet_v1_8_32_tfs_int8/resnet_v1_8_32_tfs_int8_17.tflite --step 5
```

This creates subfolders `slice_1/`, `slice_2/`, etc., each containing a `.tflite` file with progressively more operators.

### Running Pipeline on Each Slice
To automatically run the full vela pipeline on each slice:
```bash
python3 python/slice_tflite.py example_models/resnet_v1_8_32_tfs_int8/resnet_v1_8_32_tfs_int8_17.tflite --step 5 --run-pipeline
```

This will:
1. Create slices in `slice_1/`, `slice_2/`, etc.
2. Run the full vela pipeline for each slice
3. Generate all outputs (C files, txt files) in `slice_N/output/` for each slice

### Custom Options
```bash
# Custom step size and output directory
python3 python/slice_tflite.py model.tflite --step 10 --output-dir slices/

# With custom vela configuration
python3 python/slice_tflite.py model.tflite --step 5 --run-pipeline \
    --accelerator-config ethos-u55-128 \
    --system-config AmbiqLP \
    --memory-mode Sram_Only_256KB \
    --vela-verbose

# Skip certain pipeline steps
python3 python/slice_tflite.py model.tflite --step 5 --run-pipeline \
    --skip-c-arrays \
    --skip-array-to-txt
```

### Output Structure
With `--run-pipeline`, each slice gets its own output directory:
```
slice_1/
  ├── model_1.tflite
  └── output/
      ├── model_1_vela.npz
      ├── model_1_cmd_data.h
      ├── model_1_weights.h
      ├── model_1_data.h
      └── src/
          ├── input.txt
          ├── golden_output.txt
          ├── weights.txt
          └── cmd_data.txt
slice_2/
  └── ...
```

## Compiling Ethos Driver
The repo contains contains a pre-built ethos static lib ready for linking into a C project, but if you need to modify something, here is how to compile

For neuralSPOT and Ambiqsuite
```bash
$> rm -rf build
$> cmake -B build  -DCMAKE_TOOLCHAIN_FILE=./arm-none-eabi-gcc.cmake  -DTARGET_CPU=cortex-m55  -DETHOSU_TARGET_NPU_CONFIG=ethos-u85-256  -DCMSIS_PATH=../../clean/neuralSPOT/extern/CMSIS/CMSIS_5-5.9.0 && cmake --build build -j
```

For softfp
```bash
$> rm -rf build
$> cmake -B build  -DCMAKE_TOOLCHAIN_FILE=./arm-none-eabi-gcc.cmake  -DTARGET_CPU=cortex-m55+nofp  -DETHOSU_TARGET_NPU_CONFIG=ethos-u85-256  -DCMSIS_PATH=../../clean/neuralSPOT/extern/CMSIS/CMSIS_5-5.9.0 && cmake --build build -j
```

For building inside vela_for_neuralspot example
```bash
$> cd example/vela_for_neuralspot/src/ethos-u-core-driver-nogithub
$> rm -rf build
$> cmake -B build  -DCMAKE_TOOLCHAIN_FILE=./arm-none-eabi-gcc.cmake  -DTARGET_CPU=cortex-m55  -DETHOSU_TARGET_NPU_CONFIG=ethos-u85-256  -DCMSIS_PATH=../../../../../neuralSPOT/extern/CMSIS/CMSIS_5-5.9.0 && cmake --build build -j
```

## Compiling the example
This example is designed to compile in neuralSPOT, but it should be pretty straightforward to compile into bare metal C.
To compile the example:
```bash
$> cp -R example/vela_for_neuralspot ../neuralSPOT/apps/experiments
$> cd ../neuralSPOT
$> make EXAMPLE=experiments/vela_for_neuralspot
