from django.db import models
from django.contrib.auth.models import User


class Camera(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=10)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'naga_camera'


class Image(models.Model):
    user_id = models.ForeignKey(User, related_name="uimg",
                                on_delete=models.CASCADE, db_column="user_id")
    camera_id = models.ForeignKey(Camera, related_name="cimg",
                                on_delete=models.CASCADE, db_column="camera_id")
    imgUrl = models.CharField(max_length=255)
