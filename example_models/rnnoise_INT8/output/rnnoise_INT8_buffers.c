/*
 * Auto-generated from: rnnoise_INT8_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "rnnoise_INT8_weights.h"
#include "rnnoise_INT8_meta.h"

__attribute__((aligned(32))) static uint8_t rnnoise_INT8_region_1[288] = {0};
__attribute__((aligned(32))) static uint8_t rnnoise_INT8_region_2[704] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return rnnoise_INT8_region_1;
    case 2: return rnnoise_INT8_region_2;
    case 0: return (uint8_t*)rnnoise_INT8_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(rnnoise_INT8_region_1);
    case 2: return sizeof(rnnoise_INT8_region_2);
    case 0: return rnnoise_INT8_weights_size;
    default: return 0;
    }
}
