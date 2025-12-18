/*
 * Auto-generated from: strm_ww_int8_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "strm_ww_int8_weights.h"
#include "strm_ww_int8_meta.h"

__attribute__((aligned(32))) static uint8_t strm_ww_int8_region_1[1200] = {0};
__attribute__((aligned(32))) static uint8_t strm_ww_int8_region_2[6656] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return strm_ww_int8_region_1;
    case 2: return strm_ww_int8_region_2;
    case 0: return (uint8_t*)strm_ww_int8_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(strm_ww_int8_region_1);
    case 2: return sizeof(strm_ww_int8_region_2);
    case 0: return strm_ww_int8_weights_size;
    default: return 0;
    }
}
