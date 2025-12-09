/*
 * Auto-generated from: ic_4_vela.npz
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
#define IC_4_INPUT0_REGION  1
#define IC_4_INPUT0_OFFSET  0
#define IC_4_INPUT0_SIZE    3072

// ---- Outputs ----
#define IC_4_OUTPUT0_REGION 1
#define IC_4_OUTPUT0_OFFSET 0
#define IC_4_OUTPUT0_SIZE   10

// ---- Variables ----

#define IC_4_SCRATCH_REGION 1
#define IC_4_SCRATCH_SIZE   3072
#define IC_4_SCRATCH_FAST_REGION 2
#define IC_4_SCRATCH_FAST_SIZE   57376
