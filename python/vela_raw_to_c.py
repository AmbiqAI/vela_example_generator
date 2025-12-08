#!/usr/bin/env python3
import argparse, os, textwrap
import numpy as np

HEADER = """\
/*
 * Auto-generated from: {npz_name}
 * Do not edit by hand.
 *
 * Generated for Ethos-U direct driver invocation (no TFLM).
 * Assumes a single NPU command stream with no CPU fallback.
 */
"""

def _to_u8_blob(x):
    """
    Normalize Vela npz entries into a 1-D np.uint8 numpy array.
    Handles:
      - np.ndarray dtype=uint8 (fast path)
      - 0-D object arrays that contain bytes/bytearray/memoryview
      - fixed-width string/void dtypes (S*, V*)
      - scalar arrays (use .tobytes())
      - raw bytes-like objects
      - lists of ints
    """
    import numpy as np

    if isinstance(x, np.ndarray):
        if x.dtype == np.uint8:
            return x.ravel()
        # Fixed-width bytes or raw binary packed in array
        if x.dtype.kind in ("S", "V"):
            return np.frombuffer(x.tobytes(), dtype=np.uint8)
        # 0-D arrays (could be object or void)
        if x.ndim == 0:
            try:
                obj = x.item()
            except Exception:
                obj = None
            if isinstance(obj, (bytes, bytearray, memoryview, np.void)):
                return np.frombuffer(obj, dtype=np.uint8)
            # Fall back to raw bytes of the scalar
            return np.frombuffer(x.tobytes(), dtype=np.uint8)
        # Last resort: try converting to u8
        try:
            return x.astype(np.uint8).ravel()
        except Exception:
            return np.frombuffer(x.tobytes(), dtype=np.uint8)

    # Direct bytes-like
    if isinstance(x, (bytes, bytearray, memoryview)):
        return np.frombuffer(x, dtype=np.uint8)

    # np.void outside ndarray
    try:
        import numpy as np
        if isinstance(x, np.void):
            return np.frombuffer(x, dtype=np.uint8)
    except Exception:
        pass

    # List/iterable of ints
    return np.array(x, dtype=np.uint8).ravel()


def to_c_hex(x, bytes_per_line=12):
    b = _to_u8_blob(x)
    lines = []
    for i in range(0, b.size, bytes_per_line):
        chunk = ", ".join(f"0x{int(v):02X}" for v in b[i:i+bytes_per_line])
        lines.append("    " + chunk)
    return ",\n".join(lines)


def ensure_list(x):
    # Some npz entries can be scalars or vectors; normalize to Python lists
    if x is None:
        return []
    a = np.array(x)
    return a.tolist() if a.ndim > 0 else [a.item()]

def prod(shape):
    p = 1
    for s in shape:
        p *= int(s)
    return p

def main():
    ap = argparse.ArgumentParser(description="Convert Vela raw .npz to C for Ethos-U driver")
    ap.add_argument("npz", help="Vela raw output (.npz) produced with --output-format raw")
    ap.add_argument("--out-dir", default="gen", help="Output directory for generated C")
    ap.add_argument("--prefix", default="model", help="Symbol prefix for generated arrays")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    with np.load(args.npz, allow_pickle=False) as z:
        # Required keys per Vela raw format
        required_any = ["cmd_data", "weight_data", "weight_region"]
        for k in required_any:
            if k not in z.files:
                raise SystemExit(f"Missing '{k}' in {args.npz} (is this Vela --output-format raw?)")

        cmd_data = z["cmd_data"]               # Driver payload (header + command stream)
        weight_data = z["weight_data"]
        weight_region = int(np.array(z["weight_region"]).item())

        # Optional scratch info
        scratch_size = int(np.array(z["scratch_size"]).item()) if "scratch_size" in z.files else 0
        scratch_region = int(np.array(z["scratch_region"]).item()) if "scratch_region" in z.files else None

        scratch_fast_size = int(np.array(z["scratch_fast_size"]).item()) if "scratch_fast_size" in z.files else 0
        scratch_fast_region = int(np.array(z["scratch_fast_region"]).item()) if "scratch_fast_region" in z.files else None

        # Per-tensor layout (may be absent for older Vela versions)
        input_shape      = [tuple(s) for s in ensure_list(z.get("input_shape"))]
        input_elem_size  = [int(e) for e in ensure_list(z.get("input_elem_size"))]
        input_region     = [int(r) for r in ensure_list(z.get("input_region"))]
        input_offset     = [int(o) for o in ensure_list(z.get("input_offset"))]

        output_shape     = [tuple(s) for s in ensure_list(z.get("output_shape"))]
        output_elem_size = [int(e) for e in ensure_list(z.get("output_elem_size"))]
        output_region    = [int(r) for r in ensure_list(z.get("output_region"))]
        output_offset    = [int(o) for o in ensure_list(z.get("output_offset"))]

        variable_shape     = [tuple(s) for s in ensure_list(z.get("variable_shape"))]
        variable_elem_size = [int(e) for e in ensure_list(z.get("variable_elem_size"))]
        variable_region    = [int(r) for r in ensure_list(z.get("variable_region"))]
        variable_offset    = [int(o) for o in ensure_list(z.get("variable_offset"))]

    # ---- Compute region allocations (excluding weights region, which points directly at g_weights) ----
    # There are up to 8 regions; we allocate only those used by inputs/outputs/variables/scratch.
    MAX_REGIONS = 8
    region_caps = {i: 0 for i in range(MAX_REGIONS)}  # required bytes per region
    region_sources = {i: [] for i in range(MAX_REGIONS)}

    # Inputs
    for idx, (sh, es, reg, off) in enumerate(zip(input_shape, input_elem_size, input_region, input_offset)):
        size = prod(sh) * es
        region_caps[reg] = max(region_caps[reg], off + size)
        region_sources[reg].append(("INPUT", idx, off, size))
    # Outputs
    for idx, (sh, es, reg, off) in enumerate(zip(output_shape, output_elem_size, output_region, output_offset)):
        size = prod(sh) * es
        region_caps[reg] = max(region_caps[reg], off + size)
        region_sources[reg].append(("OUTPUT", idx, off, size))
    # Variables
    for idx, (sh, es, reg, off) in enumerate(zip(variable_shape, variable_elem_size, variable_region, variable_offset)):
        size = prod(sh) * es
        region_caps[reg] = max(region_caps[reg], off + size)
        region_sources[reg].append(("VARIABLE", idx, off, size))

    # Scratch
    if scratch_region is not None and scratch_size > 0:
        region_caps[scratch_region] = max(region_caps[scratch_region], scratch_size)
        region_sources[scratch_region].append(("SCRATCH", 0, 0, scratch_size))
    if scratch_fast_region is not None and scratch_fast_size > 0:
        region_caps[scratch_fast_region] = max(region_caps[scratch_fast_region], scratch_fast_size)
        region_sources[scratch_fast_region].append(("SCRATCH_FAST", 0, 0, scratch_fast_size))

    # Never try to allocate the weight region buffer; we will bind it to g_weights[]
    region_caps[weight_region] = 0

    # ---- Write headers/sources ----
    npz_name = os.path.basename(args.npz)

    # 1) Command stream (driver payload) header
    h_cmd = os.path.join(args.out_dir, f"{args.prefix}_cmd_data.h")
    with open(h_cmd, "w") as f:
        f.write(HEADER.format(npz_name=npz_name))
        f.write(f"#pragma once\n#include <stdint.h>\n#include <stddef.h>\n\n")
        f.write(f"static const uint8_t {args.prefix}_cmd_data[] = {{\n{to_c_hex(cmd_data)}\n}};\n")
        f.write(f"static const size_t  {args.prefix}_cmd_size = sizeof({args.prefix}_cmd_data);\n")

    # 2) Weights header
    h_weights = os.path.join(args.out_dir, f"{args.prefix}_weights.h")
    with open(h_weights, "w") as f:
        f.write(HEADER.format(npz_name=npz_name))
        f.write(f"#pragma once\n#include <stdint.h>\n#include <stddef.h>\n\n")
        f.write(f"// Weight region index chosen by Vela:\n#define {args.prefix.upper()}_WEIGHT_REGION {weight_region}\n\n")
        f.write(f"__attribute__((aligned(32)))\nstatic const uint8_t {args.prefix}_weights[] = {{\n{to_c_hex(weight_data)}\n}};\n")
        f.write(f"static const size_t  {args.prefix}_weights_size = sizeof({args.prefix}_weights);\n")

    # 3) Metadata header (offsets/sizes per tensor)
    h_meta = os.path.join(args.out_dir, f"{args.prefix}_meta.h")
    with open(h_meta, "w") as f:
        f.write(HEADER.format(npz_name=npz_name))
        f.write("#pragma once\n#include <stddef.h>\n#include <stdint.h>\n\n")
        f.write("// Base-pointer array length for Ethos-U\n#define ETHOSU_MAX_REGIONS 8\n\n")

        # Input/output/variable macros
        f.write(f"// ---- Inputs ----\n")
        for i, (sh, es, reg, off) in enumerate(zip(input_shape, input_elem_size, input_region, input_offset)):
            sz = prod(sh) * es
            f.write(f"#define {args.prefix.upper()}_INPUT{ i }_REGION  {reg}\n")
            f.write(f"#define {args.prefix.upper()}_INPUT{ i }_OFFSET  {off}\n")
            f.write(f"#define {args.prefix.upper()}_INPUT{ i }_SIZE    {sz}\n")
        f.write(f"\n// ---- Outputs ----\n")
        for i, (sh, es, reg, off) in enumerate(zip(output_shape, output_elem_size, output_region, output_offset)):
            sz = prod(sh) * es
            f.write(f"#define {args.prefix.upper()}_OUTPUT{ i }_REGION {reg}\n")
            f.write(f"#define {args.prefix.upper()}_OUTPUT{ i }_OFFSET {off}\n")
            f.write(f"#define {args.prefix.upper()}_OUTPUT{ i }_SIZE   {sz}\n")
        f.write(f"\n// ---- Variables ----\n")
        for i, (sh, es, reg, off) in enumerate(zip(variable_shape, variable_elem_size, variable_region, variable_offset)):
            sz = prod(sh) * es
            f.write(f"#define {args.prefix.upper()}_VARIABLE{ i }_REGION {reg}\n")
            f.write(f"#define {args.prefix.upper()}_VARIABLE{ i }_OFFSET {off}\n")
            f.write(f"#define {args.prefix.upper()}_VARIABLE{ i }_SIZE   {sz}\n")

        if scratch_region is not None:
            f.write(f"\n#define {args.prefix.upper()}_SCRATCH_REGION {scratch_region}\n")
            f.write(f"#define {args.prefix.upper()}_SCRATCH_SIZE   {scratch_size}\n")
        if scratch_fast_region is not None:
            f.write(f"#define {args.prefix.upper()}_SCRATCH_FAST_REGION {scratch_fast_region}\n")
            f.write(f"#define {args.prefix.upper()}_SCRATCH_FAST_SIZE   {scratch_fast_size}\n")

    # 4) Region buffers (excluding weights)
    h_buf = os.path.join(args.out_dir, f"{args.prefix}_buffers.h")
    c_buf = os.path.join(args.out_dir, f"{args.prefix}_buffers.c")

    with open(h_buf, "w") as f:
        f.write(HEADER.format(npz_name=npz_name))
        f.write("#pragma once\n#include <stddef.h>\n#include <stdint.h>\n\n")
        f.write("extern uint8_t* get_region_base_ptr(int region);\n")
        f.write("extern size_t   get_region_size(int region);\n")

    with open(c_buf, "w") as f:
        f.write(HEADER.format(npz_name=npz_name))
        f.write('#include <stddef.h>\n#include <stdint.h>\n')
        f.write(f'#include "{args.prefix}_weights.h"\n')
        f.write(f'#include "{args.prefix}_meta.h"\n\n')

        # Emit arrays for used regions
        used_regions = [r for r, cap in region_caps.items() if cap > 0]
        for r in used_regions:
            f.write(f'__attribute__((aligned(32))) static uint8_t {args.prefix}_region_{r}[{region_caps[r]}] = {{0}};\n')
        f.write("\n")

        # Accessors
        f.write("uint8_t* get_region_base_ptr(int region) {\n")
        f.write("    switch(region) {\n")
        for r in used_regions:
            f.write(f"    case {r}: return {args.prefix}_region_{r};\n")
        f.write(f"    case {weight_region}: return (uint8_t*){args.prefix}_weights; // weights region\n")
        f.write("    default: return (uint8_t*)0; // unused region\n")
        f.write("    }\n}\n\n")

        f.write("size_t get_region_size(int region) {\n")
        f.write("    switch(region) {\n")
        for r in used_regions:
            f.write(f"    case {r}: return sizeof({args.prefix}_region_{r});\n")
        f.write(f"    case {weight_region}: return {args.prefix}_weights_size;\n")
        f.write("    default: return 0;\n")
        f.write("    }\n}\n")

    # 5) Minimal runner (shows how to invoke the stream)
    c_run = os.path.join(args.out_dir, f"{args.prefix}_run.c")
    with open(c_run, "w") as f:
        f.write(HEADER.format(npz_name=npz_name))
        f.write(textwrap.dedent(f"""\
            #include <stdint.h>
            #include <stddef.h>
            #include "ethosu_driver.h"
            #include "{args.prefix}_cmd_data.h"
            #include "{args.prefix}_weights.h"
            #include "{args.prefix}_meta.h"
            #include "{args.prefix}_buffers.h"

            // Provide your platform's NPU register base here.
            extern void *ethosu_get_regs_base(void);

            int {args.prefix}_invoke(void) {{
                uint64_t base_addr[ETHOSU_MAX_REGIONS] = {{0}};
                size_t   base_size[ETHOSU_MAX_REGIONS] = {{0}};

                // Bind all present regions (weights + any allocated regions).
                for (int r = 0; r < ETHOSU_MAX_REGIONS; ++r) {{
                    uint8_t* p = get_region_base_ptr(r);
                    size_t   s = get_region_size(r);
                    if (p && s) {{
                        base_addr[r] = (uint64_t)(uintptr_t)p;
                        base_size[r] = s;
                    }}
                }}

                // Init driver and run
                struct ethosu_driver drv = {{0}};
                int rc = ethosu_init(&drv, ethosu_get_regs_base(), 0, 0, /*secure*/0, /*privileged*/1);
                if (rc) return rc;

                // Optional: configure cache handling per region (defaults to scratch only).
                // ethosu_set_basep_cache_mask(&drv, /*flush_mask*/0xFF, /*invalidate_mask*/0xFF);

                rc = ethosu_invoke(&drv,
                                   {args.prefix}_cmd_data, (int){args.prefix}_cmd_size,
                                   base_addr, base_size, ETHOSU_MAX_REGIONS);
                // Wait for completion if using async interface; here we use the sync wrapper.
                ethosu_deinit(&drv);
                return rc;
            }}
            """))

    print(f"Generated:\n  {h_cmd}\n  {h_weights}\n  {h_meta}\n  {h_buf}\n  {c_buf}\n  {c_run}")
    print("\nUsage example:\n  gcc -Igen -c gen/{p}_buffers.c -c gen/{p}_run.c -o app.o  # plus your platform glue & driver\n".format(p=args.prefix))

if __name__ == "__main__":
    main()

