/*
 * Auto-generated from: u85_port_rd_maxpool_global_96x96x32_vela.npz
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
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_INPUT0_REGION  1
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_INPUT0_OFFSET  32
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_INPUT0_SIZE    294912

// ---- Outputs ----
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_OUTPUT0_REGION 1
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_OUTPUT0_OFFSET 0
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_OUTPUT0_SIZE   32

// ---- Variables ----

#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_SCRATCH_REGION 1
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_SCRATCH_SIZE   294944
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_SCRATCH_FAST_REGION 2
#define U85_PORT_RD_MAXPOOL_GLOBAL_96X96X32_SCRATCH_FAST_SIZE   0
