/*
 * Auto-generated from: kws_micronet_m_vela.npz
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
#define KWS_MICRONET_M_INPUT0_REGION  1
#define KWS_MICRONET_M_INPUT0_OFFSET  0
#define KWS_MICRONET_M_INPUT0_SIZE    490

// ---- Outputs ----
#define KWS_MICRONET_M_OUTPUT0_REGION 1
#define KWS_MICRONET_M_OUTPUT0_OFFSET 0
#define KWS_MICRONET_M_OUTPUT0_SIZE   12

// ---- Variables ----

#define KWS_MICRONET_M_SCRATCH_REGION 1
#define KWS_MICRONET_M_SCRATCH_SIZE   496
#define KWS_MICRONET_M_SCRATCH_FAST_REGION 2
#define KWS_MICRONET_M_SCRATCH_FAST_SIZE   187264
