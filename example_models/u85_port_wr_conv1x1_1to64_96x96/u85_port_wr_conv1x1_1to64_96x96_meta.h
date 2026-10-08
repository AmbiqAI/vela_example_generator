/*
 * Auto-generated from: u85_port_wr_conv1x1_1to64_96x96_vela.npz
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
#define U85_PORT_WR_CONV1X1_1TO64_96X96_INPUT0_REGION  1
#define U85_PORT_WR_CONV1X1_1TO64_96X96_INPUT0_OFFSET  589824
#define U85_PORT_WR_CONV1X1_1TO64_96X96_INPUT0_SIZE    9216

// ---- Outputs ----
#define U85_PORT_WR_CONV1X1_1TO64_96X96_OUTPUT0_REGION 1
#define U85_PORT_WR_CONV1X1_1TO64_96X96_OUTPUT0_OFFSET 0
#define U85_PORT_WR_CONV1X1_1TO64_96X96_OUTPUT0_SIZE   589824

// ---- Variables ----

#define U85_PORT_WR_CONV1X1_1TO64_96X96_SCRATCH_REGION 1
#define U85_PORT_WR_CONV1X1_1TO64_96X96_SCRATCH_SIZE   599040
#define U85_PORT_WR_CONV1X1_1TO64_96X96_SCRATCH_FAST_REGION 2
#define U85_PORT_WR_CONV1X1_1TO64_96X96_SCRATCH_FAST_SIZE   0
