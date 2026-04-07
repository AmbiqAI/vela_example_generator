/*
 * Auto-generated from: conlarge_xl_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stddef.h>
#include <stdint.h>
#include "conlarge_xl_AmbiqLP_PSRAM_Shared_Sram_256KB_weights.h"
#include "conlarge_xl_AmbiqLP_PSRAM_Shared_Sram_256KB_meta.h"

__attribute__((aligned(32))) static uint8_t conlarge_xl_AmbiqLP_PSRAM_Shared_Sram_256KB_region_1[2640000] = {0};

uint8_t* get_region_base_ptr(int region) {
    switch(region) {
    case 1: return conlarge_xl_AmbiqLP_PSRAM_Shared_Sram_256KB_region_1;
    case 0: return (uint8_t*)conlarge_xl_AmbiqLP_PSRAM_Shared_Sram_256KB_weights; // weights region
    default: return (uint8_t*)0; // unused region
    }
}

size_t get_region_size(int region) {
    switch(region) {
    case 1: return sizeof(conlarge_xl_AmbiqLP_PSRAM_Shared_Sram_256KB_region_1);
    case 0: return conlarge_xl_AmbiqLP_PSRAM_Shared_Sram_256KB_weights_size;
    default: return 0;
    }
}
