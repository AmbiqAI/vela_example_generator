/*
 * Auto-generated from: conv_in_height_1_vela.npz
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
#include <stdint.h>
#include <stddef.h>
#include "ethosu_driver.h"
#include "conv_in_height_1_cmd_data.h"
#include "conv_in_height_1_weights.h"
#include "conv_in_height_1_meta.h"
#include "conv_in_height_1_buffers.h"

// Provide your platform's NPU register base here.
extern void *ethosu_get_regs_base(void);

int conv_in_height_1_invoke(void) {
    uint64_t base_addr[ETHOSU_MAX_REGIONS] = {0};
    size_t   base_size[ETHOSU_MAX_REGIONS] = {0};

    // Bind all present regions (weights + any allocated regions).
    for (int r = 0; r < ETHOSU_MAX_REGIONS; ++r) {
        uint8_t* p = get_region_base_ptr(r);
        size_t   s = get_region_size(r);
        if (p && s) {
            base_addr[r] = (uint64_t)(uintptr_t)p;
            base_size[r] = s;
        }
    }

    // Init driver and run
    struct ethosu_driver drv = {0};
    int rc = ethosu_init(&drv, ethosu_get_regs_base(), 0, 0, /*secure*/0, /*privileged*/1);
    if (rc) return rc;

    // Optional: configure cache handling per region (defaults to scratch only).
    // ethosu_set_basep_cache_mask(&drv, /*flush_mask*/0xFF, /*invalidate_mask*/0xFF);

    rc = ethosu_invoke(&drv,
                       conv_in_height_1_cmd_data, (int)conv_in_height_1_cmd_size,
                       base_addr, base_size, ETHOSU_MAX_REGIONS);
    // Wait for completion if using async interface; here we use the sync wrapper.
    ethosu_deinit(&drv);
    return rc;
}
