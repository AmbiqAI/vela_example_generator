/*
 * Auto-generated from: fc_in__200__o_4_relu_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "fc_in__200__o_4_relu_weights.h"
#include "fc_in__200__o_4_relu_meta.h"

__attribute__((aligned(32))) static uint8_t fc_in__200__o_4_relu_region_1[224] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return fc_in__200__o_4_relu_region_1;
    case 0: return (uint8_t*)fc_in__200__o_4_relu_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(fc_in__200__o_4_relu_region_1);
    case 0: return fc_in__200__o_4_relu_weights_size;
    default: return 0;
    }
}
