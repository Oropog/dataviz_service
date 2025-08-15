
from django.contrib import admin
from .models import DataFile, ChartConfig

@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    list_display = ("id", "filename", "uploaded_at")

@admin.register(ChartConfig)
class ChartConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "chart_type", "title", "created_at")
