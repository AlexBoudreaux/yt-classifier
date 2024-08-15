import json
import random
from typing import List, Dict

def read_jsonl(file_path: str) -> List[Dict]:
    """Read a JSONL file and return a list of dictionaries."""
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

def write_jsonl(data: List[Dict], file_path: str):
    """Write a list of dictionaries to a JSONL file."""
    with open(file_path, 'w') as file:
        for item in data:
            json.dump(item, file)
            file.write('\n')

def split_data(data: List[Dict], train_ratio: float = 0.8) -> tuple:
    """Split data into training and validation sets."""
    random.shuffle(data)
    split_index = int(len(data) * train_ratio)
    return data[:split_index], data[split_index:]

def prepare_data(input_file: str, train_output: str, val_output: str, train_ratio: float = 0.8):
    """Prepare data for fine-tuning by splitting into training and validation sets."""
    # Read input data
    data = read_jsonl(input_file)
    
    # Split data
    train_data, val_data = split_data(data, train_ratio)
    
    # Write output files
    write_jsonl(train_data, train_output)
    write_jsonl(val_data, val_output)
    
    print(f"Total samples: {len(data)}")
    print(f"Training samples: {len(train_data)}")
    print(f"Validation samples: {len(val_data)}")

if __name__ == "__main__":
    input_file = "path/to/your/input.jsonl"
    train_output = "path/to/your/train_data.jsonl"
    val_output = "path/to/your/val_data.jsonl"
    
    prepare_data(input_file, train_output, val_output)
