from PIL import Image, ImageSequence
from rembg import remove
import os

def process_gif(input_path, temp_path):
    # Open the original GIF
    gif = Image.open(input_path)
    frames = ImageSequence.Iterator(gif)

    # Ensure temp_path exists
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    # Process each frame to remove the background
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
    print(f"GIF saved at {output_gif_path}")


if __name__ == '__main__':
    input_gif_path = r"C:\Users\PC\Desktop\gifsuppr\giphy.gif"
    output_gif_path = r"C:\Users\PC\Desktop\gifsuppr\giphy_out.gif"
    temp_path = r'C:\Users\PC\Desktop\gifsuppr\temp'

    process_gif(input_gif_path, temp_path)
    make_gif_from_folder(input_gif_path, temp_path, output_gif_path)
