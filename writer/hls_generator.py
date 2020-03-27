import subprocess as sp
import numpy as np

def gen_hls_command(width, height):
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
               "videos/live.m3u8"]

class HlsGenerator:
    def __init__(self, width, height):
        command = gen_hls_command(int(width), int(height))
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
