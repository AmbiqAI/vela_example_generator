/*
 * Auto-generated from: ic_1_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "ic_1_weights.h"
#include "ic_1_meta.h"

__attribute__((aligned(32))) static uint8_t ic_1_region_1[8192] = {0};
__attribute__((aligned(32))) static uint8_t ic_1_region_2[57376] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return ic_1_region_1;
    case 2: return ic_1_region_2;
    case 0: return (uint8_t*)ic_1_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(ic_1_region_1);
    case 2: return sizeof(ic_1_region_2);
    case 0: return ic_1_weights_size;
    default: return 0;
    }
}
