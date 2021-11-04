from django.http.response import StreamingHttpResponse
from .picam import MJpegStreamCam

mjpegstream = MJpegStreamCam()

def mjpeg_stream(request):
    return StreamingHttpResponse(mjpegstream,
        content_type='multipart/x-mixed-replace;boundary=--myboundary')
