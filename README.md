# Vela Bare-Metal Example Generator
This repo contains:

## Limitations
- Only single-command-stream models are supported. Any model that requires CPU fallback will fail to convert.
- Only GCC (arm-none-eabi-gcc, specifically) is supported
- This has not been tested on real hardware. We only know that it compiles.

## Process
1. Compile the model using Vela
2. Convert the resulting raw output file (a serialized numpy file) into C
3. Compile the resulting C as needed (at minimum you need a main() and a pointer to the Ethos register base)

## Compiling your model using Vela
```bash
pip install ethos-u-vela
vela --accelerator-config ethos-u85-256 ../clean/model_perf_tests/models/kws/kws_ref_model_aligned.tflite --output-format raw
```

## Converting model to C
```bash
python vela_raw_to_c.py ../output/kws_ref_model_aligned_vela.npz --out-dir . --prefix foo
```

## Compiling Ethos Driver
The repo contains contains a pre-built ethos static lib ready for linking into a C project, but if you need to modify something, here is how to compile

For neuralSPOT and Ambiqsuite
```bash
$> rm -rf build
$> cmake -B build \\n  -DCMAKE_TOOLCHAIN_FILE=./arm-none-eabi-gcc.cmake \\n  -DTARGET_CPU=cortex-m55 \\n  -DETHOSU_TARGET_NPU_CONFIG=ethos-u85-256 \\n  -DCMSIS_PATH=../../clean/neuralSPOT/extern/CMSIS/CMSIS_5-5.9.0\ncmake --build build -j
```

For softfp
```bash
$> rm -rf build
$> cmake -B build  -DCMAKE_TOOLCHAIN_FILE=./arm-none-eabi-gcc.cmake  -DTARGET_CPU=cortex-m55+nofp  -DETHOSU_TARGET_NPU_CONFIG=ethos-u85-256  -DCMSIS_PATH=../../clean/neuralSPOT/extern/CMSIS/CMSIS_5-5.9.0 && cmake --build build -j
```


## Compiling the example
This example is designed to compile in neuralSPOT, but it should be pretty straightforward to compile into bare metal C.
To compile the example:
```bash
$> cp -R example/vela ../neuralSPOT/apps/experiments
$> cd ../neuralSPOT
$> make EXAMPLE=experiments/vela
