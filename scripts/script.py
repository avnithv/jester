import os
import numpy as np
from PIL import Image

def apply_hat_mask(directory_path):
    """
    Loads 'hat.PNG', creates a mask from non-white pixels, 
    and applies this mask (turning pixels white) to all other PNGs.
    """
    
    # 1. file paths setup
    hat_path = os.path.join(directory_path, "hat.PNG")
    output_dir = os.path.join(directory_path, "masked_output")

    # Check if hat.PNG exists
    if not os.path.exists(hat_path):
        print(f"Error: 'hat.PNG' not found in {directory_path}")
        return

    # Create output directory to avoid overwriting originals
    os.makedirs(output_dir, exist_ok=True)

    # 2. Process the Hat (Create the Mask)
    print("Processing mask from hat.PNG...")
    try:
        # Convert to RGBA to ensure consistent channel handling
        hat_img = Image.open(hat_path).convert("RGBA")
        hat_arr = np.array(hat_img)
        
        # Define "White" threshold
        # We look at the RGB channels (first 3). 
        # [255, 255, 255] is white.
        # We create a boolean mask: True where the pixel is NOT white.
        
        # Extract RGB channels
        rgb_channels = hat_arr[:, :, :3]
        
        # Check where all RGB values are 255
        is_white_pixel = np.all(rgb_channels == [255, 255, 255], axis=2)
        
        # The mask is the inverse: True where color is present (non-white)
        # This boolean mask is shape (32, 32)
        mask_to_whiten = ~is_white_pixel
        
    except Exception as e:
        print(f"Failed to process hat.PNG: {e}")
        return

    # 3. Process all other images
    files = [f for f in os.listdir(directory_path) if f.lower().endswith('.png')]
    count = 0

    for filename in files:
        if filename == "hat.PNG":
            continue

        if not filename.endswith(".PNG"):
            continue

        file_path = os.path.join(directory_path, filename)
        
        try:
            # Open image and convert to RGBA
            img = Image.open(file_path).convert("RGBA")
            img_arr = np.array(img)
            
            # Ensure the image matches the mask size (32x32)
            if img_arr.shape[:2] != hat_arr.shape[:2]:
                print(f"Skipping {filename}: Size mismatch ({img_arr.shape[:2]})")
                continue

            # 4. Apply the mask
            # Where mask_to_whiten is True, set pixel to Pure White (255, 255, 255, 255)
            img_arr[mask_to_whiten] = [255, 255, 255, 255]

            # Save the result
            result_img = Image.fromarray(img_arr)
            result_img.save(os.path.join(output_dir, filename))
            count += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"---")
    print(f"Success! Processed {count} images.")
    print(f"Modified images saved to: {output_dir}")

# --- Usage Example ---
if __name__ == "__main__":
    # Change this string to point to your specific folder
    target_directory = "./img" 
    
    # Run the function
    if os.path.exists(target_directory):
        apply_hat_mask(target_directory)
    else:
        print(f"Directory not found: {target_directory}")