import os
from datetime import datetime, timedelta
from io import BytesIO
import requests as req
from threading import Condition
from picamera import PiCamera
from mysite.settings import BASE_DIR

SNAPSHOT_DIR = os.path.join(BASE_DIR, 'media/snapshot/')

class PiCam:
    def __init__(self, framerate=25, width=640, height=480):
        self.size = (width, height)
        self.framerate = framerate

        self.camera = PiCamera()
        self.camera.rotation = 180
        self.camera.resolution = self.size
        self.camera.framerate = self.framerate

last_time = datetime.now()

def save_image(frame):
    global last_time
    if not len(frame):
        return
    now = datetime.now()
    if now - last_time < timedelta(seconds=1):
        return

    last_time = now
    fname = now.strftime("%Y%m%d_%H%M%S.jpg")
    year, month, day, hour, minute = fname[:4], fname[4:6], fname[6:8], fname[9:11], fname[11:13]
    # print(year, month, day, hour, minute)
    dir_path = os.path.join(SNAPSHOT_DIR, year, month, day, hour, minute)
    # 디렉토리 생성
    # if not os.path.exists(dir_path):
    #     os.makedirs(dir_path)
    file_path = os.path.join(dir_path, fname)
    # 파일로 저장
    if not os.path.isfile(file_path):
        print(file_path)
        # with open(file_path, "wb") as f: # 직접 저장
        #     f.write(frame)
        # api 호출해서 db 거쳐서 저장
        data = {
            'filename': fname,
            'content_type': 'image/jpeg',
            'size': len(frame),
        }
        url = 'http://localhost:8000/api/snapshot/'
        headers = {
            'Content-Disposition': f'attachment; filename={fname}',
        }
        try:
            res = req.post(url, headers=headers, data=data, files={
                'image_file': frame
            })
        except Exception as e:
            print('error:', e)


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
            save_image(self.frame)
        return self.buffer.write(buf)

class MJpegStreamCam(PiCam):
    def __init__(self, framerate=10, width=640, height=480):
        super().__init__(framerate=framerate, width=width, height=height)
        self.output = StreamingOutput()
        self.camera.start_recording(self.output, format='mjpeg')

    def __iter__(self):
        while True:
            with self.output.condition:
                self.output.condition.wait()
                frame = self.output.frame
            yield (b'--myboundary\n'
                    b'Content-Type:image/jpeg\n'
                    b'Content-Length: ' + f"{len(frame)}".encode() + b'\n\n' +
                    frame + b'\n')
