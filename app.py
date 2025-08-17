# app.py

import os
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import converter_backend as backend
import uuid

# --- Flask App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_super_secret_key_for_flash_messages'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_image():
    """Handles the image conversion logic."""
    # 1. Get the uploaded file
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        # Generate unique filenames to avoid conflicts
        unique_id = uuid.uuid4().hex
        original_filename = secure_filename(file.filename)
        input_filename = f"{unique_id}_{original_filename}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        file.save(input_path)

        # 2. Get form options
        mode = request.form.get('mode')
        output_path = None
        result_message = ""

        try:
            if mode == 'tnpc':
                output_filename = f"{unique_id}_tnpc.jpg"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)
                result_message = backend.convert_to_tnpc(input_path, output_path)
            else: # Standard mode
                target_format = request.form.get('format')
                output_filename = f"{unique_id}_converted.{target_format}"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)

                if target_format == 'ico':
                    sizes_str = request.form.get('ico_sizes', '16,32,48')
                    sizes = [int(s.strip()) for s in sizes_str.split(',')]
                    result_message = backend.convert_to_ico(input_path, output_path, sizes)
                else:
                    quality = int(request.form.get('quality', 90))
                    result_message = backend.convert_generic(input_path, output_path, quality)
            
            # 3. Send the converted file for download
            if "✅ Success" in result_message:
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=os.path.splitext(original_filename)[0] + os.path.splitext(output_path)[1]
                )
            else:
                flash(f"Conversion failed: {result_message}")
                return redirect(url_for('index'))

        finally:
            # 4. Clean up the temporary uploaded file
            if os.path.exists(input_path):
                os.remove(input_path)
            # We don't clean the output_path here because send_file needs it.
            # A more robust app would clean these files later.

if __name__ == '__main__':
    app.run(debug=True) # debug=True is for development, remove for production