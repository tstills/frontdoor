#!/usr/bin/env python

import cv2, datetime, face_recognition, numpy, os, pickle, re, time

from picamera2 import Picamera2
from RPi import GPIO

MOTION_DETECT_PIN_N = 22

cv_scaler = 4 # this has to be a whole number

def process_frame(frame, known_face_encodings, known_face_names):

    # Resize the frame using cv_scaler to increase performance (less pixels processed, less time spent)
    resized_frame = cv2.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))

    # Convert the image from BGR to RGB colour space, the facial recognition library uses RGB, OpenCV uses BGR
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model='large')

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = numpy.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        face_names.append(name)

    return frame, face_locations, face_encodings, face_names

def draw_results(frame, face_locations, face_names):
    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled
        top *= cv_scaler
        right *= cv_scaler
        bottom *= cv_scaler
        left *= cv_scaler

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left -3, top - 35), (right+3, top), (244, 42, 3), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)

    return frame

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

def main():
    # Set up the GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTION_DETECT_PIN_N, GPIO.IN)

    # Load pre-trained face encodings
    print("[INFO] loading encodings...")
    with open("encodings.pickle", "rb") as f:
        data = pickle.loads(f.read())
    known_face_encodings = data["encodings"]
    known_face_names = data["names"]

    # Initialize the camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080)}))
    picam2.start()

    # Poll the motion detect once a second
    print('Starting')
    while True:
        if not GPIO.input(MOTION_DETECT_PIN_N):
            print("Motion detected.")
            start_time = time.time()
            print('Start time: %.1f' % start_time)
            os.system('rm -f images/*')
            frame_count = 0
            image_count = 0

            # Do facial recognition and record as long as motion is detected
            while not GPIO.input(MOTION_DETECT_PIN_N):

                # Capture a frame from camera
                frame = picam2.capture_array()
                frame_count += 1

                # Process the frame with the function
                processed_frame, face_locations, face_encodings, face_names = \
                        process_frame(frame, known_face_encodings, known_face_names)

                # Get the text and boxes to be drawn based on the processed frame
                display_frame = draw_results(processed_frame, face_locations, face_names)

                # Attach FPS counter to the text and boxes
                frame_height, frame_width, _ = display_frame.shape
                text_x = 10           # Margin from the left edge
                color = (0, 255, 0)   # White color for the text (B, G, R)
                font_scale = 1
                font = cv2.FONT_HERSHEY_DUPLEX

                # Get the current time
                current_time = datetime.datetime.now()
                time_string = current_time.strftime("%m/%d/%y %I:%M%p").lstrip('0')
                time_string = re.sub(' 0', ' ', time_string)

                # Add the time string to the frame
                text_y = frame_height - 10  # Margin from the bottom edge
                cv2.putText(display_frame, time_string, (text_x, text_y), font, font_scale, color, 1)

                # Display everything over the video feed.
                cv2.imshow('Video', display_frame)

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

                # Break the loop and stop the script if 'q' is pressed
                if cv2.waitKey(1) == ord("q"):
                    break

            # Convert the images to a video
            now = time.time()
            print('End time: %.1f' % now)
            print('Frame count: %d' % frame_count)
            current_time = datetime.datetime.now()
            time_string = current_time.strftime("%Y-%m-%d_%H:%M")
            file_name = 'videos/' + time_string + '.mp4'
            fps = frame_count / (now - start_time)
            print('%.1f fps' % fps)
            create_video_from_images('images', file_name, fps)
            print('Process time: %.1fs' % (time.time() - now))

        else:
            time.sleep(1)

    # By breaking the loop we run this code here which closes everything
    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print
