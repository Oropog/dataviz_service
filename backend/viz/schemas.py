
from typing import List, Optional, Any
from ninja import Schema

class UploadResponse(Schema):
    file_id: int
    filename: str
    head: List[dict]
    columns: List[str]

class FilterCond(Schema):
    col: str
    op: str
    value: Any

class PlotRequest(Schema):
    file_id: int
    chart_type: str
    x: Optional[str] = None
    y: Optional[Any] = None  # str | List[str]
    title: Optional[str] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    legend: Optional[bool] = True
    figsize: Optional[List[float]] = None  # [w, h]
    color: Optional[str] = None
    bins: Optional[int] = None
    format: str = "png"  # png | jpeg | html
    filters: Optional[List[FilterCond]] = None

class FileInfo(Schema):
    id: int
    filename: str
    uploaded_at: str
