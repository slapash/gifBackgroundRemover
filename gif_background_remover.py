from flask import Flask, request, send_from_directory, Blueprint
import os
import tempfile
import shutil
from PIL import Image, ImageSequence
from rembg import remove
from werkzeug.utils import secure_filename

# Create a Blueprint
gif_bp = Blueprint('gif_bp', __name__)

def process_gif(input_path, temp_path):
    gif = Image.open(input_path)
    frames = ImageSequence.Iterator(gif)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    for count, frame in enumerate(frames):
        frame = frame.convert("RGBA")
        frame_output_path = os.path.join(temp_path, f"frame_{count:03d}.png")
        frame.save(frame_output_path, 'PNG')

        with open(frame_output_path, 'rb') as input_file:
            input_data = input_file.read()
        output_data = remove(input_data)

        with open(frame_output_path, 'wb') as output_file:
            output_file.write(output_data)

def get_average_gif_frame_duration(gif_path):
    with Image.open(gif_path) as gif:
        durations = [frame.info['duration'] for frame in ImageSequence.Iterator(gif)]
    return sum(durations) // len(durations) if durations else 100  # default to 100ms

def make_gif_from_folder(input_path, folder_path, output_gif_path):
    images = sorted(
        (os.path.join(folder_path, file_name) for file_name in os.listdir(folder_path) if file_name.lower().endswith('.png')),
        key=lambda x: os.path.getmtime(x)
    )
    frames = [Image.open(image) for image in images]
    average_duration = get_average_gif_frame_duration(input_path)

    frames[0].save(
        output_gif_path,
        format='GIF',
        append_images=frames[1:],
        save_all=True,
        duration=average_duration,
        loop=0,
        disposal=2 
    )

@gif_bp.route('/upload', methods=['POST'])
def upload_gif():
    if 'gif' not in request.files:
        return "No file part", 400
    file = request.files['gif']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.gif'):
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(input_path)
        process_gif(input_path, temp_dir)
        output_gif_path = os.path.join(temp_dir, 'output.gif')
        make_gif_from_folder(input_path, temp_dir, output_gif_path)
        response = send_from_directory(temp_dir, 'output.gif', as_attachment=True)

        # Cleanup delayed until after the request
        @response.call_on_close
        def cleanup_temp_dir():
            shutil.rmtree(temp_dir)
        
        return response

    return "Invalid file format", 400
