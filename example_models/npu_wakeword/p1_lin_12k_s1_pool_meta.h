/*
 * Auto-generated from: p1_lin_12k_s1_pool_vela.npz
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
#define P1_LIN_12K_S1_POOL_INPUT0_REGION  1
#define P1_LIN_12K_S1_POOL_INPUT0_OFFSET  131072
#define P1_LIN_12K_S1_POOL_INPUT0_SIZE    65792

// ---- Outputs ----
#define P1_LIN_12K_S1_POOL_OUTPUT0_REGION 1
#define P1_LIN_12K_S1_POOL_OUTPUT0_OFFSET 0
#define P1_LIN_12K_S1_POOL_OUTPUT0_SIZE   16

// ---- Variables ----

#define P1_LIN_12K_S1_POOL_SCRATCH_REGION 1
#define P1_LIN_12K_S1_POOL_SCRATCH_SIZE   196864
#define P1_LIN_12K_S1_POOL_SCRATCH_FAST_REGION 0
#define P1_LIN_12K_S1_POOL_SCRATCH_FAST_SIZE   0
