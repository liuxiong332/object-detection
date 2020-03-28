import subprocess as sp
import numpy as np
import os
from pathlib import Path


def gen_hls_command(width, height, output_dir):
    return ['ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-pixel_format', 'bgr24',
            '-video_size', "{}x{}".format(width, height),  # 图片分辨率
            '-framerate', str(25),  # 视频帧率
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-f', 'hls',
            '-hls_time', '5',
            os.path.join(output_dir, "live.m3u8")]


class HlsGenerator:
    def __init__(self, width, height, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        command = gen_hls_command(int(width), int(height), output_dir)
        self.width = int(width)
        self.height = int(height)
        self.child_process = sp.Popen(command, stdin=sp.PIPE)
        self.frame_count = 0

    def write_frame(self, frame):
        if frame.shape != (self.height, self.width, 3):
            raise Exception("Frame argument is not valid")
        self.frame_count += 1
        self.child_process.stdin.write(frame.astype('int8').tostring())

    def join(self):
        self.child_process.stdin.flush()
        self.child_process.stdin.close()
        print("Gen video with frames ", self.frame_count)
        self.child_process.wait()
