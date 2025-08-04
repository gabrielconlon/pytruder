import itertools
import csv
from pathlib import Path

def generate_payload_matrix(output_path, *input_lists):
    combinations = list(itertools.product(*input_lists))
    output_file = Path(output_path)
    with output_file.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for combo in combinations:
            writer.writerow(combo)
    return output_file, len(combinations)

# Example usage with hardcoded values for demonstration
offsets = list(range(0, 11))  # §1§
table_names = ["users", "pg_authid", "pg_roles", "pg_shadow"]  # §2§

output_file, count = generate_payload_matrix("./payloads.csv", offsets, table_names)
output_file.name, count
