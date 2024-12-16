import cv2
import os

def create_video_from_images(image_folder, output_video, fps=30):
    # Get all image file names from the directory
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".jpeg")]
    
    # Sort the images by filename to ensure the video frames are in order
    images.sort()

    # Check if there are images in the folder
    if len(images) == 0:
        print("No images found in the folder.")
        return

    # Read the first image to get the dimensions
    first_image_path = os.path.join(image_folder, images[0])
    frame = cv2.imread(first_image_path)
    
    # Get height, width, and layers (channels)
    height, width, _ = frame.shape

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # Add images to the video
    for image in images:
        image_path = os.path.join(image_folder, image)
        frame = cv2.imread(image_path)
        video.write(frame)

    # Release the VideoWriter object
    video.release()
    print(f"Video saved as {output_video}")

# Example usage
image_folder = 'images'
output_video = 'video.mp4'
create_video_from_images(image_folder, output_video, fps=3.2)
