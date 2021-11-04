from django.urls import path
from .views import *
from django.http import HttpResponse

urlpatterns = [
    path('stream', mjpeg_stream, name='stream'),
    # path('stream', lambda request: HttpResponse('Hello World!')),
]
