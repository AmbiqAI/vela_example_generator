/*
 * Auto-generated from: mlperf_tiny_vww_vela.npz
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
#define MLPERF_TINY_VWW_INPUT0_REGION  1
#define MLPERF_TINY_VWW_INPUT0_OFFSET  0
#define MLPERF_TINY_VWW_INPUT0_SIZE    27648

// ---- Outputs ----
#define MLPERF_TINY_VWW_OUTPUT0_REGION 1
#define MLPERF_TINY_VWW_OUTPUT0_OFFSET 0
#define MLPERF_TINY_VWW_OUTPUT0_SIZE   2

// ---- Variables ----

#define MLPERF_TINY_VWW_SCRATCH_REGION 1
#define MLPERF_TINY_VWW_SCRATCH_SIZE   27648
#define MLPERF_TINY_VWW_SCRATCH_FAST_REGION 2
#define MLPERF_TINY_VWW_SCRATCH_FAST_SIZE   73728
