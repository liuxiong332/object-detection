import cv2
import queue
import os
import numpy as np
from threading import Thread
import datetime
import _thread
import subprocess as sp
import time
from imutils.video import VideoStream

# 使用线程锁，防止线程死锁
mutex = _thread.allocate_lock()
# 存图片的队列
frame_queue = queue.Queue()
# 推流的地址，前端通过这个地址拉流，主机的IP，2019是ffmpeg在nginx中设置的端口号
rtmpUrl = "rtmp://192.168.40.145:2019/live/1"
# 用于推流的配置,参数比较多，可网上查询理解
command = ['ffmpeg',
           '-y',
           '-f', 'rawvideo',
           '-vcodec', 'rawvideo',
           '-pix_fmt', 'bgr24',
           '-s', "{}x{}".format(640, 480),  # 图片分辨率
           '-r', str(25.0),  # 视频帧率
           '-i', '-',
           '-c:v', 'libx264',
           '-pix_fmt', 'yuv420p',
           '-preset', 'ultrafast',
           '-f', 'flv',
           rtmpUrl]

hls_command = ['ffmpeg',
               '-y',
               '-f', 'rawvideo',
               '-pixel_format', 'bgr24',
               '-video_size', "{}x{}".format(1920, 1080),  # 图片分辨率
               '-framerate', str(30),  # 视频帧率
               '-i', '-',
               '-c:v', 'libx264',
               '-pixel_format', 'yuv420p',
               '-preset', 'ultrafast',
               '-f', 'hls',
               '-hls_time', '10',
               "videos/live.m3u8"]


def Video():
    # 调用相机拍图的函数
    vid = cv2.VideoCapture("videos/XQEO7341.mov")
    if not vid.isOpened():
        raise IOError("Couldn't open webcam or video")
    while (vid.isOpened()):
        return_value, frame = vid.read()

        # 原始图片推入队列中
        frame_queue.put(frame)


def push_frame():
    # 推流函数
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    prev_time = time.time()

    # 防止多线程时 command 未被设置
    while True:
        if len(hls_command) > 0:
            # 管道配置，其中用到管道
            p = sp.Popen(hls_command, stdin=sp.PIPE)
            break

    while True:
        if frame_queue.empty() != True:
            # 从队列中取出图片
            frame = frame_queue.get()
            #curr_time = timer()
            #exec_time = curr_time - prev_time
            #prev_time = curr_time
            #accum_time = accum_time + exec_time
            #curr_fps = curr_fps + 1

            # process frame
            # 你处理图片的代码
            # 将图片从队列中取出来做处理，然后再通过管道推送到服务器上
            # 增加画面帧率
            # if accum_time > 1:
            #accum_time = accum_time - 1
            #fps = "FPS: " + str(curr_fps)
            #curr_fps = 0

            # write to pipe
            # 将处理后的图片通过管道推送到服务器上,image是处理后的图片
            p.stdin.write(frame.tostring())


def run():
     # 使用两个线程处理

    thread1 = Thread(target=Video,)
    thread1.start()
    thread2 = Thread(target=push_frame,)
    thread2.start()

    thread1.join()
    thread2.join()


if __name__ == '__main__':
    # run()
    p = sp.Popen(hls_command, stdin=sp.PIPE)
    vs = VideoStream(src="videos/XQEO7341.mov").start()

    while True:
      frame = vs.read()
      if frame is None:
          break
      p.stdin.buffer.write(frame.astype('int8').tostring())
