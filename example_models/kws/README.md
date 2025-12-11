
# Keyword Spotting Example Model

```bash
cd example_models/kws

# Generate Vela as npz
uv run vela ./kws.tflite\
    --accelerator-config ethos-u85-256 \
    --output-format raw \
    --config ../../config/ambiq_debug.ini \
    --system-config Ambiq_Debug_SRAM_Only \
    --output-dir . \
    --memory-mode Sram_Only_256KB_Axi0 \
    --disable-chaining \
    --disable-fwd \
    --disable-cascading \
    --disable-buffering

# Convert Vela npz to C files
python ../../python/vela_raw_to_c.py ./kws_vela.npz --out-dir ./src  --prefix kws_min

# Generate reference input/output C arrays
python ../../python/generate_c_arrays.py ./kws.tflite -o  ./src/kws_data.h

# Convert C arrays to txt files
python ../../python/array_2_txt.py ./src/kws_data.h

```
