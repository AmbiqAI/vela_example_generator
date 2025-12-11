
# Keyword Spotting Example Model

```bash
uv run vela ./example_models/kws/kws.tflite\
    --accelerator-config ethos-u85-256 \
    --output-format raw \
    --config /Users/adampage/Ambiq/research/vela_example_generator/config/ambiq_debug.ini \
    --system-config Ambiq_Debug_SRAM_Only \
    --output-dir ./example_models/kws \
    --memory-mode Sram_Only_256KB_Axi0 \
    --disable-chaining \
    --disable-fwd \
    --disable-cascading \
    --disable-buffering
```

    # --config ./config/ambiq_debug.ini \

```bash
uv run python ./python/vela_raw_to_c.py ./example_models/kws/kws_vela.npz --out-dir ./example_models/kws/src  --prefix kws_min
```

```bash
uv run python ./python/generate_c_arrays.py ./example_models/kws/kws.tflite -o  ./example_models/kws/src/kws_data.h
```

```bash
uv run python ./python/array_2_txt.py ./example_models/kws/src/kws_data.h kws_input -o ./example_models/kws/src/kws_input.txt
```

```bash
uv run python ./python/array_2_txt.py ./example_models/kws/src/kws_data.h kws_output -o ./example_models/kws/src/kws_output.txt
```
