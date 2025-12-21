/*
 * Auto-generated from: mobilenet_v2_1.0_224_INT8_vela.npz
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
#define MOBILENET_V2_1.0_224_INT8_INPUT0_REGION  1
#define MOBILENET_V2_1.0_224_INT8_INPUT0_OFFSET  100352
#define MOBILENET_V2_1.0_224_INT8_INPUT0_SIZE    150528

// ---- Outputs ----
#define MOBILENET_V2_1.0_224_INT8_OUTPUT0_REGION 1
#define MOBILENET_V2_1.0_224_INT8_OUTPUT0_OFFSET 0
#define MOBILENET_V2_1.0_224_INT8_OUTPUT0_SIZE   1001

// ---- Variables ----

#define MOBILENET_V2_1.0_224_INT8_SCRATCH_REGION 1
#define MOBILENET_V2_1.0_224_INT8_SCRATCH_SIZE   652288
#define MOBILENET_V2_1.0_224_INT8_SCRATCH_FAST_REGION 2
#define MOBILENET_V2_1.0_224_INT8_SCRATCH_FAST_SIZE   250304
