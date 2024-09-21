#!/usr/bin/env python3

import cv2
import face_recognition
import os
import pickle

from imutils import paths

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


def face_recognize(known_encodings):

    # Initialize video capture from the USB camera
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        # Find all faces in the current frame
        faces_in_frame = face_recognition.face_locations(frame)
        encodings_in_frame = face_recognition.face_encodings(frame, faces_in_frame)

        # Loop through each face in the frame
        for (top, right, bottom, left), encoding in zip(faces_in_frame, encodings_in_frame):
            matches = face_recognition.compare_faces(known_encodings["encodings"], encoding)

            # If a match is found...
            if matches[0]:

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, 'Tim', (left + 6,  bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    known_encodings = get_encodings()
    face_recognize(known_encodings)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print

