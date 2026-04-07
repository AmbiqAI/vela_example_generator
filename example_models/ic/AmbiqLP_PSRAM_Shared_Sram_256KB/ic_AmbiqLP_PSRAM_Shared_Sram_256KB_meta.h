/*
 * Auto-generated from: ic_vela.npz
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
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_INPUT0_REGION  1
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_INPUT0_OFFSET  16384
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_INPUT0_SIZE    3072

// ---- Outputs ----
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_OUTPUT0_REGION 1
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_OUTPUT0_OFFSET 128
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_OUTPUT0_SIZE   10

// ---- Variables ----

#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_SCRATCH_REGION 1
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_SCRATCH_SIZE   75072
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_SCRATCH_FAST_REGION 0
#define IC_AMBIQLP_PSRAM_SHARED_SRAM_256KB_SCRATCH_FAST_SIZE   0
