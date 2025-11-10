import re

# === User settings ===
input_file = "conv_in_height_1_weights.h"   # Your .c or .h file
output_file = "conv_in_height_1_weights.txt"    # Output .txt file
array_name = "conv_in_height_1_weights"  # Array to extract

# ======================

# Read entire file
with open(input_file, "r") as f:
    content = f.read()

# Regular expression to match array data
pattern = rf"{array_name}\s*\[[^\]]*\]\s*=\s*\{{([^}}]+)\}}"
match = re.search(pattern, content, re.DOTALL)

if not match:
    print(f"Could not find array '{array_name}' in {input_file}")
    exit(1)

# Extract numbers (split on commas, remove whitespace)
data_str = match.group(1)
data_list = [x.strip() for x in data_str.split(",") if x.strip()]

# Convert to integers
numbers = [int(x) for x in data_list]

# Write to file, one per line
with open(output_file, "w") as f:
    for n in numbers:
        f.write(f"{n}\n")

print(f"Extracted {len(numbers)} values from '{array_name}' into '{output_file}'")
