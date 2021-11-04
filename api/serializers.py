from rest_framework import serializers
from .models import SnapshotFile

class SnapshotFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnapshotFile
        exclude = []
