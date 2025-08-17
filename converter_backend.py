# converter_backend.py

import io
import os
from PIL import Image

# --- TNPC (Tamil Nadu Public Service Commission) Specifications ---
TNPC_PHOTO_DIMS = (200, 230)
TNPC_PHOTO_SIZE_KB = (20, 50)
TNPC_SIGN_DIMS = (140, 60)
TNPC_SIGN_SIZE_KB = (10, 20)

def handle_rgba_to_rgb(image: Image.Image) -> Image.Image:
    """Converts an RGBA image to RGB by pasting it onto a white background."""
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        return background
    return image

def convert_to_tnpc(input_path: str, output_path: str):
    """
    Converts an image to be compliant with TNPC specifications.
    Returns a status message.
    """
    try:
        with Image.open(input_path) as img:
            aspect_ratio = img.width / img.height
            if aspect_ratio < 1.2:
                target_dims, target_size_kb, file_type = TNPC_PHOTO_DIMS, TNPC_PHOTO_SIZE_KB, "Photograph"
            else:
                target_dims, target_size_kb, file_type = TNPC_SIGN_DIMS, TNPC_SIGN_SIZE_KB, "Signature"

            log_msg = (
                f"Processing '{os.path.basename(input_path)}' as TNPC {file_type}...\n"
                f"  Target: {target_dims[0]}x{target_dims[1]}px, {target_size_kb[0]}-{target_size_kb[1]} KB"
            )
            print(log_msg)

            resized_img = img.resize(target_dims, Image.Resampling.LANCZOS)
            resized_img = handle_rgba_to_rgb(resized_img)

            quality, min_quality = 95, 10
            final_data = None
            while quality >= min_quality:
                buffer = io.BytesIO()
                resized_img.save(buffer, format='JPEG', quality=quality)
                size_kb = len(buffer.getvalue()) / 1024
                if target_size_kb[0] <= size_kb <= target_size_kb[1]:
                    final_data = buffer.getvalue()
                    break
                elif size_kb > target_size_kb[1]:
                    quality -= 5
                else:
                    final_data = buffer.getvalue()
                    break
            
            if final_data:
                with open(output_path, 'wb') as f:
                    f.write(final_data)
                final_size = len(final_data) / 1024
                return f"✅ Success! Saved to '{os.path.basename(output_path)}' ({final_size:.2f} KB, Quality: {quality})"
            else:
                return f"❌ Error: Could not meet file size requirements for '{os.path.basename(input_path)}'."

    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"

def convert_to_ico(input_path: str, output_path: str, sizes: list):
    """Converts an image to the .ico format. Returns a status message."""
    try:
        with Image.open(input_path) as img:
            icon_sizes = [(s, s) for s in sizes]
            img.save(output_path, format='ICO', sizes=icon_sizes)
            return f"✅ Success! Saved icon '{os.path.basename(output_path)}' with sizes {sizes}."
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"

def convert_generic(input_path: str, output_path: str, quality: int):
    """Performs general-purpose image format conversion. Returns a status message."""
    try:
        with Image.open(input_path) as img:
            save_options = {}
            output_ext = os.path.splitext(output_path)[1].lower()
            if output_ext in ['.jpg', '.jpeg', '.webp']:
                save_options['quality'] = quality
                img = handle_rgba_to_rgb(img)
            
            img.save(output_path, **save_options)
            return f"✅ Success! Saved '{os.path.basename(output_path)}'."
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"