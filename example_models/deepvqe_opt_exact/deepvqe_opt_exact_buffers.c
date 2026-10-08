/*
 * Auto-generated from: deepvqe_opt_exact_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "deepvqe_opt_exact_weights.h"
#include "deepvqe_opt_exact_meta.h"

__attribute__((aligned(32))) static uint8_t deepvqe_opt_exact_region_1[226688] = {0};
__attribute__((aligned(32))) static uint8_t deepvqe_opt_exact_region_2[95696] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return deepvqe_opt_exact_region_1;
    case 2: return deepvqe_opt_exact_region_2;
    case 0: return (uint8_t*)deepvqe_opt_exact_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(deepvqe_opt_exact_region_1);
    case 2: return sizeof(deepvqe_opt_exact_region_2);
    case 0: return deepvqe_opt_exact_weights_size;
    default: return 0;
    }
}
