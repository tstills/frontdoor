import cv2
from imutils.video import VideoStream
import time

# Initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()  # 'src=0' is typically the built-in webcam
time.sleep(2.0)  # Allow the camera to warm up

# Define the codec and create VideoWriter object for MP4 file
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

# Loop over the frames from the video stream
while True:
    # Grab the frame from the video stream
    frame = vs.read()
    
    if frame is None:
        break

    # Write the frame to the output file
    out.write(frame)

    # Display the frame to the screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # If the 'q' key is pressed, break from the loop
    if key == ord('q'):
        break

# Cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()
out.release()
