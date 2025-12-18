/*
 * Generated C arrays for TFLite model: rnnoise_INT8.tflite
 *
 * Input shape: [1, 1, 42]
 * Input type: <class 'numpy.int8'>
 * Output shape: [1, 1, 96]
 * Output type: <class 'numpy.int8'>
 */

#ifndef RNNOISE_INT8_DATA_H
#define RNNOISE_INT8_DATA_H

#include <stdint.h>

/* Input tensor data */
const int8_t rnnoise_INT8_input[42] = {
    52, 111, -52, -122, 83, -36, 29, 3, 65, 93, -123, 73,
    -89, 117, -117, 22, 126, -16, -46, -42, 115, -93, 46, 54,
    100, 74, 46, 90, -17, 110, -44, -41, -127, -94, 18, 8,
    -73, -20, -123, -111, 20, 42
};

/* Output tensor data */
const int8_t rnnoise_INT8_output[96] = {
    126, 8, -128, -128, 125, 0, -128, -124, -16, 44, -117, 8,
    126, 0, 0, -1, -128, 126, 26, 7, 0, 0, -1, 126,
    -128, 110, 96, 1, 126, -1, -128, 0, 126, -64, 126, 126,
    126, 0, 126, -1, -16, -21, 24, 6, 0, 0, -128, 121,
    126, 51, 126, -128, -128, -128, -38, 117, 31, 126, 42, 7,
    126, -1, -1, 0, -80, -34, -128, -128, -36, 126, 126, 0,
    125, 126, 126, -128, 0, -1, 126, 126, -81, 10, 126, 126,
    0, -1, 0, -1, -124, 10, 24, 7, -128, 50, -128, 125
};

/* Metadata */
#define RNNOISE_INT8_INPUT_SIZE 42
#define RNNOISE_INT8_OUTPUT_SIZE 96

#endif /* RNNOISE_INT8_DATA_H */
