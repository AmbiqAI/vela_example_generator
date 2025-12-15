/*
 * Auto-generated from: resnet_v1_8_32_tfs_int8_17_12_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "resnet_v1_8_32_tfs_int8_17_12_weights.h"
#include "resnet_v1_8_32_tfs_int8_17_12_meta.h"

__attribute__((aligned(32))) static uint8_t resnet_v1_8_32_tfs_int8_17_12_region_1[4096] = {0};
__attribute__((aligned(32))) static uint8_t resnet_v1_8_32_tfs_int8_17_12_region_2[57376] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return resnet_v1_8_32_tfs_int8_17_12_region_1;
    case 2: return resnet_v1_8_32_tfs_int8_17_12_region_2;
    case 0: return (uint8_t*)resnet_v1_8_32_tfs_int8_17_12_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(resnet_v1_8_32_tfs_int8_17_12_region_1);
    case 2: return sizeof(resnet_v1_8_32_tfs_int8_17_12_region_2);
    case 0: return resnet_v1_8_32_tfs_int8_17_12_weights_size;
    default: return 0;
    }
}
