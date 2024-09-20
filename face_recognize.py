#!/usr/bin/env python3

import cv2
import face_recognition

def face_recognize():

    # Load the known face image (replace with your image)
    known_image = face_recognition.load_image_file("dataset/Tim/IMG_2191.jpg")
    known_encoding = face_recognition.face_encodings(known_image)[0]

    # Initialize video capture from the USB camera
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        # Find all faces in the current frame
        faces_in_frame = face_recognition.face_locations(frame)
        encodings_in_frame = face_recognition.face_encodings(frame, faces_in_frame)

        # Loop through each face in the frame
        for (top, right, bottom, left), encoding in zip(faces_in_frame, encodings_in_frame):
            matches = face_recognition.compare_faces([known_encoding], encoding)

            # If a match is found, draw a rectangle around the face
            if matches[0]:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    face_recognize()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print
