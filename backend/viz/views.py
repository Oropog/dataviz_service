
import os
import io
from datetime import datetime
from typing import List

import pandas as pd
from ninja import NinjaAPI, File, UploadedFile
from ninja.responses import Response
from django.http import HttpResponse
from django.conf import settings

from .models import DataFile, ChartConfig
from .schemas import UploadResponse, PlotRequest, FileInfo
from .utils import read_dataframe, df_head_preview
from .filters import apply_filters
from .plotting import plot_static, plot_interactive_html

api = NinjaAPI(title="DataViz API", version="1.0")

@api.post("/upload", response=UploadResponse)
def upload(request, file: UploadedFile = File(...)):
    # Сохраняем исходный файл в MEDIA_ROOT
    fname = file.name
    ext = os.path.splitext(fname)[1].lower()
    if ext not in {'.csv', '.xlsx'}:
        return Response({"detail": f"Unsupported file type: {ext}"}, status=400)

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    save_name = f"{timestamp}_{fname}"
    save_path = os.path.join(settings.MEDIA_ROOT, save_name)
    with open(save_path, 'wb') as out:
        for chunk in file.chunks():
            out.write(chunk)

    # Пробуем прочитать DataFrame для предпросмотра
    try:
        df = read_dataframe(save_path)
    except Exception as e:
        # удалим бракованный файл
        try:
            os.remove(save_path)
        except Exception:
            pass
        return Response({"detail": f"Failed to parse file: {e}"}, status=400)

    datafile = DataFile.objects.create(filename=fname, path=save_path)

    return {
        "file_id": datafile.id,
        "filename": fname,
        "head": df_head_preview(df, n=10),
        "columns": [str(c) for c in df.columns],
    }

@api.get("/files", response=List[FileInfo])
def files_list(request):
    items = DataFile.objects.order_by('-uploaded_at').all()
    return [
        FileInfo(id=i.id, filename=i.filename, uploaded_at=i.uploaded_at.isoformat())
        for i in items
    ]

@api.get("/files/{file_id}/preview")
def file_preview(request, file_id: int):
    try:
        df = read_dataframe(DataFile.objects.get(id=file_id).path)
    except DataFile.DoesNotExist:
        return Response({"detail": "file not found"}, status=404)
    except Exception as e:
        return Response({"detail": f"failed to read: {e}"}, status=400)

    return {"head": df_head_preview(df, 10), "columns": [str(c) for c in df.columns]}

@api.post("/plot")
def plot(request, payload: PlotRequest):
    # Загружаем данные
    try:
        datafile = DataFile.objects.get(id=payload.file_id)
    except DataFile.DoesNotExist:
        return Response({"detail": "file not found"}, status=404)

    try:
        df = read_dataframe(datafile.path)
    except Exception as e:
        return Response({"detail": f"failed to read: {e}"}, status=400)

    # Фильтрация
    try:
        df = apply_filters(df, payload.filters)
    except Exception:
        pass

    # Построение
    fmt = (payload.format or 'png').lower()

    if fmt in {'png', 'jpeg', 'jpg'}:
        try:
            img = plot_static(
                df=df,
                chart_type=payload.chart_type,
                x=payload.x,
                y=payload.y,
                title=payload.title,
                xlabel=payload.xlabel,
                ylabel=payload.ylabel,
                legend=bool(payload.legend),
                figsize=payload.figsize,
                color=payload.color,
                bins=payload.bins,
                fmt='jpeg' if fmt in {'jpeg', 'jpg'} else 'png',
            )
            # Сохраняем изображение и отдаём пользователю
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            graph_path = os.path.join(settings.MEDIA_ROOT, f"graph.{fmt}")
            with open(graph_path, "wb") as f:
                f.write(img)
                return HttpResponse(img, content_type=f"image/{'jpeg' if fmt in {'jpeg','jpg'} else 'png'}")
        except Exception as e:
            return Response({"detail": f"plot error: {e}"}, status=400)
        #return HttpResponse(img, content_type=f"image/{'jpeg' if fmt in {'jpeg','jpg'} else 'png'}")

    elif fmt == 'html':
        try:
            html = plot_interactive_html(
                df=df,
                chart_type=payload.chart_type,
                x=payload.x,
                y=payload.y,
                title=payload.title,
                bins=payload.bins,
            )
        except Exception as e:
            return Response({"detail": f"plot error: {e}"}, status=400)
        return HttpResponse(html, content_type="text/html; charset=utf-8")

    else:
        return Response({"detail": f"Unsupported format: {fmt}"}, status=400)
