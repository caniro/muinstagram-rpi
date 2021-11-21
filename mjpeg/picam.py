import os
from datetime import datetime, timedelta
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import requests as req
from threading import Condition, Lock, Thread
from picamera import PiCamera
from subprocess import call
from mysite.settings import BASE_DIR
from config import BUCKET_NAME, s3_connection, HOSTNAME, S3_BUCKET_DOMAIN
from .models import Image, Camera

SNAPSHOT_DIR = os.path.join(BASE_DIR, 'media/snapshot/')
VIDEO_DIR = os.path.join(BASE_DIR, 'media/video/')


class PiCam:
    def __init__(self, framerate=25, width=640, height=480):
        self.size = (width, height)
        self.framerate = framerate

        self.camera = PiCamera()
        self.camera.rotation = 180
        self.camera.resolution = self.size
        self.camera.framerate = self.framerate


# 전역 객체로 전체 사이클 관리 (IPC 때문에 객체로 사용)
# api 요청시 남은 프레임을 갱신
class Recording:
    def __init__(self):
        self.record_flag = False
        self.is_recording = False
        self.remain_frames = 0

def is_elapsed_one_sec():
    global last_time

    now = datetime.now()
    if now - last_time < timedelta(milliseconds=900):
        return False
    last_time = now
    return True

def upload_to_s3(key, frame):
    s3 = s3_connection()
    s3.put_object(Bucket=BUCKET_NAME, Key=key,
                    Body=BytesIO(frame), ACL='public-read')

camera_row = Camera.objects.get(name=HOSTNAME)
user = camera_row.user

# 이미지 한 장씩 버킷에 저장
def upload_image_frame(frame):
    basename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    print(basename, 'saved')
    key = f'{user.id}/{HOSTNAME}/image/{basename}'
    upload_to_s3(key, frame)
    # DB 저장
    image_url = os.path.join(S3_BUCKET_DOMAIN, key)
    image = Image()
    image.imgUrl = image_url
    image.camera_id = camera_row
    image.user_id = user
    image.save()

event_image = Recording()
event_last_filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
event_lock = Lock()
EVENT_TARGET_FRAME = 60

def check_event(frame):
    global event_last_filename

    if not event_image.record_flag or len(frame) == 0:
        return
    event_new_filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    if event_new_filename == event_last_filename:
        return
    event_last_filename = event_new_filename

    if not event_image.is_recording:
        print('이벤트 발생 감지')
        event_image.is_recording = True
        event_image.remain_frames = EVENT_TARGET_FRAME

    if event_image.is_recording:
        print('이미지 저장 중... 남은 프레임:', event_image.remain_frames)
        try:
            upload_image_frame(frame)
            event_image.remain_frames -= 1
        except Exception as e:
            print('error:', e)

    # 원하는 프레임을 다 찍었으면 api 호출하여 db 거쳐서 파일로 저장
    if event_image.is_recording and event_image.remain_frames == 0:
        print('이벤트 이미지 저장 완료')
        event_lock.acquire()
        event_image.record_flag = False
        event_image.is_recording = False
        event_lock.release()

def save_image(frame):
    if not is_elapsed_one_sec():
        return
    thread = Thread(target=upload_image_frame, args=(frame, ))
    thread.start()
    # check_event(frame)


last_time = datetime.now()
last_time_image = datetime.now()
FRAMERATE = 5 # 초당 프레임 수
TARGET_TIME = 10 # 녹화 시간
TARGET_FRAME = FRAMERATE * TARGET_TIME
VIDEO_SERVER_URL = 'http://localhost:8000/api/video/'
lock = Lock()
recording = Recording()
file_path = ''
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
video = None

def convert_format(src, dst):
    command = f"MP4Box -add {src} {dst}"
    call([command], shell=True)

# mp4 변환
def convert_to_mp4(file_path):
    print('start converting file...')
    mp4_file_path = file_path.replace('h264', 'mp4')
    convert_format(file_path, mp4_file_path)
    os.remove(file_path)
    print('end converting file and deleting original file')
    return mp4_file_path

def upload_video(url, file_path):
    print(file_path)
    data = {
        'filename': os.path.basename(file_path),
        'content_type': 'video/mp4',
        'size': os.path.getsize(file_path),
    }
    try:
        res = req.post(url, data=data, files={
            'video_file': open(file_path, 'br')
        })
    except Exception as e:
        print('error:', e)

def save_video(frame):
    global last_time, file_path, video

    if not recording.record_flag or len(frame) == 0:
        return
    now = datetime.now()
    # if now - last_time < timedelta(milliseconds=(1000 // FRAMERATE)):
    #     return
    last_time = now

    # 영상 촬영 준비
    if not recording.is_recording:
        print('녹화 시작')
        recording.is_recording = True
        recording.remain_frames = TARGET_FRAME
        # fname = datetime.now().strftime("%Y%m%d_%H%M%S.h264")
        fname = datetime.now().strftime("%Y%m%d_%H%M%S.avi")
        file_path = os.path.join(VIDEO_DIR, fname)
        video = cv2.VideoWriter(file_path, fourcc, FRAMERATE, (640, 480))

    if recording.is_recording:
        # print('녹화 중... 남은 프레임:', recording.remain_frames)
        try:
            img = np.asarray(Image.open(BytesIO(frame)))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            video.write(img)
            recording.remain_frames -= 1
        except Exception as e:
            print('error:', e)

    # 원하는 프레임을 다 찍었으면 api 호출하여 db 거쳐서 파일로 저장
    if recording.is_recording and recording.remain_frames == 0:
        print('녹화 완료')
        # file_path = convert_to_mp4(file_path)
        lock.acquire()
        recording.record_flag = False
        recording.is_recording = False
        lock.release()
        upload_video(VIDEO_SERVER_URL, file_path)


# PiCamera().start_recording 메서드가 내부적으로 처리하는 write를 정의
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'): # jpeg magic number
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
            save_image(self.frame)
            # save_video(self.frame)
        return self.buffer.write(buf)


class MJpegStreamCam(PiCam):
    def __init__(self, framerate=5, width=640, height=480):
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

    def __del__(self):
        self.camera.stop_recording()
