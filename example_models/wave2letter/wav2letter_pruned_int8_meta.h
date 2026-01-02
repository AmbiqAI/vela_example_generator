/*
 * Auto-generated from: wav2letter_pruned_int8_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#pragma once
#include <stddef.h>
#include <stdint.h>

// Base-pointer array length for Ethos-U
#define ETHOSU_MAX_REGIONS 8

// ---- Inputs ----
#define WAV2LETTER_PRUNED_INT8_INPUT0_REGION  1
#define WAV2LETTER_PRUNED_INT8_INPUT0_OFFSET  37888
#define WAV2LETTER_PRUNED_INT8_INPUT0_SIZE    11544

// ---- Outputs ----
#define WAV2LETTER_PRUNED_INT8_OUTPUT0_REGION 1
#define WAV2LETTER_PRUNED_INT8_OUTPUT0_OFFSET 0
#define WAV2LETTER_PRUNED_INT8_OUTPUT0_SIZE   4292

// ---- Variables ----

#define WAV2LETTER_PRUNED_INT8_SCRATCH_REGION 1
#define WAV2LETTER_PRUNED_INT8_SCRATCH_SIZE   592000
#define WAV2LETTER_PRUNED_INT8_SCRATCH_FAST_REGION 2
#define WAV2LETTER_PRUNED_INT8_SCRATCH_FAST_SIZE   246784
