/*
 * Auto-generated from: mobilenet_v3_sm_min_s8_md_vela.npz
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
#define MOBILENET_V3_SM_MIN_S8_MD_INPUT0_REGION  1
#define MOBILENET_V3_SM_MIN_S8_MD_INPUT0_OFFSET  802816
#define MOBILENET_V3_SM_MIN_S8_MD_INPUT0_SIZE    150528

// ---- Outputs ----
#define MOBILENET_V3_SM_MIN_S8_MD_OUTPUT0_REGION 1
#define MOBILENET_V3_SM_MIN_S8_MD_OUTPUT0_OFFSET 0
#define MOBILENET_V3_SM_MIN_S8_MD_OUTPUT0_SIZE   1000

// ---- Variables ----

#define MOBILENET_V3_SM_MIN_S8_MD_SCRATCH_REGION 1
#define MOBILENET_V3_SM_MIN_S8_MD_SCRATCH_SIZE   953344
#define MOBILENET_V3_SM_MIN_S8_MD_SCRATCH_FAST_REGION 2
#define MOBILENET_V3_SM_MIN_S8_MD_SCRATCH_FAST_SIZE   253568
