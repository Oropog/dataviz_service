
import io
import pandas as pd
from pathlib import Path

READERS = {
    '.csv': lambda p: pd.read_csv(p),
    '.xlsx': lambda p: pd.read_excel(p),
}

def read_dataframe(path: str) -> pd.DataFrame:
    ext = Path(path).suffix.lower()
    if ext not in READERS:
        raise ValueError(f"Unsupported file type: {ext}")
    return READERS[ext](path)

def df_head_preview(df: pd.DataFrame, n: int = 10):
    return df.head(n).to_dict(orient='records')

def to_bytes_figure(fig, fmt: str = 'png') -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, bbox_inches='tight')
    buf.seek(0)
    return buf.read()
