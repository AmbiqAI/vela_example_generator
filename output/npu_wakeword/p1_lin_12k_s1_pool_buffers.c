/*
 * Auto-generated from: p1_lin_12k_s1_pool_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "p1_lin_12k_s1_pool_weights.h"
#include "p1_lin_12k_s1_pool_meta.h"

__attribute__((aligned(32))) static uint8_t p1_lin_12k_s1_pool_region_1[196864] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return p1_lin_12k_s1_pool_region_1;
    case 0: return (uint8_t*)p1_lin_12k_s1_pool_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(p1_lin_12k_s1_pool_region_1);
    case 0: return p1_lin_12k_s1_pool_weights_size;
    default: return 0;
    }
}
