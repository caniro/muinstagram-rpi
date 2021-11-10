from django.http.response import HttpResponse, StreamingHttpResponse
from datetime import datetime
from .picam import *

mjpegstream = MJpegStreamCam()

def mjpeg_stream(request):
    return StreamingHttpResponse(mjpegstream,
        content_type='multipart/x-mixed-replace;boundary=--myboundary')

def start_record(request):
    global last_time
    last_time = datetime.now()
    lock.acquire()
    recording.record_flag = True
    recording.remain_frames = TARGET_FRAME
    lock.release()
    return HttpResponse("<h1>Recording start</h1>")
