from django.contrib.auth.models import User
from django.db import models


class Shop(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=10)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'naga_shop'


class AlertTbl(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    alert_msg = models.CharField(max_length=255)
    alert_time = models.DateTimeField('경고 방송 송출 시간', auto_now_add=True)

    class Meta:
        db_table = 'naga_alert'
        ordering = ('-alert_time', )
