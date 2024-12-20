#!/usr/bin/env python

import face_recognition
import cv2
import numpy as np
from picamera2 import Picamera2
import time
import pickle
import datetime
import re

cv_scaler = 4 # this has to be a whole number
frame_count = 0
start_time = time.time()

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
        best_match_index = np.argmin(face_distances)
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

def calculate_fps():
    global frame_count, start_time
    fps = 0
    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 1:
        fps = frame_count / elapsed_time
        frame_count = 0
        start_time = time.time()
    return fps

def main():
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

    while True:
        # Capture a frame from camera
        frame = picam2.capture_array()

        # Process the frame with the function
        processed_frame, face_locations, face_encodings, face_names = \
                process_frame(frame, known_face_encodings, known_face_names)

        # Get the text and boxes to be drawn based on the processed frame
        display_frame = draw_results(processed_frame, face_locations, face_names)

        # Calculate and update FPS
        current_fps = calculate_fps()

        # Attach FPS counter to the text and boxes
        frame_height, frame_width, _ = display_frame.shape
        text_x = 10                 # Margin from the left edge
        text_y = frame_height - 10  # Margin from the bottom edge
        color = (0, 255, 0)  # White color for the text (B, G, R)
        font_scale = 1
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(display_frame, f"FPS: {current_fps:.1f}", (text_x, text_y), 
                    font, font_scale, color, 1)

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%m/%d/%y %I:%M%p").lstrip('0')
        time_string = re.sub(' 0', ' ', time_string)

        # Add the time string to the frame
        text_y = frame_height - 40  # Margin from the bottom edge
        cv2.putText(display_frame, time_string, (text_x, text_y), font, font_scale, color, 1)

        # Display everything over the video feed.
        cv2.imshow('Video', display_frame)

        # Break the loop and stop the script if 'q' is pressed
        if cv2.waitKey(1) == ord("q"):
            break

    # By breaking the loop we run this code here which closes everything
    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print

