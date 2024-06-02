import imageio
from PIL import Image

# Open the video file
video_reader = imageio.get_reader('output.h264', 'ffmpeg')

# Specify the frame number you want to capture
frame_number = 0

# Read the frame
frame = video_reader.get_data(frame_number)

# Convert the frame (numpy array) to an image
image = Image.fromarray(frame)

# Save the image as JPEG
image.save('output.jpg')

print(f"Frame {frame_number} saved as output.jpg")
