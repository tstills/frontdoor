#!/usr/bin/env python3

import cv2

name = "Tim"

cam = cv2.VideoCapture(0)

cv2.namedWindow("Press Space button to take a Photo", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Press Space button to take a Photo",600,400)

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to take or grab a new frame")
        break

    cv2.imshow("Press Space button to take a Photo", frame)

    k = cv2.waitKey(1)

    if k%256 == 27:
        print("Escape hit, we are closing the program")
        break
    elif k%256 == 32:
        img_name = "dataset/"+ name + "/image_{}.jpg".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!!".format(img_name))
        img_counter +=1

cam.release()

cv2.destroyAllWindows()

