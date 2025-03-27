from flask import Flask, request, jsonify, send_file
import os
import subprocess
from werkzeug.utils import secure_filename
import uuid
import shutil
import tempfile
import logging
from PIL import Image
import io
import cv2
import numpy as np
import time

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/tmp/image_processing'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/process/<tool>', methods=['POST'])
def process_image(tool):
    # Check if an image file was uploaded
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Get parameters
    width = request.form.get('width', 800, type=int)
    height = request.form.get('height', 600, type=int)
    output_format = request.form.get('format', 'jpg').lower()
    
    # Create a unique filename to avoid collisions
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_input_{filename}")
    output_filename = f"{unique_id}_output.{output_format}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Save the input file
    file.save(input_path)
    
    try:
        # Process based on selected tool
        if tool == 'imagemagick':
            process_imagemagick(input_path, output_path, width, height)
        elif tool == 'graphicsmagick':
            process_graphicsmagick(input_path, output_path, width, height)
        elif tool == 'ffmpeg':
            process_ffmpeg(input_path, output_path, width, height)
        elif tool == 'vips':
            process_vips(input_path, output_path, width, height)
        elif tool == 'pillow':
            process_pillow(input_path, output_path, width, height)
        elif tool == 'nconvert':
            process_nconvert(input_path, output_path, width, height)
        elif tool == 'opencv':
            process_opencv(input_path, output_path, width, height)
        elif tool == 'imageio':
            process_imageio(input_path, output_path, width, height)
        elif tool == 'gimp':
            process_gimp(input_path, output_path, width, height)  
        elif tool == 'skimage':
            process_skimage(input_path, output_path, width, height)
        elif tool == 'pyvips':
            process_pyvips(input_path, output_path, width, height)
        else:
            return jsonify({"error": f"Unknown tool: {tool}. Available tools: imagemagick, graphicsmagick, ffmpeg, vips, pillow, nconvert, opencv, imageio, gimp, skimage, pyvips"}), 400
        
        # Return the processed image
        return send_file(output_path, as_attachment=True, download_name=output_filename)
    
    except Exception as e:
        logger.error(f"Error processing with {tool}: {str(e)}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500
    
    finally:
        # Clean up files after sending response
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            # We don't remove output_path here as it's being sent to the client
        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}")

# The actual processing functions for each tool
def process_imagemagick(input_path, output_path, width, height):
    # Resize and center crop
    cmd = [
        'convert', input_path,
        '-resize', f'{width}x{height}^',
        '-gravity', 'center',
        '-extent', f'{width}x{height}',
        output_path
    ]
    subprocess.run(cmd, check=True)

def process_graphicsmagick(input_path, output_path, width, height):
    # Resize and center crop
    cmd = [
        'gm', 'convert', input_path,
        '-resize', f'{width}x{height}^',
        '-gravity', 'center',
        '-extent', f'{width}x{height}',
        output_path
    ]
    subprocess.run(cmd, check=True)

def process_ffmpeg(input_path, output_path, width, height):
    # First resize to cover the dimensions, then crop to center
    cmd = [
        'ffmpeg', '-i', input_path,
        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}',
        '-y', output_path
    ]
    subprocess.run(cmd, check=True)

def process_vips(input_path, output_path, width, height):
    # Resize then center crop
    cmd = [
        'vips', 'thumbnail', input_path, output_path,
        width, height,
        '--size', 'both'
    ]
    subprocess.run(cmd, check=True)

def process_pillow(input_path, output_path, width, height):
    # Open image with Pillow
    img = Image.open(input_path)
    
    # Calculate dimensions to maintain aspect ratio
    img_width, img_height = img.size
    ratio = max(width/img_width, height/img_height)
    new_size = (int(img_width * ratio), int(img_height * ratio))
    
    # Resize image to cover the target dimensions
    img = img.resize(new_size, Image.LANCZOS)
    
    # Calculate crop box (center crop)
    left = (new_size[0] - width) / 2
    top = (new_size[1] - height) / 2
    right = left + width
    bottom = top + height
    img = img.crop((left, top, right, bottom))
    
    # Save the result
    img.save(output_path)

def process_nconvert(input_path, output_path, width, height):
    # Resize and center crop using NConvert
    cmd = [
        'nconvert',
        '-resize', f'{width} {height}', '-ratio', '-rtype', 'lanczos',
        '-canvas', f'{width} {height}', '-ctype', 'center',
        '-out', output_path.split('.')[-1],
        '-o', output_path,
        input_path
    ]
    subprocess.run(cmd, check=True)

def process_opencv(input_path, output_path, width, height):
    # Resize and center crop using OpenCV
    img = cv2.imread(input_path)
    
    # Calculate dimensions to maintain aspect ratio
    h, w = img.shape[:2]
    ratio = max(width/w, height/h)
    new_size = (int(w * ratio), int(h * ratio))
    
    # Resize image to cover the target dimensions
    img_resized = cv2.resize(img, new_size, interpolation=cv2.INTER_LANCZOS4)
    
    # Calculate crop coordinates (center crop)
    start_x = (new_size[0] - width) // 2
    start_y = (new_size[1] - height) // 2
    
    # Crop the image
    img_cropped = img_resized[start_y:start_y+height, start_x:start_x+width]
    
    # Save the result
    cv2.imwrite(output_path, img_cropped)

def process_imageio(input_path, output_path, width, height):
    # Resize and center crop using ImageIO
    import imageio.v3 as iio
    from skimage.transform import resize
    
    # Read image
    img = iio.imread(input_path)
    
    # Calculate dimensions to maintain aspect ratio
    h, w = img.shape[:2]
    ratio = max(width/w, height/h)
    new_h, new_w = int(h * ratio), int(w * ratio)
    
    # Resize image
    img_resized = resize(img, (new_h, new_w), order=3, anti_aliasing=True, preserve_range=True).astype(img.dtype)
    
    # Calculate crop coordinates (center crop)
    start_x = (new_w - width) // 2
    start_y = (new_h - height) // 2
    
    # Crop the image
    img_cropped = img_resized[start_y:start_y+height, start_x:start_x+width]
    
    # Save the result
    iio.imwrite(output_path, img_cropped)

def process_gimp(input_path, output_path, width, height):
    # Create a temporary script file for GIMP
    script_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{str(uuid.uuid4())}_gimp_script.scm")
    
    with open(script_file, 'w') as f:
        f.write(f'''
(let* (
  (image (car (gimp-file-load RUN-NONINTERACTIVE "{input_path}" "{input_path}")))
  (drawable (car (gimp-image-get-active-layer image)))
  (orig-width (car (gimp-image-width image)))
  (orig-height (car (gimp-image-height image)))
  (ratio (max (/ {width} orig-width) (/ {height} orig-height)))
  (new-width (round (* orig-width ratio)))
  (new-height (round (* orig-height ratio)))
  (offx (round (/ (- new-width {width}) 2)))
  (offy (round (/ (- new-height {height}) 2)))
)
  (gimp-image-scale image new-width new-height)
  (gimp-image-crop image {width} {height} offx offy)
  (gimp-file-save RUN-NONINTERACTIVE image drawable "{output_path}" "{output_path}")
  (gimp-image-delete image)
)
(gimp-quit 0)
''')
    
    # Run GIMP in batch mode with the script
    cmd = [
        'gimp',
        '--no-interface',
        '--batch', f'(load-module "script-fu")' +
                  f'(load "{script_file}")',
        '--batch', '(gimp-quit 0)'
    ]
    subprocess.run(cmd, check=True)
    
    # Clean up the script file
    if os.path.exists(script_file):
        os.remove(script_file)

def process_skimage(input_path, output_path, width, height):
    # Resize and center crop using scikit-image
    from skimage import io, transform
    import numpy as np
    
    # Read image
    img = io.imread(input_path)
    
    # Calculate dimensions to maintain aspect ratio
    h, w = img.shape[:2]
    ratio = max(width/w, height/h)
    new_h, new_w = int(h * ratio), int(w * ratio)
    
    # Resize image
    img_resized = transform.resize(img, (new_h, new_w), order=3, anti_aliasing=True, preserve_range=True).astype(img.dtype)
    
    # Calculate crop coordinates (center crop)
    start_x = (new_w - width) // 2
    start_y = (new_h - height) // 2
    
    # Crop the image
    img_cropped = img_resized[start_y:start_y+height, start_x:start_x+width]
    
    # Save the result
    io.imsave(output_path, img_cropped)

def process_pyvips(input_path, output_path, width, height):
    # Resize and center crop using pyvips (Python binding for libvips)
    import pyvips
    
    # Load image
    image = pyvips.Image.new_from_file(input_path)
    
    # Calculate scale factor to maintain aspect ratio
    scale = max(width / image.width, height / image.height)
    
    # Resize image
    resized = image.resize(scale)
    
    # Calculate crop offsets (for center crop)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    
    # Crop image
    cropped = resized.crop(left, top, width, height)
    
    # Save image
    cropped.write_to_file(output_path)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return jsonify({"status": "cleanup successful"})
    except Exception as e:
        return jsonify({"error": f"Cleanup error: {str(e)}"}), 500

# Add some error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)