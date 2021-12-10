from django.db import models
from django.contrib.auth.models import User


# class Camera(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     name = models.CharField(max_length=10)
#     shop = models.ForeignKey(Shop, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'naga_camera'

# class Camera(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     name = models.CharField(max_length=10)
#     user = models.ForeignKey(User, models.DO_NOTHING)
#     # shop_id = models.ForeignKey(Shop, related_name="camera", on_delete=models.CASCADE, db_column="shop_id")

#     class Meta:
#         managed = False
#         db_table = 'naga_camera'




class Shop(models.Model):
    user_id = models.ForeignKey(User, related_name="shop", on_delete=models.CASCADE, db_column="user_id")
    name = models.CharField(max_length=10)
    # alert = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'naga_shop'

    def __str__(self):
        return self.name


class Camera(models.Model):
    shop_id = models.ForeignKey(Shop, related_name="camera", on_delete=models.CASCADE, db_column="shop_id")
    name = models.CharField(max_length=10, default='')
    alert = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'naga_camera'

    def __str__(self):
        return self.name

class Image(models.Model):
    # user_id = models.ForeignKey(User, related_name="uimg",
    #                             on_delete=models.CASCADE, db_column="user_id")
    camera_id = models.ForeignKey(Camera, related_name="cimg",
                                on_delete=models.CASCADE, db_column="camera_id")
    imgUrl = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'naga_image'




# class Camera(models.Model):
#     # shop_id = models.ForeignKey(Shop, related_name="camera", on_delete=models.CASCADE, db_column="shop_id")
#     user_id = models.ForeignKey(User, related_name="camera", on_delete=models.CASCADE, db_column="user_id", default='')
#     name = models.CharField(max_length=10, default='')
#
#     def __str__(self):
#         return self.name



class Event(models.Model):
    camera = models.CharField(max_length=10, default='')
    imgUrl = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'naga_event'