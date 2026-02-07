import os
import sys
from PIL import Image

# --- Configuration ---
# Colors defined in the prompt
COLOR_MAP = {
    "Green": (143, 178, 91),   # #8FB25B
    "Black": (0, 0, 0),        # #000000
    "White": (255, 255, 255),  # #FFFFFF
    "Pink":  (255, 181, 181)   # #FFB5B5
}

# Allow a small margin of error for colors (e.g. compression artifacts)
TOLERANCE = 5 

def matches_color(pixel, target_rgb):
    """Checks if a pixel matches a target color within tolerance."""
    r, g, b = pixel[:3]
    tr, tg, tb = target_rgb
    dist = (r - tr)**2 + (g - tg)**2 + (b - tb)**2
    return dist <= TOLERANCE**2

def get_region_labels():
    """Generator for region labels: A-Z, then a-z."""
    import string
    for char in string.ascii_uppercase:
        yield char
    for char in string.ascii_lowercase:
        yield char
    # Fallback if > 52 regions (unlikely for 32x32)
    i = 0
    while True:
        yield str(i)
        i += 1

def process_image(image_path, output_path):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    if img.size != (32, 32):
        print(f"Warning: Image size is {img.size}, resizing to 32x32.")
        img = img.resize((32, 32))

    pixels = img.load()
    width, height = img.size

    # 1. Initialize Grid and Classification Matrix
    # We use a 2D array to store the final characters.
    grid = [['?' for _ in range(width)] for _ in range(height)]
    
    # Track status of pixels
    # Types: 'green', 'pink', 'processed'
    pixel_types = [[None for _ in range(width)] for _ in range(height)]

    green_coords = []
    pink_coords = []

    for y in range(height):
        for x in range(width):
            p = pixels[x, y]
            
            if matches_color(p, COLOR_MAP["White"]):
                grid[y][x] = '.'
                pixel_types[y][x] = 'processed'
            elif matches_color(p, COLOR_MAP["Black"]):
                grid[y][x] = '#'
                pixel_types[y][x] = 'processed'
            elif matches_color(p, COLOR_MAP["Green"]):
                pixel_types[y][x] = 'green'
                green_coords.append((x, y))
            elif matches_color(p, COLOR_MAP["Pink"]):
                pixel_types[y][x] = 'pink'
                pink_coords.append((x, y))
            else:
                # Handle unknown colors (treat as white/background or error?)
                # Defaulting to '.' for safety
                grid[y][x] = '.'
                pixel_types[y][x] = 'processed'

    # 2. Floodfill Green Regions
    label_gen = get_region_labels()
    visited_green = set()
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Orthogonal only

    for gx, gy in green_coords:
        if (gx, gy) in visited_green:
            continue
        
        # Start a new region
        current_label = next(label_gen)
        queue = [(gx, gy)]
        visited_green.add((gx, gy))
        grid[gy][gx] = current_label
        
        while queue:
            cx, cy = queue.pop(0)
            
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                
                # Check bounds
                if 0 <= nx < width and 0 <= ny < height:
                    # If neighbor is green and not visited
                    if pixel_types[ny][nx] == 'green' and (nx, ny) not in visited_green:
                        visited_green.add((nx, ny))
                        grid[ny][nx] = current_label
                        queue.append((nx, ny))

    # 3. Handle Pink Pixels (Merge with adjacent green regions)
    # We iterate until no changes are made to handle chains of pink pixels attached to green
    
    pink_pending = set(pink_coords)
    changed = True
    
    while changed and pink_pending:
        changed = False
        processed_this_round = set()

        for px, py in pink_pending:
            # Look for an orthogonal neighbor that already has a Label (A-Z, a-z)
            found_label = None
            for dx, dy in directions:
                nx, ny = px + dx, py + dy
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor_char = grid[ny][nx]
                    # Check if neighbor is a region letter (not . or # or ?)
                    if neighbor_char not in ['.', '#', '?']:
                        found_label = neighbor_char
                        break
            
            if found_label:
                grid[py][px] = found_label
                processed_this_round.add((px, py))
                changed = True
        
        pink_pending -= processed_this_round

    # Determine fallback for orphaned pink pixels (if any)
    for px, py in pink_pending:
        grid[py][px] = '.' # Treat as whitespace if it never touches a green region

    # 4. Save to file
    try:
        with open(output_path, "w") as f:
            for row in grid:
                row_str = "".join(row)
                f.write(f"\"{row_str}\",\n")
        print(f"Successfully processed {image_path} -> {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

# --- Usage ---
if __name__ == "__main__":
    # Change these paths as needed
    input_image = "img/hat.PNG"
    output_text = "output_grid.txt"
    
    # If passing arguments via command line
    if len(sys.argv) > 1:
        input_image = sys.argv[1]
    if len(sys.argv) > 2:
        output_text = sys.argv[2]

    process_image(input_image, output_text)