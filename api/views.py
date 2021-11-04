from rest_framework import viewsets
from .models import SnapshotFile
from .serializers import SnapshotFileSerializer
from .paginations import SnapshotFilePageNumberPagination
from rest_framework.response import Response

class SnapshotViewSet(viewsets.ModelViewSet):
    queryset = SnapshotFile.objects.all()
    serializer_class = SnapshotFileSerializer
    pagination_class = SnapshotFilePageNumberPagination

    # 이미지 url 입력 시 다운로드되는 문제
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     res = Response(serializer.data)
    #     return res
