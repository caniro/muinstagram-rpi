from rest_framework.pagination import PageNumberPagination

class SnapshotFilePageNumberPagination(PageNumberPagination):
    page_size = 10

class VideoFilePageNumberPagination(PageNumberPagination):
    page_size = 10
