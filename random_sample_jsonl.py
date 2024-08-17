import json
import random

def sample_jsonl(input_file, output_file, sample_size=20):
    # Read all lines from the input file
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Ensure we don't try to sample more lines than exist in the file
    sample_size = min(sample_size, len(lines))

    # Randomly sample 'sample_size' number of lines
    sampled_indices = random.sample(range(len(lines)), sample_size)
    sampled_lines = [lines[i] for i in sampled_indices]

    # Remove sampled lines from the original list
    remaining_lines = [line for i, line in enumerate(lines) if i not in sampled_indices]

    # Write the sampled lines to the output file
    with open(output_file, 'w') as f:
        f.writelines(sampled_lines)

    # Write the remaining lines back to the input file
    with open(input_file, 'w') as f:
        f.writelines(remaining_lines)

if __name__ == "__main__":
    input_file = "../data/training-data-train_8-16.jsonl"  # Replace with your input file name
    output_file = "../data/training-data-validate_8-16.jsonl"  # Replace with your desired output file name
    sample_jsonl(input_file, output_file)
    print(f"Randomly sampled 20 lines from {input_file} and saved to {output_file}")
    print(f"Removed sampled lines from {input_file}")
