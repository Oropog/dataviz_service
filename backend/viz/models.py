
from django.db import models

class DataFile(models.Model):
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=1024)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.filename}"

class ChartConfig(models.Model):
    chart_type = models.CharField(max_length=32)
    params_json = models.JSONField(default=dict, blank=True)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
