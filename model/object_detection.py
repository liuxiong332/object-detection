from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
from writer.hls_generator import HlsGenerator
import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

CONFDIENCE = 0.2


def read_config():
    config_path = os.path.join(ROOT_DIR, "config.json")
    with open(config_path, "r") as fp:
        config = json.load(fp)
        print("Get config:", config)
        video_path = config["simulateVideo"]
        video_path = os.path.abspath(os.path.join(ROOT_DIR, video_path))

        output_dir = config["outputDir"]
        output_dir = os.path.abspath(os.path.join(ROOT_DIR, output_dir))
        print("Get Video path", video_path)
        return {"video_path": video_path, "output_dir": output_dir}


# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))


class ModelRunner:
    def __init__(self, conn, key):
        # load our serialized model from disk
        proto_path = os.path.join(ROOT_DIR, "MobileNetSSD_deploy.prototxt.txt")
        model_path = os.path.join(ROOT_DIR, "MobileNetSSD_deploy.caffemodel")
        print("[INFO] loading model...", proto_path, model_path)
        self.net = cv2.dnn.readNetFromCaffe(proto_path, model_path)
        self.conn = conn
        self.key = key

    def read_from_cap(self, capture):
        ret, frame = capture.read()
        if not ret:
            if not self.conn.poll(0):
                    # Set index to 0 (start frame)
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return capture.read()
            else:
                print("Recv msg, will quit...", self.conn.recv())

        return ret, frame

    def run(self):
        config = read_config()

        # initialize the video stream, allow the cammera sensor to warmup,
        # and initialize the FPS counter
        print("[INFO] starting video stream...")
        capture = cv2.VideoCapture("videos/XQEO7341.mov")
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)
        print("The video width and height is ", width, height)

        outvideo_path = os.path.join(config["output_dir"], self.key)
        print("The video will output to ", outvideo_path)
        hls_generator = HlsGenerator(width, height, outvideo_path)

        # loop over the frames from the video stream
        while True:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            # ret, frame = capture.read()
            ret, frame = self.read_from_cap(capture)
            if not ret:
                break

            frame = imutils.resize(frame, width=width, height=height)

            # grab the frame dimensions and convert it to a blob
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

            # pass the blob through the network and obtain the detections and
            # predictions
            self.net.setInput(blob)
            detections = self.net.forward()

            put_rect(detections, frame, w, h)
            hls_generator.write_frame(frame)

        # do a bit of cleanup
        # cv2.destroyAllWindows()
        # vs.stop()
        hls_generator.join()


def put_rect(detections, frame, width, height):
    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > CONFDIENCE:
            # extract the index of the class label from the
            # `detections`, then compute the (x, y)-coordinates of
            # the bounding box for the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * \
                np.array([width, height, width, height])
            (startX, startY, endX, endY) = box.astype("int")

            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx],
                                         confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
