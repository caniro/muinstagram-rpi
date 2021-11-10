from django.db import models

class SnapshotFile(models.Model):
    # image_file에는 해당 파일에 접근할 수 있는 url이 저장된다.
    image_file = models.FileField('스냅샷', upload_to='snapshot/%Y/%m/%d/%H/%M',
                                null=True, blank=True)
    filename = models.CharField('파일명', max_length=64, null=True)
    content_type = models.CharField('Mimetype', max_length=128, null=True)
    size = models.IntegerField('파일크기')
    reg_date = models.DateTimeField('등록일', auto_now_add=True,
                                    null=True, blank=True)

    class Meta:
        ordering = ('-reg_date',)

    def __str__(self):
        return self.filename

class VideoFile(models.Model):
    video_file = models.FileField('녹화 파일', upload_to='video/%Y/%m/%d/%H',
                                null=True, blank=True)
    filename = models.CharField('파일명', max_length=64, null=True)
    content_type = models.CharField('Mimetype', max_length=128, null=True)
    size = models.IntegerField('파일크기')
    reg_date = models.DateTimeField('등록일', auto_now_add=True,
                                    null=True, blank=True)
    
    class Meta:
        ordering = ('-reg_date',)

    def __str__(self):
        return self.filename

# DRF 관련 코드는 나중에 서버쪽으로 옮기기