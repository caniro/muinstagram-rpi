from django.urls import path
from .views import *
# from django.http import HttpResponse

urlpatterns = [
    # path('test', lambda request: HttpResponse('Hello World!')),
    path('stream', mjpeg_stream, name='stream'),
    path('record', start_record, name='record'),
    path('event', detect_event, name='event'),
]
