/*
 * Auto-generated from: u85_mem_ladder_conv1x1_64_64x64_r4_vela.npz
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
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_INPUT0_REGION  1
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_INPUT0_OFFSET  262144
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_INPUT0_SIZE    262144

// ---- Outputs ----
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_OUTPUT0_REGION 1
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_OUTPUT0_OFFSET 0
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_OUTPUT0_SIZE   262144

// ---- Variables ----

#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_SCRATCH_REGION 1
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_SCRATCH_SIZE   524288
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_SCRATCH_FAST_REGION 2
#define U85_MEM_LADDER_CONV1X1_64_64X64_R4_SCRATCH_FAST_SIZE   245760
