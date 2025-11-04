/*
 * Auto-generated from: kws_ref_model_aligned_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "foo_weights.h"
#include "foo_meta.h"

__attribute__((aligned(32))) static uint8_t foo_region_1[496] = {0};
__attribute__((aligned(32))) static uint8_t foo_region_2[20752] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return foo_region_1;
    case 2: return foo_region_2;
    case 0: return (uint8_t*)foo_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(foo_region_1);
    case 2: return sizeof(foo_region_2);
    case 0: return foo_weights_size;
    default: return 0;
    }
}
