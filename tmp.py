from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2

# Construct the argument parse and parse the arguments
output_file = 'output.avi'
fps = 20

# Initialize the video stream and allow the camera sensor to warmup
print("Warming up camera...")
vs = VideoStream(0).start()
time.sleep(2.0)

# Initialize the FourCC, video writer, dimensions of the frame, and zeros array
fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
writer = None
(h, w) = (None, None)
zeros = None

# Loop over frames from the video stream
print('Starting')
while True:
    # Grab the frame from the video stream and resize it to have a maximum width of 300 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=300)

    # Check if the writer is None
    if writer is None:
        # Store the image dimensions, initialize the video writer, and construct the zeros array
        (h, w) = frame.shape[:2]
        writer = cv2.VideoWriter(output_file, fourcc, fps, (w * 2, h * 2), True)
        zeros = np.zeros((h, w), dtype="uint8")

# break the image into its RGB components, then construct the
    # RGB representation of each frame individually
#    (B, G, R) = cv2.split(frame)
#    R = cv2.merge([zeros, zeros, R])
#    G = cv2.merge([zeros, G, zeros])
#    B = cv2.merge([B, zeros, zeros])
    # construct the final output frame, storing the original frame
    # at the top-left, the red channel in the top-right, the green
    # channel in the bottom-right, and the blue channel in the
    # bottom-left
    output = np.zeros((h * 2, w * 2, 3), dtype="uint8")
    output[0:h, 0:w] = frame
#    output[0:h, w:w * 2] = R
#    output[h:h * 2, w:w * 2] = G
#    output[h:h * 2, 0:w] = B

    # Write the output frame to file
    writer.write(output)

    # Show the frames
    cv2.imshow("Frame", frame)
    cv2.imshow("Output", output)

    # if the `q` key was pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# Cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()
writer.release()

