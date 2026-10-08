/*
 * Auto-generated from: u85_port_wr_conv1x1_1to64_96x96_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "u85_port_wr_conv1x1_1to64_96x96_weights.h"
#include "u85_port_wr_conv1x1_1to64_96x96_meta.h"

__attribute__((aligned(32))) static uint8_t u85_port_wr_conv1x1_1to64_96x96_region_1[599040] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return u85_port_wr_conv1x1_1to64_96x96_region_1;
    case 0: return (uint8_t*)u85_port_wr_conv1x1_1to64_96x96_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(u85_port_wr_conv1x1_1to64_96x96_region_1);
    case 0: return u85_port_wr_conv1x1_1to64_96x96_weights_size;
    default: return 0;
    }
}
