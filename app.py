from flask import Flask, request, jsonify, send_file
import os
import subprocess
from werkzeug.utils import secure_filename
import uuid
import shutil
import tempfile
import logging
from PIL import Image, ImageColor
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
    
    # Get basic parameters
    width = request.form.get('width', 1000, type=int)
    height = request.form.get('height', 1500, type=int)
    output_format = request.form.get('format', 'jpg').lower()
    
    # Get additional parameters (avec valeurs par défaut selon XnConvert)
    resize_mode = request.form.get('resize_mode', 'fit')  # 'fit' correspond à "Ajuster"
    keep_ratio = request.form.get('keep_ratio', 'true').lower() == 'true'  # Conservation du ratio
    resampling = request.form.get('resampling', 'hanning')  # Méthode Hanning
    crop_position = request.form.get('crop_position', 'center')  # Position de recadrage centrée
    bg_color = request.form.get('bg_color', 'white')  # Couleur de fond blanche
    bg_alpha = request.form.get('bg_alpha', 255, type=int)  # Alpha 255
    
    # Create a unique filename to avoid collisions
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_input_{filename}")
    output_filename = f"{unique_id}_output.{output_format}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Log the parameters
    logger.info(f"Processing with {tool}: width={width}, height={height}, resize_mode={resize_mode}, "
                f"keep_ratio={keep_ratio}, resampling={resampling}, crop_position={crop_position}")
    
    # Save the input file
    file.save(input_path)
    
    try:
        # Process based on selected tool with all parameters
        if tool == 'imagemagick':
            process_imagemagick(input_path, output_path, width, height, resize_mode, keep_ratio, 
                               resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'graphicsmagick':
            process_graphicsmagick(input_path, output_path, width, height, resize_mode, keep_ratio, 
                                  resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'ffmpeg':
            process_ffmpeg(input_path, output_path, width, height, resize_mode, keep_ratio, 
                          resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'vips':
            process_vips(input_path, output_path, width, height, resize_mode, keep_ratio, 
                        resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'pillow':
            process_pillow(input_path, output_path, width, height, resize_mode, keep_ratio, 
                          resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'nconvert':
            process_nconvert(input_path, output_path, width, height, resize_mode, keep_ratio, 
                            resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'opencv':
            process_opencv(input_path, output_path, width, height, resize_mode, keep_ratio, 
                          resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'imageio':
            process_imageio(input_path, output_path, width, height, resize_mode, keep_ratio, 
                           resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'gimp':
            process_gimp(input_path, output_path, width, height, resize_mode, keep_ratio, 
                        resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'skimage':
            process_skimage(input_path, output_path, width, height, resize_mode, keep_ratio, 
                           resampling, crop_position, bg_color, bg_alpha)
        elif tool == 'pyvips':
            process_pyvips(input_path, output_path, width, height, resize_mode, keep_ratio, 
                          resampling, crop_position, bg_color, bg_alpha)
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

# Les fonctions de traitement pour chaque outil
def process_imagemagick(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                       resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    # Map resampling methods to ImageMagick filter
    filter_map = {
        'nearest': 'Point',
        'bilinear': 'Bilinear',
        'bicubic': 'Cubic',
        'lanczos': 'Lanczos',
        'hanning': 'Hanning'
    }
    filter_type = filter_map.get(resampling.lower(), 'Lanczos')
    
    # Build the command based on resize_mode
    cmd = ['convert', input_path]
    
    if resize_mode == 'fit' and keep_ratio:
        # Fit within dimensions and keep ratio
        cmd.extend([
            '-filter', filter_type,
            '-resize', f'{width}x{height}',
            '-background', bg_color,
            '-alpha', 'remove',
            '-alpha', 'off',
            '-gravity', crop_position,
            '-extent', f'{width}x{height}'
        ])
    elif resize_mode == 'stretch':
        # Stretch to fit exactly
        cmd.extend([
            '-filter', filter_type,
            '-resize', f'{width}x{height}!',
        ])
    else:
        # Default to fill mode (crop)
        cmd.extend([
            '-filter', filter_type,
            '-resize', f'{width}x{height}^',
            '-gravity', crop_position,
            '-extent', f'{width}x{height}'
        ])
    
    # Add output path
    cmd.append(output_path)
    
    # Run the command
    subprocess.run(cmd, check=True)

def process_graphicsmagick(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                          resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    # Similar to ImageMagick but with gm prefix
    filter_map = {
        'nearest': 'Point',
        'bilinear': 'Bilinear',
        'bicubic': 'Cubic',
        'lanczos': 'Lanczos',
        'hanning': 'Hanning'
    }
    filter_type = filter_map.get(resampling.lower(), 'Lanczos')
    
    cmd = ['gm', 'convert', input_path]
    
    if resize_mode == 'fit' and keep_ratio:
        cmd.extend([
            '-filter', filter_type,
            '-resize', f'{width}x{height}',
            '-background', bg_color,
            '-gravity', crop_position,
            '-extent', f'{width}x{height}'
        ])
    elif resize_mode == 'stretch':
        cmd.extend([
            '-filter', filter_type,
            '-resize', f'{width}x{height}!'
        ])
    else:
        cmd.extend([
            '-filter', filter_type,
            '-resize', f'{width}x{height}^',
            '-gravity', crop_position,
            '-extent', f'{width}x{height}'
        ])
    
    cmd.append(output_path)
    subprocess.run(cmd, check=True)

def process_ffmpeg(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                  resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    # Map resampling to ffmpeg flags
    filter_map = {
        'nearest': 'neighbor',
        'bilinear': 'bilinear',
        'bicubic': 'bicubic',
        'lanczos': 'lanczos',
        'hanning': 'hanning'  # FFmpeg supporte hanning
    }
    filter_type = filter_map.get(resampling.lower(), 'lanczos')
    
    # Map crop position to ffmpeg parameters
    crop_x = "(iw-ow)/2"
    crop_y = "(ih-oh)/2"
    
    if crop_position == 'top':
        crop_y = "0"
    elif crop_position == 'bottom':
        crop_y = "ih-oh"
    elif crop_position == 'left':
        crop_x = "0"
    elif crop_position == 'right':
        crop_x = "iw-ow"
    
    # Build the ffmpeg command based on resize_mode
    if resize_mode == 'fit' and keep_ratio:
        # Utiliser pad pour ajouter des bordures
        bg_hex = bg_color if bg_color.startswith('#') else 'white'
        if bg_color == 'white':
            bg_hex = 'white'
        elif bg_color == 'black':
            bg_hex = 'black'
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease:flags={filter_type},'
                   f'pad={width}:{height}:{crop_x}:{crop_y}:color={bg_hex}',
            '-y', output_path
        ]
    elif resize_mode == 'stretch':
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', f'scale={width}:{height}:flags={filter_type}',
            '-y', output_path
        ]
    else:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=increase:flags={filter_type},'
                   f'crop={width}:{height}:{crop_x}:{crop_y}',
            '-y', output_path
        ]
    
    subprocess.run(cmd, check=True)

def process_vips(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    # VIPS command-line options
    if resize_mode == 'fit' and keep_ratio:
        cmd = [
            'vips', 'thumbnail', input_path, output_path,
            str(width), '--height', str(height),
            '--size', 'down',
            '--background', bg_color
        ]
    elif resize_mode == 'stretch':
        cmd = [
            'vips', 'thumbnail', input_path, output_path,
            str(width), '--height', str(height),
            '--size', 'force'
        ]
    else:
        cmd = [
            'vips', 'thumbnail', input_path, output_path,
            str(width), '--height', str(height),
            '--size', 'both',
            '--crop', crop_position
        ]
    
    subprocess.run(cmd, check=True)

def process_pillow(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                  resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    # Open image with Pillow
    img = Image.open(input_path)
    
    # Map resampling methods to Pillow constants
    resampling_methods = {
        'nearest': Image.NEAREST,
        'bilinear': Image.BILINEAR,
        'bicubic': Image.BICUBIC,
        'lanczos': Image.LANCZOS,
        'hanning': Image.LANCZOS  # Pillow n'a pas de méthode Hanning, utiliser Lanczos
    }
    resample = resampling_methods.get(resampling.lower(), Image.LANCZOS)
    
    # Handle background color
    bg = bg_color
    if isinstance(bg_color, str):
        try:
            # Convert string color name to RGB
            bg = ImageColor.getcolor(bg_color, 'RGBA')
            bg = (*bg[:3], bg_alpha)
        except:
            # Fallback to white
            bg = (255, 255, 255, bg_alpha)
    
    # Process resize based on mode
    if resize_mode == 'fit' and keep_ratio:
        # Calculate dimensions to maintain aspect ratio
        img_width, img_height = img.size
        ratio = min(width/img_width, height/img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        # Resize image to fit within the target dimensions
        img = img.resize(new_size, resample)
        
        # Create new image with background color
        new_img = Image.new('RGBA', (width, height), bg)
        
        # Calculate position based on crop_position
        if crop_position == 'center':
            paste_x = (width - new_size[0]) // 2
            paste_y = (height - new_size[1]) // 2
        elif crop_position == 'top':
            paste_x = (width - new_size[0]) // 2
            paste_y = 0
        elif crop_position == 'bottom':
            paste_x = (width - new_size[0]) // 2
            paste_y = height - new_size[1]
        elif crop_position == 'left':
            paste_x = 0
            paste_y = (height - new_size[1]) // 2
        elif crop_position == 'right':
            paste_x = width - new_size[0]
            paste_y = (height - new_size[1]) // 2
        else:  # default to center
            paste_x = (width - new_size[0]) // 2
            paste_y = (height - new_size[1]) // 2
        
        # Paste resized image onto background
        if img.mode == 'RGBA':
            new_img.paste(img, (paste_x, paste_y), img)
        else:
            new_img.paste(img, (paste_x, paste_y))
        img = new_img
    
    elif resize_mode == 'stretch':
        # Stretch to fit dimensions without keeping ratio
        img = img.resize((width, height), resample)
    
    else:  # Default to crop (fill mode)
        # Calculate dimensions to maintain aspect ratio
        img_width, img_height = img.size
        ratio = max(width/img_width, height/img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        # Resize image to cover the target dimensions
        img = img.resize(new_size, resample)
        
        # Calculate crop box (center crop by default)
        if crop_position == 'center':
            left = (new_size[0] - width) / 2
            top = (new_size[1] - height) / 2
        elif crop_position == 'top':
            left = (new_size[0] - width) / 2
            top = 0
        elif crop_position == 'bottom':
            left = (new_size[0] - width) / 2
            top = new_size[1] - height
        elif crop_position == 'left':
            left = 0
            top = (new_size[1] - height) / 2
        elif crop_position == 'right':
            left = new_size[0] - width
            top = (new_size[1] - height) / 2
        else:  # default to center
            left = (new_size[0] - width) / 2
            top = (new_size[1] - height) / 2
            
        right = left + width
        bottom = top + height
        img = img.crop((int(left), int(top), int(right), int(bottom)))
    
    # Convert to RGB if saving as JPG
    if output_path.lower().endswith(('.jpg', '.jpeg')):
        if img.mode == 'RGBA':
            img = img.convert('RGB')
    
    # Save the result
    img.save(output_path)

def process_nconvert(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                    resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    # Map resampling methods
    filter_map = {
        'nearest': 'nearest',
        'bilinear': 'bilinear',
        'bicubic': 'bicubic',
        'lanczos': 'lanczos',
        'hanning': 'hanning'
    }
    filter_type = filter_map.get(resampling.lower(), 'lanczos')
    
    # Map crop position
    position_map = {
        'center': 'center',
        'top': 'top',
        'bottom': 'bottom',
        'left': 'left',
        'right': 'right'
    }
    position = position_map.get(crop_position, 'center')
    
    # Base command
    cmd = ['xnconvert', '-silent']
    
    # Configure resize/crop based on mode
    if resize_mode == 'fit' and keep_ratio:
        cmd.extend([
            '-resize', str(width), str(height),
            '-ratio', 'yes',
            '-rtype', filter_type,
            '-canvas', str(width), str(height),
            '-ctype', position,
            '-bgcolor', bg_color
        ])
    elif resize_mode == 'stretch':
        cmd.extend([
            '-resize', str(width), str(height),
            '-ratio', 'no',
            '-rtype', filter_type
        ])
    else:
        cmd.extend([
            '-resize', str(width), str(height),
            '-ratio', 'grow',
            '-rtype', filter_type,
            '-crop', str(width), str(height), position
        ])
    
    # Add input and output
    cmd.extend([
        '-out', output_path.split('.')[-1],
        '-o', output_path,
        input_path
    ])
    
    subprocess.run(cmd, check=True)

def process_opencv(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                  resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    # Read the image
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    # Check if image has alpha channel
    has_alpha = img.shape[2] == 4 if len(img.shape) == 3 else False
    
    # Map resampling methods to OpenCV interpolation
    interp_map = {
        'nearest': cv2.INTER_NEAREST,
        'bilinear': cv2.INTER_LINEAR,
        'bicubic': cv2.INTER_CUBIC,
        'lanczos': cv2.INTER_LANCZOS4,
        'hanning': cv2.INTER_LINEAR  # OpenCV doesn't have Hanning
    }
    interpolation = interp_map.get(resampling.lower(), cv2.INTER_LANCZOS4)
    
    # Map background color
    if isinstance(bg_color, str):
        if bg_color == 'white':
            bg = [255, 255, 255]
        elif bg_color == 'black':
            bg = [0, 0, 0]
        else:
            # Try to parse hex color
            try:
                if bg_color.startswith('#'):
                    bg = [int(bg_color[i:i+2], 16) for i in (1, 3, 5)]
                else:
                    bg = [255, 255, 255]  # Default to white
            except:
                bg = [255, 255, 255]  # Default to white
    else:
        bg = [255, 255, 255]  # Default to white
    
    # Add alpha channel if specified
    if has_alpha:
        bg.append(bg_alpha)
    
    # Process the image based on resize mode
    if resize_mode == 'fit' and keep_ratio:
        # Calculate dimensions to maintain aspect ratio
        h, w = img.shape[:2]
        ratio = min(width/w, height/h)
        new_size = (int(w * ratio), int(h * ratio))
        
        # Resize image to fit within the target dimensions
        img_resized = cv2.resize(img, new_size, interpolation=interpolation)
        
        # Create new image with background color
        if has_alpha:
            # Create BGRA image
            new_img = np.full((height, width, 4), bg, dtype=np.uint8)
        else:
            # Create BGR image
            new_img = np.full((height, width, 3), bg[:3], dtype=np.uint8)
        
        # Calculate position based on crop_position
        if crop_position == 'center':
            start_x = (width - new_size[0]) // 2
            start_y = (height - new_size[1]) // 2
        elif crop_position == 'top':
            start_x = (width - new_size[0]) // 2
            start_y = 0
        elif crop_position == 'bottom':
            start_x = (width - new_size[0]) // 2
            start_y = height - new_size[1]
        elif crop_position == 'left':
            start_x = 0
            start_y = (height - new_size[1]) // 2
        elif crop_position == 'right':
            start_x = width - new_size[0]
            start_y = (height - new_size[1]) // 2
        else:
            start_x = (width - new_size[0]) // 2
            start_y = (height - new_size[1]) // 2
        
        # Paste resized image onto background
        end_x = start_x + new_size[0]
        end_y = start_y + new_size[1]
        
        if has_alpha:
            # Alpha blending
            alpha = img_resized[:, :, 3] / 255.0
            for c in range(3):
                new_img[start_y:end_y, start_x:end_x, c] = (
                    img_resized[:, :, c] * alpha + 
                    new_img[start_y:end_y, start_x:end_x, c] * (1 - alpha)
                ).astype(np.uint8)
            new_img[start_y:end_y, start_x:end_x, 3] = img_resized[:, :, 3]
        else:
            new_img[start_y:end_y, start_x:end_x] = img_resized
        
        img_result = new_img
    
    elif resize_mode == 'stretch':
        # Stretch to fit dimensions without keeping ratio
        img_result = cv2.resize(img, (width, height), interpolation=interpolation)
    
    else:  # Default to crop (fill mode)
        # Calculate dimensions to maintain aspect ratio
        h, w = img.shape[:2]
        ratio = max(width/w, height/h)
        new_size = (int(w * ratio), int(h * ratio))
        
        # Resize image to cover the target dimensions
        img_resized = cv2.resize(img, new_size, interpolation=interpolation)
        
        # Calculate crop coordinates
        if crop_position == 'center':
            start_x = (new_size[0] - width) // 2
            start_y = (new_size[1] - height) // 2
        elif crop_position == 'top':
            start_x = (new_size[0] - width) // 2
            start_y = 0
        elif crop_position == 'bottom':
            start_x = (new_size[0] - width) // 2
            start_y = new_size[1] - height
        elif crop_position == 'left':
            start_x = 0
            start_y = (new_size[1] - height) // 2
        elif crop_position == 'right':
            start_x = new_size[0] - width
            start_y = (new_size[1] - height) // 2
        else:
            start_x = (new_size[0] - width) // 2
            start_y = (new_size[1] - height) // 2
        
        # Crop the image
        end_x = start_x + width
        end_y = start_y + height
        img_result = img_resized[start_y:end_y, start_x:end_x]
    
    # Save the result
    if output_path.lower().endswith(('.jpg', '.jpeg')) and has_alpha:
        # Convert BGRA to BGR for JPG
        img_result = cv2.cvtColor(img_result, cv2.COLOR_BGRA2BGR)
    
    cv2.imwrite(output_path, img_result)

def process_imageio(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                   resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    import imageio.v3 as iio
    from skimage.transform import resize
    import numpy as np
    
    # Read image
    img = iio.imread(input_path)
    
    # Check if image has alpha channel
    has_alpha = img.shape[2] == 4 if len(img.shape) == 3 else False
    
    # Process the image based on resize mode
    if resize_mode == 'fit' and keep_ratio:
        # Calculate dimensions to maintain aspect ratio
        h, w = img.shape[:2]
        ratio = min(width/w, height/h)
        new_h, new_w = int(h * ratio), int(w * ratio)
        
        # Resize image
        img_resized = resize(img, (new_h, new_w), order=3, anti_aliasing=True, 
                            preserve_range=True).astype(img.dtype)
        
        # Parse background color
        if isinstance(bg_color, str):
            if bg_color == 'white':
                bg = np.array([255, 255, 255])
            elif bg_color == 'black':
                bg = np.array([0, 0, 0])
            else:
                bg = np.array([255, 255, 255])
        else:
            bg = np.array([255, 255, 255])
        
        # Create new canvas with background color
        if has_alpha:
            canvas = np.zeros((height, width, 4), dtype=img.dtype)
            canvas[:, :, :3] = bg
            canvas[:, :, 3] = bg_alpha
        else:
            canvas = np.zeros((height, width, 3), dtype=img.dtype)
            canvas[:, :, :] = bg
        
        # Calculate position based on crop_position
        if crop_position == 'center':
            start_x = (width - new_w) // 2
            start_y = (height - new_h) // 2
        elif crop_position == 'top':
            start_x = (width - new_w) // 2
            start_y = 0
        elif crop_position == 'bottom':
            start_x = (width - new_w) // 2
            start_y = height - new_h
        elif crop_position == 'left':
            start_x = 0
            start_y = (height - new_h) // 2
        elif crop_position == 'right':
            start_x = width - new_w
            start_y = (height - new_h) // 2
        else:
            start_x = (width - new_w) // 2
            start_y = (height - new_h) // 2
        
        # Place resized image on canvas
        end_x = start_x + new_w
        end_y = start_y + new_h
        
        if has_alpha and img_resized.shape[2] == 4:
# Alpha compositing
            alpha = img_resized[:, :, 3:4] / 255.0
            canvas[start_y:end_y, start_x:end_x, :3] = (
                img_resized[:, :, :3] * alpha + 
                canvas[start_y:end_y, start_x:end_x, :3] * (1 - alpha)
            )
            canvas[start_y:end_y, start_x:end_x, 3] = img_resized[:, :, 3]
        else:
            canvas[start_y:end_y, start_x:end_x] = img_resized
        
        img_result = canvas
    
    elif resize_mode == 'stretch':
        # Stretch to fit dimensions without keeping ratio
        img_result = resize(img, (height, width), order=3, anti_aliasing=True, 
                           preserve_range=True).astype(img.dtype)
    
    else:  # Default to crop (fill mode)
        # Calculate dimensions to maintain aspect ratio
        h, w = img.shape[:2]
        ratio = max(width/w, height/h)
        new_h, new_w = int(h * ratio), int(w * ratio)
        
        # Resize image
        img_resized = resize(img, (new_h, new_w), order=3, anti_aliasing=True, 
                            preserve_range=True).astype(img.dtype)
        
        # Calculate crop coordinates
        if crop_position == 'center':
            start_x = (new_w - width) // 2
            start_y = (new_h - height) // 2
        elif crop_position == 'top':
            start_x = (new_w - width) // 2
            start_y = 0
        elif crop_position == 'bottom':
            start_x = (new_w - width) // 2
            start_y = new_h - height
        elif crop_position == 'left':
            start_x = 0
            start_y = (new_h - height) // 2
        elif crop_position == 'right':
            start_x = new_w - width
            start_y = (new_h - height) // 2
        else:
            start_x = (new_w - width) // 2
            start_y = (new_h - height) // 2
        
        # Crop the image
        end_x = start_x + width
        end_y = start_y + height
        img_result = img_resized[start_y:end_y, start_x:end_x]
    
    # Save the result (convert to uint8 if necessary)
    if img_result.dtype != np.uint8:
        img_result = np.clip(img_result, 0, 255).astype(np.uint8)
    
    iio.imwrite(output_path, img_result)

def process_gimp(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    # Create a temporary script file for GIMP
    script_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{str(uuid.uuid4())}_gimp_script.scm")
    
    # Convert position to GIMP position
    position_map = {
        'center': 2,
        'top': 1,
        'bottom': 3,
        'left': 4,
        'right': 5
    }
    position = position_map.get(crop_position, 2)
    
    # Generate GIMP script based on resize mode
    if resize_mode == 'fit' and keep_ratio:
        script = f'''
(let* (
  (image (car (gimp-file-load RUN-NONINTERACTIVE "{input_path}" "{input_path}")))
  (drawable (car (gimp-image-get-active-layer image)))
  (orig-width (car (gimp-image-width image)))
  (orig-height (car (gimp-image-height image)))
  (ratio (min (/ {width} orig-width) (/ {height} orig-height)))
  (new-width (round (* orig-width ratio)))
  (new-height (round (* orig-height ratio)))
)
  (gimp-image-scale image new-width new-height)
  (gimp-image-resize image {width} {height} (/ (- {width} new-width) 2) (/ (- {height} new-height) 2))
  (gimp-context-set-background '(255 255 255))
  (gimp-layer-resize drawable {width} {height} 0 0)
  (gimp-drawable-fill (car (gimp-image-get-active-layer image)) BACKGROUND-FILL)
  (gimp-layer-set-offsets drawable (/ (- {width} new-width) 2) (/ (- {height} new-height) 2))
  (gimp-file-save RUN-NONINTERACTIVE image drawable "{output_path}" "{output_path}")
  (gimp-image-delete image)
)
(gimp-quit 0)
'''
    elif resize_mode == 'stretch':
        script = f'''
(let* (
  (image (car (gimp-file-load RUN-NONINTERACTIVE "{input_path}" "{input_path}")))
  (drawable (car (gimp-image-get-active-layer image)))
)
  (gimp-image-scale image {width} {height})
  (gimp-file-save RUN-NONINTERACTIVE image drawable "{output_path}" "{output_path}")
  (gimp-image-delete image)
)
(gimp-quit 0)
'''
    else:  # Default to crop (fill mode)
        script = f'''
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
'''
    
    # Write script to file
    with open(script_file, 'w') as f:
        f.write(script)
    
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

def process_skimage(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                   resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    from skimage import io, transform
    import numpy as np
    
    # Read image
    img = io.imread(input_path)
    
    # Check if image has alpha channel
    has_alpha = img.shape[2] == 4 if len(img.shape) == 3 else False
    
    # Map resampling mode
    order_map = {
        'nearest': 0,
        'bilinear': 1,
        'bicubic': 3,
        'lanczos': 1,  # Not directly supported, use bilinear
        'hanning': 1   # Not directly supported, use bilinear
    }
    order = order_map.get(resampling.lower(), 1)
    
    # Process the image based on resize mode
    if resize_mode == 'fit' and keep_ratio:
        # Calculate dimensions to maintain aspect ratio
        h, w = img.shape[:2]
        ratio = min(width/w, height/h)
        new_h, new_w = int(h * ratio), int(w * ratio)
        
        # Resize image
        img_resized = transform.resize(img, (new_h, new_w), order=order, 
                                      anti_aliasing=True, preserve_range=True).astype(img.dtype)
        
        # Parse background color
        if isinstance(bg_color, str):
            if bg_color == 'white':
                bg = np.array([255, 255, 255])
            elif bg_color == 'black':
                bg = np.array([0, 0, 0])
            else:
                bg = np.array([255, 255, 255])
        else:
            bg = np.array([255, 255, 255])
        
        # Create new canvas with background color
        if has_alpha:
            canvas = np.zeros((height, width, 4), dtype=img.dtype)
            canvas[:, :, :3] = bg
            canvas[:, :, 3] = bg_alpha
        else:
            canvas = np.zeros((height, width, 3), dtype=img.dtype)
            canvas[:, :, :] = bg
        
        # Calculate position based on crop_position
        if crop_position == 'center':
            start_x = (width - new_w) // 2
            start_y = (height - new_h) // 2
        elif crop_position == 'top':
            start_x = (width - new_w) // 2
            start_y = 0
        elif crop_position == 'bottom':
            start_x = (width - new_w) // 2
            start_y = height - new_h
        elif crop_position == 'left':
            start_x = 0
            start_y = (height - new_h) // 2
        elif crop_position == 'right':
            start_x = width - new_w
            start_y = (height - new_h) // 2
        else:
            start_x = (width - new_w) // 2
            start_y = (height - new_h) // 2
        
        # Place resized image on canvas
        end_x = start_x + new_w
        end_y = start_y + new_h
        
        if has_alpha and img_resized.shape[2] == 4:
            # Alpha compositing
            alpha = img_resized[:, :, 3:4] / 255.0
            canvas[start_y:end_y, start_x:end_x, :3] = (
                img_resized[:, :, :3] * alpha + 
                canvas[start_y:end_y, start_x:end_x, :3] * (1 - alpha)
            )
            canvas[start_y:end_y, start_x:end_x, 3] = img_resized[:, :, 3]
        else:
            canvas[start_y:end_y, start_x:end_x] = img_resized
        
        img_result = canvas
    
    elif resize_mode == 'stretch':
        # Stretch to fit dimensions without keeping ratio
        img_result = transform.resize(img, (height, width), order=order, 
                                     anti_aliasing=True, preserve_range=True).astype(img.dtype)
    
    else:  # Default to crop (fill mode)
        # Calculate dimensions to maintain aspect ratio
        h, w = img.shape[:2]
        ratio = max(width/w, height/h)
        new_h, new_w = int(h * ratio), int(w * ratio)
        
        # Resize image
        img_resized = transform.resize(img, (new_h, new_w), order=order, 
                                      anti_aliasing=True, preserve_range=True).astype(img.dtype)
        
        # Calculate crop coordinates
        if crop_position == 'center':
            start_x = (new_w - width) // 2
            start_y = (new_h - height) // 2
        elif crop_position == 'top':
            start_x = (new_w - width) // 2
            start_y = 0
        elif crop_position == 'bottom':
            start_x = (new_w - width) // 2
            start_y = new_h - height
        elif crop_position == 'left':
            start_x = 0
            start_y = (new_h - height) // 2
        elif crop_position == 'right':
            start_x = new_w - width
            start_y = (new_h - height) // 2
        else:
            start_x = (new_w - width) // 2
            start_y = (new_h - height) // 2
        
        # Crop the image
        end_x = start_x + width
        end_y = start_y + height
        img_result = img_resized[start_y:end_y, start_x:end_x]
    
    # Save the result (convert to uint8 if necessary)
    if img_result.dtype != np.uint8:
        img_result = np.clip(img_result, 0, 255).astype(np.uint8)
    
    io.imsave(output_path, img_result)

def process_pyvips(input_path, output_path, width, height, resize_mode='fit', keep_ratio=True, 
                  resampling='hanning', crop_position='center', bg_color='white', bg_alpha=255):
    import pyvips
    
    # Map resampling method to pyvips kernel
    kernel_map = {
        'nearest': 'nearest',
        'bilinear': 'linear',
        'bicubic': 'cubic',
        'lanczos': 'lanczos3',
        'hanning': 'linear'  # Not directly supported
    }
    kernel = kernel_map.get(resampling.lower(), 'lanczos3')
    
    # Load image
    image = pyvips.Image.new_from_file(input_path)
    
    # Process based on resize mode
    if resize_mode == 'fit' and keep_ratio:
        # Calculate scale to fit within dimensions
        scale_x = width / image.width
        scale_y = height / image.height
        scale = min(scale_x, scale_y)
        
        # Resize the image
        resized = image.resize(scale, kernel=kernel)
        
        # Create a new image with background color
        # Convert bg_color to pyvips format
        if isinstance(bg_color, str):
            if bg_color == 'white':
                bg = [255, 255, 255]
            elif bg_color == 'black':
                bg = [0, 0, 0]
            else:
                # Try to parse hex color (not fully implemented)
                bg = [255, 255, 255]
        else:
            bg = [255, 255, 255]
        
        # Create background image
        background = pyvips.Image.new_from_array(
            [[bg[0], bg[1], bg[2]]], scale=1.0
        ).resize(width, height)
        
        # Calculate position
        left = (width - resized.width) // 2
        top = (height - resized.height) // 2
        
        if crop_position == 'top':
            top = 0
        elif crop_position == 'bottom':
            top = height - resized.height
        elif crop_position == 'left':
            left = 0
        elif crop_position == 'right':
            left = width - resized.width
        
        # Embed resized image in background
        result = background.embed(left, top, resized.width, resized.height, extend="copy")
        result = result.composite(resized, "over", x=left, y=top)
    
    elif resize_mode == 'stretch':
        # Stretch to fit without keeping ratio
        result = image.resize(width / image.width, kernel=kernel, vscale=height / image.height)
    
    else:  # Default to crop (fill mode)
        # Calculate scale to cover dimensions
        scale_x = width / image.width
        scale_y = height / image.height
        scale = max(scale_x, scale_y)
        
        # Resize image
        resized = image.resize(scale, kernel=kernel)
        
        # Calculate crop position
        left = (resized.width - width) // 2
        top = (resized.height - height) // 2
        
        if crop_position == 'top':
            top = 0
        elif crop_position == 'bottom':
            top = resized.height - height
        elif crop_position == 'left':
            left = 0
        elif crop_position == 'right':
            left = resized.width - width
        
        # Crop image
        result = resized.crop(left, top, width, height)
    
    # Save image
    result.write_to_file(output_path)

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