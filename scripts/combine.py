import os

# Configuration
INPUT_DIR = "compressed_output"  # Directory containing your .txt files
OUTPUT_FILE = "all_levels.js"    # The single output file name

def combine_text_files(input_dir, output_file):
    # 1. Verify Input Directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    # 2. Get list of .txt files
    # We sort them to ensure a consistent order in the output file
    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.txt')])

    if not files:
        print(f"No .txt files found in '{input_dir}'.")
        return

    try:
        with open(output_file, 'w') as out_f:
            print(f"Processing {len(files)} files from '{input_dir}'...")

            for filename in files:
                file_path = os.path.join(input_dir, filename)
                
                try:
                    with open(file_path, 'r') as in_f:
                        # Read content and strip existing newlines/whitespace
                        content = in_f.read().strip()
                        
                        # Create variable name: filename in CAPS without extension + "_str"
                        # e.g., "level1.txt" -> "LEVEL1_str"
                        var_name = os.path.splitext(filename)[0].upper() + "_str"
                        
                        # Format the line
                        # const LEVEL1_str = "content";
                        line = f'const {var_name} = "{content}";\n'
                        
                        out_f.write(line)
                        print(f"  Added: {filename} -> {var_name}")

                except Exception as e:
                    print(f"  Error reading {filename}: {e}")

        print(f"Successfully created '{output_file}'")

    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    combine_text_files(INPUT_DIR, OUTPUT_FILE)