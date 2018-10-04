from django.db import models

class Document(models.Model):
    videoFile = models.FileField(upload_to='documents/')
    subtitleFile = models.FileField(upload_to='documents/')