/*
 * Auto-generated from: ic_2_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "ic_2_weights.h"
#include "ic_2_meta.h"

__attribute__((aligned(32))) static uint8_t ic_2_region_1[4096] = {0};
__attribute__((aligned(32))) static uint8_t ic_2_region_2[57376] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return ic_2_region_1;
    case 2: return ic_2_region_2;
    case 0: return (uint8_t*)ic_2_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(ic_2_region_1);
    case 2: return sizeof(ic_2_region_2);
    case 0: return ic_2_weights_size;
    default: return 0;
    }
}
