#!/usr/bin/env python3

import cv2, datetime, os, re, time

from picamera2 import Picamera2

def create_video_from_images():
    fps = 12
    start_time = time.time()

    # Get all image file names from the directory
    images = [img for img in os.listdir('images') if img.endswith(".jpg") or img.endswith(".jpeg")]
    
    # Sort the images by filename to ensure the video frames are in order
    images.sort()

    # Check if there are images in the folder
    if len(images) == 0:
        print("No images found in the folder.")
        return

    # Read the first image to get the dimensions
    first_image_path = os.path.join('images', images[0])
    frame = cv2.imread(first_image_path)
    
    # Get height, width, and layers (channels)
    height, width, _ = frame.shape

    # Create the file name
    current_time = datetime.datetime.now()
    output_video = 'videos/' + current_time.strftime("%m_%d_%y__%I_%M%p") + '.mp4'

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # Add images to the video
    for image in images:
        image_path = os.path.join('images', image)
        frame = cv2.imread(image_path)
        video.write(frame)

    # Release the VideoWriter object
    video.release()
    print('Video saved as %s in %.1f seconds' % (output_video, time.time() - start_time))

def main():
    fps = 12
    interval = 1/fps
    image_count = 0

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080)}))
    picam2.start()

    for ii in range(120):
        start_time = time.time()

        # Capture a frame from camera
        frame = picam2.capture_array()

        # Attach FPS counter to the text and boxes
        frame_height, frame_width, _ = frame.shape
        text_x = 10           # Margin from the left edge
        color = (0, 255, 0)   # White color for the text (B, G, R)
        font_scale = 1
        font = cv2.FONT_HERSHEY_DUPLEX

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%m/%d/%y %I:%M%p").lstrip('0')
        time_string = re.sub(' 0', ' ', time_string)

        # Add the time string to the frame
        text_y = frame_height - 40  # Margin from the bottom edge
        cv2.putText(frame, time_string, (text_x, text_y), font, font_scale, color, 1)

        # Write the frame to disk
        file_name = 'images/image_'
        if image_count < 100:
            file_name += '0'
        if image_count < 10:
            file_name += '0'
        file_name = '%s%d' % (file_name, image_count)
        file_name += '.jpg'
        cv2.imwrite(file_name, frame)
        image_count += 1

        # Go to sleep
        elapsed_time = time.time() - start_time
        sleep_time = max(0, interval - elapsed_time)
        if sleep_time == 0:
            print('0 sleep time')
        time.sleep(sleep_time)

    # Convert the images to video
    create_video_from_images()
    os.system('rm -f images/*')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()

