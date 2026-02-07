import os
from PIL import Image

# --- Configuration ---
INPUT_DIR = "img/masked_output"              # Directory containing your PNGs
OUTPUT_DIR = "compressed_output"  # Directory where .txt files will be saved
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# Palette Definition (R, G, B) mapping to 2-bit integers
# 00 (0): White
# 01 (1): Black
# 10 (2): Blue
# 11 (3): Yellow
PALETTE_MAP = [
    (255, 255, 255), # Index 0
    (0, 0, 0),       # Index 1
    (41, 167, 232),  # Index 2
    (255, 247, 128)  # Index 3
]

def get_closest_color_index(pixel):
    """
    Returns the index (0-3) of the closest palette color 
    using squared Euclidean distance.
    """
    r, g, b = pixel[0], pixel[1], pixel[2]
    min_dist_sq = float('inf')
    best_index = 0

    for i, (pr, pg, pb) in enumerate(PALETTE_MAP):
        dist_sq = (r - pr)**2 + (g - pg)**2 + (b - pb)**2
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_index = i
            
    return best_index

def process_images(input_dir, output_dir):
    # 1. Verify Input Directory
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    # 2. Create Output Directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving text files to: {output_dir}/")

    # 3. List PNG files
    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]

    for filename in files:
        file_path = os.path.join(input_dir, filename)
        
        try:
            img = Image.open(file_path).convert("RGB")
            
            # Force resize to 32x32 if necessary
            if img.size != (32, 32):
                img = img.resize((32, 32))

            # --- Step 1: Create List of Lists of Ints ---
            image_matrix = []
            for y in range(32):
                row_ints = []
                for x in range(32):
                    pixel = img.getpixel((x, y))
                    color_index = get_closest_color_index(pixel)
                    row_ints.append(color_index)
                image_matrix.append(row_ints)

            # --- Step 2: Compress each row ---
            compressed_parts = []
            for row in image_matrix:
                # Calculate L (Length of White/0 prefix)
                L = 0
                for val in row:
                    if val == 0:
                        L += 1
                    else:
                        break
                
                # Extract remaining data (from L onwards)
                data_segment = row[L:]

                # Trim trailing Whites (0s) from the right
                while len(data_segment) > 0 and data_segment[-1] == 0:
                    data_segment.pop()

                # Encode data_segment to Base64 (blocks of 3 pixels)
                b64_string = ""
                for i in range(0, len(data_segment), 3):
                    chunk = data_segment[i : i + 3]
                    
                    # Pad with 0 (White) if chunk < 3
                    while len(chunk) < 3:
                        chunk.append(0)

                    # Pack 3 pixels (2 bits each) into one 6-bit integer
                    val = (chunk[0] << 4) | (chunk[1] << 2) | chunk[2]
                    b64_string += BASE64_CHARS[val]

                # Append row format: "L:base64;"
                compressed_parts.append(f"{L}:{b64_string};")

            # --- Step 3: Save to New Directory ---
            final_string = "".join(compressed_parts)
            
            # Change extension from .png to .txt
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(output_dir, txt_filename)
            
            with open(output_path, "w") as f:
                f.write(final_string)
            
            print(f"Processed: {filename} -> {output_path}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    process_images(INPUT_DIR, OUTPUT_DIR)