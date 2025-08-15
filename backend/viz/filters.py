
import pandas as pd

_OPS = {
    'eq': lambda s, v: s == v,
    'ne': lambda s, v: s != v,
    'gt': lambda s, v: s > v,
    'lt': lambda s, v: s < v,
    'ge': lambda s, v: s >= v,
    'le': lambda s, v: s <= v,
    'contains': lambda s, v: s.astype(str).str.contains(str(v), na=False, case=False),
    'in': lambda s, v: s.isin(v if isinstance(v, (list, tuple, set)) else [v]),
}

def apply_filters(df: pd.DataFrame, conds):
    if not conds:
        return df
    mask = pd.Series([True] * len(df), index=df.index)
    for c in conds:
        col = c.col
        op = c.op
        val = c.value
        if col not in df.columns or op not in _OPS:
            continue
        try:
            mask &= _OPS[op](df[col], val)
        except Exception:
            # безопасно пропускаем некорректное условие
            pass
    return df[mask]
