#!/usr/bin/env python3

import os
from imutils import paths
import face_recognition
import pickle
import cv2

print("[INFO] start processing faces...")
image_paths = list(paths.list_images("dataset"))
known_encodings = []
known_names = []

for (ii, image_path) in enumerate(image_paths):
    print(f"[INFO] processing image {ii + 1}/{len(image_paths)}")
    name = image_path.split(os.path.sep)[-2]
    
    image = cv2.imread(image_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)
    
    for encoding in encodings:
        known_encodings.append(encoding)
        known_names.append(name)

print("[INFO] serializing encodings...")
data = {"encodings": known_encodings, "names": known_names}
with open("encodings.pickle", "wb") as f:
    f.write(pickle.dumps(data))

print("[INFO] Training complete. Encodings saved to 'encodings.pickle'")
