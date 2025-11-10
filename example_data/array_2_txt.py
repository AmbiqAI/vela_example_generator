import re

# === User settings ===
input_file = "./fc_in__200__o_32_relu/converted_model/fc_in__200__o_32_relu_data.h"      # Your C or header file
output_file = "./fc_in__200__o_32_relu/converted_model/fc_in__200__o_32_relu_output.txt"    # Output .txt file
array_name = "fc_in__200__o_32_relu_output"  # Array variable name
# ======================

# Read the file
with open(input_file, "r") as f:
    content = f.read()

# Regex pattern to find the array content inside braces { ... }
pattern = rf"{array_name}\s*\[[^\]]*\]\s*=\s*\{{([^}}]+)\}}"
match = re.search(pattern, content, re.DOTALL)

if not match:
    print(f"Could not find array '{array_name}' in {input_file}")
    exit(1)

# Extract data between braces
data_str = match.group(1)

# Split on commas, remove whitespace
raw_values = [x.strip() for x in data_str.split(",") if x.strip()]

numbers = []
for val in raw_values:
    try:
        # Automatically detect hex (0x..) or decimal
        num = int(val, 0)
        numbers.append(num)
    except ValueError:
        print(f"Skipping invalid value: {val}")

# Write numbers to text file (one per line)
with open(output_file, "w") as f:
    for n in numbers:
        f.write(f"{n}\n")

print(f"Extracted {len(numbers)} values from '{array_name}' → {output_file}")
