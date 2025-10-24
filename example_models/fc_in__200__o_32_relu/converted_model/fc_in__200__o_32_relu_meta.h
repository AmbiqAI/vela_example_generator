/*
 * Auto-generated from: fc_in__200__o_32_relu_vela.npz
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
#define FC_IN__200__O_32_RELU_INPUT0_REGION  1
#define FC_IN__200__O_32_RELU_INPUT0_OFFSET  32
#define FC_IN__200__O_32_RELU_INPUT0_SIZE    200

// ---- Outputs ----
#define FC_IN__200__O_32_RELU_OUTPUT0_REGION 1
#define FC_IN__200__O_32_RELU_OUTPUT0_OFFSET 0
#define FC_IN__200__O_32_RELU_OUTPUT0_SIZE   32

// ---- Variables ----

#define FC_IN__200__O_32_RELU_SCRATCH_REGION 1
#define FC_IN__200__O_32_RELU_SCRATCH_SIZE   240
#define FC_IN__200__O_32_RELU_SCRATCH_FAST_REGION 2
#define FC_IN__200__O_32_RELU_SCRATCH_FAST_SIZE   0
