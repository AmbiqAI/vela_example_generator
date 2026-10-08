/*
 * Auto-generated from: u85_mem_fm_add_96x96x32_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "u85_mem_fm_add_96x96x32_weights.h"
#include "u85_mem_fm_add_96x96x32_meta.h"

__attribute__((aligned(32))) static uint8_t u85_mem_fm_add_96x96x32_region_1[884736] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return u85_mem_fm_add_96x96x32_region_1;
    case 0: return (uint8_t*)u85_mem_fm_add_96x96x32_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(u85_mem_fm_add_96x96x32_region_1);
    case 0: return u85_mem_fm_add_96x96x32_weights_size;
    default: return 0;
    }
}
