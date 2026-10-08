/*
 * Auto-generated from: mlperf_tiny_vww_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "mlperf_tiny_vww_weights.h"
#include "mlperf_tiny_vww_meta.h"

__attribute__((aligned(32))) static uint8_t mlperf_tiny_vww_region_1[27648] = {0};
__attribute__((aligned(32))) static uint8_t mlperf_tiny_vww_region_2[73728] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return mlperf_tiny_vww_region_1;
    case 2: return mlperf_tiny_vww_region_2;
    case 0: return (uint8_t*)mlperf_tiny_vww_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(mlperf_tiny_vww_region_1);
    case 2: return sizeof(mlperf_tiny_vww_region_2);
    case 0: return mlperf_tiny_vww_weights_size;
    default: return 0;
    }
}
