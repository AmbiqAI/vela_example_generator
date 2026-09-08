# Wake-word model input and outputs

- `sample_13_model_input_int8.bin`: 65,792 raw int8 bytes in TFLite row-major order for `[1,257,1,256]`.
- `sample_13_model_output_int8.bin`: 16 raw int8 output bytes for `[1,16,1,1]`.
- `sample_13_model_output_float32.bin`: 16 little-endian float32 dequantized output values.
- `sample_13_model_output.csv`: human-readable output values.
- `manifest.json`: shapes, quantization, padding, and values.

The 0.697-second WAV was right-aligned in the model's 4.112-second input window and padded with leading silence. PCM conversion was `q = round(pcm_int16 / 256)`, clipped to `[-128,127]`.

The stored output was produced by the included NumPy reference executor. A native TFLite runtime may differ by one least-significant bit because optimized kernels can use slightly different fixed-point rounding.
