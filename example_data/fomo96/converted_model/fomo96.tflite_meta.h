/*
 * Auto-generated from: fomo96_vela.npz
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
#define FOMO96.TFLITE_INPUT0_REGION  1
#define FOMO96.TFLITE_INPUT0_OFFSET  0
#define FOMO96.TFLITE_INPUT0_SIZE    9216

// ---- Outputs ----
#define FOMO96.TFLITE_OUTPUT0_REGION 1
#define FOMO96.TFLITE_OUTPUT0_OFFSET 0
#define FOMO96.TFLITE_OUTPUT0_SIZE   288

// ---- Variables ----

#define FOMO96.TFLITE_SCRATCH_REGION 1
#define FOMO96.TFLITE_SCRATCH_SIZE   9216
#define FOMO96.TFLITE_SCRATCH_FAST_REGION 2
#define FOMO96.TFLITE_SCRATCH_FAST_SIZE   149552
