from django.urls import path, include
from rest_framework import routers
from api.views import *

router = routers.DefaultRouter()

router.register('snapshot', SnapshotViewSet)    # api/snapshot

urlpatterns = [
    path('', include(router.urls)),
]
