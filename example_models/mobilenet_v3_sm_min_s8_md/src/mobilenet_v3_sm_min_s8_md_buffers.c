/*
 * Auto-generated from: mobilenet_v3_sm_min_s8_md_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "mobilenet_v3_sm_min_s8_md_weights.h"
#include "mobilenet_v3_sm_min_s8_md_meta.h"

__attribute__((aligned(32))) static uint8_t mobilenet_v3_sm_min_s8_md_region_1[953344] = {0};
__attribute__((aligned(32))) static uint8_t mobilenet_v3_sm_min_s8_md_region_2[253568] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return mobilenet_v3_sm_min_s8_md_region_1;
    case 2: return mobilenet_v3_sm_min_s8_md_region_2;
    case 0: return (uint8_t*)mobilenet_v3_sm_min_s8_md_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(mobilenet_v3_sm_min_s8_md_region_1);
    case 2: return sizeof(mobilenet_v3_sm_min_s8_md_region_2);
    case 0: return mobilenet_v3_sm_min_s8_md_weights_size;
    default: return 0;
    }
}
