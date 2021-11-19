from django.http.response import HttpResponse, StreamingHttpResponse
from datetime import datetime
from .picam import *

mjpegstream = MJpegStreamCam()

def mjpeg_stream(request):
    return StreamingHttpResponse(mjpegstream,
        content_type='multipart/x-mixed-replace;boundary=--myboundary')

# 영상 녹화 시작
def start_record(request):
    global last_time
    last_time = datetime.now()
    lock.acquire()
    recording.record_flag = True
    recording.remain_frames = TARGET_FRAME
    lock.release()
    return HttpResponse("<h1>Recording start</h1>")

# 이벤트 감지 -> 마지막 요청으로부터 1분 간 이미지 버킷에 올리기
def detect_event(request):
    global event_last_filename
    event_last_filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    event_lock.acquire()
    event_image.record_flag = True
    event_image.remain_frames = EVENT_TARGET_FRAME
    event_lock.release()
    return HttpResponse("<h1>Event detected</h1>")
