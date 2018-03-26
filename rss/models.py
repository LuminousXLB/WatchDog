from watchdog.settings import *
from django.db import models


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    pub_date = models.DateTimeField()
    models.FileField(upload_to='anno/', blank=True)
