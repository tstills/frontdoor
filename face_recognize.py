#!/usr/bin/env python3

import cv2
import face_recognition
import os
import pickle
import sys
import datetime
import time

from picamera2 import Picamera2

from RPi import GPIO

from imutils import paths

MOTION_DETECT_PIN_N = 22

# Read the known encodings from a pickle file.
# If the pickle file doesn't exist, create it.
def get_encodings():
    pickle_file = 'encodings.pickle'

    if not os.path.isfile(pickle_file):
        print('Start processing images')
        image_paths = list(paths.list_images('dataset'))

        known_encodings = []
        known_names = []

        for (ii, image_path) in enumerate(image_paths):
            print('Processing image {}/{}'.format(ii+1, len(image_paths)))

            name = image_path.split(os.path.sep)[-2]

            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            boxes = face_recognition.face_locations(rgb, model='hog')

            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(name)

        print('Serializing encodings')
        data = {'encodings': known_encodings, 'names': known_names}

        f = open(pickle_file, 'wb')
        f.write(pickle.dumps(data))
        f.close()
    else:
        data = pickle.loads(open(pickle_file, 'rb').read())

    return data

#
#  Do face recognition
#
def face_recognize(known_encodings):
    time_diffs = []
    count = 0

    faces_found = []

    # Initialize video capture from the USB camera
#    cap = cv2.VideoCapture(0)

    # Keep track of how many faces we've found
    last_face_count = -1
    face_count = 0
    last_match_count = -1
    match_count = 0
    last_unix_time = 0
    count = 0

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080)}))
    picam2.start()

    while True:
        ret, frame = cap.read()
        if not ret:
            print('Unable to read from camera')
            sys.exit(1)

        # Find all faces in the current frame
        faces_in_frame = face_recognition.face_locations(frame)
        encodings_in_frame = face_recognition.face_encodings(frame, faces_in_frame)

        # If there are any faces in the frame:
        if encodings_in_frame:

            # Get the current date and time
            current_time = datetime.datetime.now()
            time_string = current_time.strftime("%H:%M %m/%d/%Y")

            # Define the font, scale, color, and thickness for the text
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            color = (255, 255, 255)  # White color for the text (B, G, R)
            thickness = 2

            # Get the size of the frame (height, width)
            frame_height, frame_width, _ = frame.shape

            # Calculate position for the text (lower left corner)
            text_x = 10                 # Margin from the left edge
            text_y = frame_height - 10  # Margin from the bottom edge

            # Loop through each face in the frame
            for (top, right, bottom, left), encoding in zip(faces_in_frame, encodings_in_frame):
                matches = face_recognition.compare_faces(known_encodings["encodings"], encoding)
                face_count += 1

                # If a match is found...
                match_found = False
                for ii, match in enumerate(matches):
                    if match:
                        # Increment the face count
                        match_count += 1

                        # Decode the name
                        name = known_encodings['names'][ii]
                        if name not in faces_found:
                            faces_found = name
                            print(name)

                        # Draw a box around the face
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                        # Draw a label with a name below the face
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, name, (left + 6,  bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Add the time string to the frame
            cv2.putText(frame, time_string, (text_x, text_y), font, font_scale, color, 1)

            # Write the frame to disk
#            if (match_count):
#                ((match_count == 0) && (face_count > last_face_count)):
#                cv2.imwrite('captured_frame.jpg', frame)
#                last_face_count = face_count
            file_name = 'images/image_'
            if count < 100:
                file_name += '0'
            if count < 10:
                file_name += '0'
            file_name = '%s%d' % (file_name, count)
            file_name += '.jpg'
            cv2.imwrite(file_name, frame)
            count += 1

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

#
#  Callback function for the motion detection interrupt
#
def motion_detect_callback(channel):
    print('Motion detected on GPIO channel {}'.format(channel))

#
#  Main function
#
def main():
    # Set up the GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTION_DETECT_PIN_N, GPIO.IN)

    known_encodings = get_encodings()
#    face_recognize(known_encodings)

    while True:
        # Poll the active low motion detect pin
        # I hate doing this by polling, but I get a weird runtime exception when I setup the interrrupt
        if not GPIO.input(MOTION_DETECT_PIN_N):
            print('Motion detected')
            face_recognize(known_encodings)
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print
