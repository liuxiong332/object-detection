import cv2
import sys
from imutils.video import VideoStream

if sys.platform == "win32":
    import os
    import msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

count = 0
# print("start")
vs = VideoStream(src="videos/XQEO7341.mov").start()
while True:
    frame = vs.read()
    # print("get res", frame.shape)

    if frame is None:
        break
    count += 1
    # sys.stdout.buffer.write(frame.astype('int8').tostring())

print("frame count ", count)
sys.stdout.flush()