from django.contrib.auth.models import User
from django.db import models


# class AlertTbl(models.Model):
#     shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
#     alert_msg = models.CharField(max_length=255)
#     alert_time = models.DateTimeField('경고 방송 송출 시간', auto_now_add=True)

#     class Meta:
#         db_table = 'naga_alert'
#         ordering = ('-alert_time', )
