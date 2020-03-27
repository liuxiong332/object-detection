import cv2
import sys
import os
from imutils.video import VideoStream

if sys.platform == "win32":
    import os
    import msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

count = 0
# print("start")
# vs = VideoStream(src="videos/MP4_20200326_083722_PHOTOMOVIE.mp4").start()
cap = cv2.VideoCapture("videos/MP4_20200326_083722_PHOTOMOVIE.mp4")
while True:
    # frame = vs.read()
    ret, frame = cap.read()
    # print("get res", frame.shape)

    if not ret:
        break
    count += 1
    sys.stdout.buffer.write(frame.astype('int8').tostring())

# print("frame count ", count)
sys.stdout.flush()