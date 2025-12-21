/*
 * Auto-generated from: ad_medium_int8_vela.npz
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
#define AD_MEDIUM_INT8_INPUT0_REGION  1
#define AD_MEDIUM_INT8_INPUT0_OFFSET  196608
#define AD_MEDIUM_INT8_INPUT0_SIZE    1024

// ---- Outputs ----
#define AD_MEDIUM_INT8_OUTPUT0_REGION 1
#define AD_MEDIUM_INT8_OUTPUT0_OFFSET 0
#define AD_MEDIUM_INT8_OUTPUT0_SIZE   8

// ---- Variables ----

#define AD_MEDIUM_INT8_SCRATCH_REGION 1
#define AD_MEDIUM_INT8_SCRATCH_SIZE   197632
#define AD_MEDIUM_INT8_SCRATCH_FAST_REGION 2
#define AD_MEDIUM_INT8_SCRATCH_FAST_SIZE   239968
