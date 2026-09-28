# example_models5.2: Vela 5.2.0 builds of kws_micronet_m and resnet_v1_8_32_tfs_int8

Same source tflites as `example_models/<model>/<model>.tflite`, compiled with ethos-u-vela 5.2.0, `--accelerator-config ethos-u85-256`, default optimisation, in four configurations. Each `<variant>_<model>_vela.tflite` carries the command stream and weights as the ethos-u custom op's constant inputs (byte-identical to what `--output-format raw` would emit).

| variant | ini | system config | memory mode |
|---|---|---|---|
| A52 | `config/ambiq_final.ini` | AmbiqLP_SRAM | Dedicated_Sram_256KB |
| B | `example_models5.2/at110_vela.ini` | atomiq110_HP | Shared_Sram |
| C | `example_models5.2/at110_vela.ini` | atomiq110_ULP | Shared_Sram |
| D | `example_models5.2/at110_vela.ini` | atomiq110_HP | Dedicated_Sram_256KB |

`A52` is the same recipe as the Vela 4.5.0 streams in `example_models/` (those reproduce with `Dedicated_Sram`; the cache cap does not change the stream for these models). `at110_vela.ini` is the Atomiq AT110 system model (SSRAM on Axi0, HBLRAM on Axi1, HP = 500 MHz, ULP = 100 MHz).

## Files

| file | cmd stream bytes | cmd sha1 | weights bytes | weights sha1 | Vela est. NPU cycles |
|---|---:|---|---:|---|---:|
| `kws_micronet_m/A52_kws_micronet_m_vela.tflite` | 1,696 | 08850e0b3c0b | 272,544 | 85196e536c43 | 177,117 |
| `resnet_v1_8_32_tfs_int8/A52_resnet_v1_8_32_tfs_int8_vela.tflite` | 5,788 | 6ad18030b3a1 | 103,280 | 4540effdd004 | 85,928 |
| `kws_micronet_m/B_kws_micronet_m_vela.tflite` | 2,160 | 3d6879f4acde | 140,784 | 1b37353211e9 | 186,722 |
| `resnet_v1_8_32_tfs_int8/B_resnet_v1_8_32_tfs_int8_vela.tflite` | 6,140 | 9fff135ec869 | 86,496 | f16ccba43c3d | 90,785 |
| `kws_micronet_m/C_kws_micronet_m_vela.tflite` | 2,196 | 613dc942be40 | 166,672 | a798248afab7 | 181,075 |
| `resnet_v1_8_32_tfs_int8/C_resnet_v1_8_32_tfs_int8_vela.tflite` | 6,140 | 20030f2c05e2 | 92,288 | 6909571e5845 | 87,691 |
| `kws_micronet_m/D_kws_micronet_m_vela.tflite` | 2,152 | 2925dabbc611 | 140,784 | 1b37353211e9 | 186,958 |
| `resnet_v1_8_32_tfs_int8/D_resnet_v1_8_32_tfs_int8_vela.tflite` | 6,132 | 2d22ab4d7cdb | 86,496 | f16ccba43c3d | 91,633 |

## Commands

```
vela --accelerator-config ethos-u85-256 example_models/kws_micronet_m/kws_micronet_m.tflite --config config/ambiq_final.ini --system-config AmbiqLP_SRAM --memory-mode Dedicated_Sram_256KB --output-dir <out>   # A52
vela --accelerator-config ethos-u85-256 example_models/resnet_v1_8_32_tfs_int8/resnet_v1_8_32_tfs_int8.tflite --config config/ambiq_final.ini --system-config AmbiqLP_SRAM --memory-mode Dedicated_Sram_256KB --output-dir <out>   # A52
vela --accelerator-config ethos-u85-256 example_models/kws_micronet_m/kws_micronet_m.tflite --config example_models5.2/at110_vela.ini --system-config atomiq110_HP --memory-mode Shared_Sram --output-dir <out>   # B
vela --accelerator-config ethos-u85-256 example_models/resnet_v1_8_32_tfs_int8/resnet_v1_8_32_tfs_int8.tflite --config example_models5.2/at110_vela.ini --system-config atomiq110_HP --memory-mode Shared_Sram --output-dir <out>   # B
vela --accelerator-config ethos-u85-256 example_models/kws_micronet_m/kws_micronet_m.tflite --config example_models5.2/at110_vela.ini --system-config atomiq110_ULP --memory-mode Shared_Sram --output-dir <out>   # C
vela --accelerator-config ethos-u85-256 example_models/resnet_v1_8_32_tfs_int8/resnet_v1_8_32_tfs_int8.tflite --config example_models5.2/at110_vela.ini --system-config atomiq110_ULP --memory-mode Shared_Sram --output-dir <out>   # C
vela --accelerator-config ethos-u85-256 example_models/kws_micronet_m/kws_micronet_m.tflite --config example_models5.2/at110_vela.ini --system-config atomiq110_HP --memory-mode Dedicated_Sram_256KB --output-dir <out>   # D
vela --accelerator-config ethos-u85-256 example_models/resnet_v1_8_32_tfs_int8/resnet_v1_8_32_tfs_int8.tflite --config example_models5.2/at110_vela.ini --system-config atomiq110_HP --memory-mode Dedicated_Sram_256KB --output-dir <out>   # D
```

## Bare-metal C package (variant D)

`<model>/D_bare_metal/` holds the direct-driver integration package for variant **D** (at110_vela.ini, atomiq110_HP,
Dedicated_Sram_256KB), generated with `run_vela_pipeline.py` and Vela 5.2.0, with the same file names and C symbols as
`example_models/<model>/`: a copy of the tflite it was built from (`D_<model>_vela.tflite`), `<model>_vela.npz` (Vela raw output),
`<model>_cmd_data.h`, `<model>_weights.h`, `<model>_meta.h`, `<model>_buffers.{h,c}`, `<model>_run.c`, `<model>_data.h` (reference
input/output arrays), `<model>_summary_atomiq110_HP.csv` and `src/*.txt` dumps. The npz command stream and weights are byte-identical to
the tflite. Reference inputs are the same as in `example_models/` (kws: the sibling `ifm0.npy`/`ofm0.npy` there; resnet: `ifm0.npy`
rebuilt from the example's `src/*_input.txt`, uint8 1x32x32x3, kept next to the package), and the golden outputs match the 4.5.0
examples value for value.

```
python3 run_vela_pipeline.py example_models/<model>/<model>.tflite --output-dir example_models5.2/<model>/D_bare_metal \
    --vela-config example_models5.2/at110_vela.ini --system-config atomiq110_HP --memory-mode Dedicated_Sram_256KB \
    --use-model-sidecar-npy            # kws;  resnet: --input-npy example_models5.2/resnet_v1_8_32_tfs_int8/D_bare_metal/ifm0.npy
```

Measured on the Atomiq110 FPGA (NPU ulp/hp, AXI stall and per-port beat counters): see the compile-recipe report in the u85-npu-utilization project.
