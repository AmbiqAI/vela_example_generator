/*
 * Auto-generated from: resnet_v1_8_32_tfs_int8_17_9_vela.npz
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
#define RESNET_V1_8_32_TFS_INT8_17_9_INPUT0_REGION  1
#define RESNET_V1_8_32_TFS_INT8_17_9_INPUT0_OFFSET  0
#define RESNET_V1_8_32_TFS_INT8_17_9_INPUT0_SIZE    3072

// ---- Outputs ----
#define RESNET_V1_8_32_TFS_INT8_17_9_OUTPUT0_REGION 1
#define RESNET_V1_8_32_TFS_INT8_17_9_OUTPUT0_OFFSET 0
#define RESNET_V1_8_32_TFS_INT8_17_9_OUTPUT0_SIZE   8192

// ---- Variables ----

#define RESNET_V1_8_32_TFS_INT8_17_9_SCRATCH_REGION 1
#define RESNET_V1_8_32_TFS_INT8_17_9_SCRATCH_SIZE   8192
#define RESNET_V1_8_32_TFS_INT8_17_9_SCRATCH_FAST_REGION 2
#define RESNET_V1_8_32_TFS_INT8_17_9_SCRATCH_FAST_SIZE   57376
