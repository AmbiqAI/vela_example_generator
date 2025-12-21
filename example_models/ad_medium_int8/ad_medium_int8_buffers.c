/*
 * Auto-generated from: ad_medium_int8_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "ad_medium_int8_weights.h"
#include "ad_medium_int8_meta.h"

__attribute__((aligned(32))) static uint8_t ad_medium_int8_region_1[197632] = {0};
__attribute__((aligned(32))) static uint8_t ad_medium_int8_region_2[239968] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return ad_medium_int8_region_1;
    case 2: return ad_medium_int8_region_2;
    case 0: return (uint8_t*)ad_medium_int8_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(ad_medium_int8_region_1);
    case 2: return sizeof(ad_medium_int8_region_2);
    case 0: return ad_medium_int8_weights_size;
    default: return 0;
    }
}
