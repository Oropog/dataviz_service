
import io
from typing import List, Optional, Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px

from .utils import to_bytes_figure

_ALLOWED = {"line", "bar", "pie", "hist", "scatter", "box", "auto"}


def _auto_chart_type(df: pd.DataFrame, x: Optional[str], y: Any) -> str:
    # Простое правило выбора
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    if x and y:
        if pd.api.types.is_datetime64_any_dtype(df[x]) or 'date' in x.lower():
            return 'line'
        if isinstance(y, list) or y in num_cols:
            return 'line' if pd.api.types.is_datetime64_any_dtype(df[x]) else 'scatter'
    if x and x in df.columns and x not in num_cols:
        return 'bar'
    if len(num_cols) >= 1:
        return 'hist'
    return 'bar'


def _ensure_fig(figsize: Optional[List[float]]):
    if figsize and isinstance(figsize, (list, tuple)) and len(figsize) == 2:
        plt.figure(figsize=(figsize[0], figsize[1]))
    else:
        plt.figure(figsize=(8, 5))


def plot_static(df: pd.DataFrame, chart_type: str, x: Optional[str], y: Any,
                title: Optional[str], xlabel: Optional[str], ylabel: Optional[str],
                legend: bool, figsize: Optional[List[float]], color: Optional[str],
                bins: Optional[int], fmt: str = 'png') -> bytes:
    if chart_type not in _ALLOWED:
        raise ValueError(f"Unsupported chart_type: {chart_type}")

    if chart_type == 'auto':
        chart_type = _auto_chart_type(df, x, y)

    _ensure_fig(figsize)

    if chart_type == 'line':
        if isinstance(y, list):
            for col in y:
                plt.plot(df[x], df[col], label=col)
        elif y:
            plt.plot(df[x], df[y], label=str(y))
        else:
            # если y не задан, рисуем все числовые по x-индексу
            df.select_dtypes('number').plot(kind='line')
        if legend:
            plt.legend()

    elif chart_type == 'bar':
        if isinstance(y, list):
            for col in y:
                plt.bar(df[x], df[col], label=col)
            if legend:
                plt.legend()
        elif y:
            plt.bar(df[x], df[y])
        else:
            df.select_dtypes('number').sum().plot(kind='bar')

    elif chart_type == 'pie':
        # Для pie можно указать x как категорию, y как числовую метрику
        if x and y:
            series = df.groupby(x)[y].sum()
        elif x:
            series = df[x].value_counts()
        else:
            series = df.select_dtypes('number').sum()
        plt.pie(series.values, labels=series.index, autopct='%1.1f%%')

    elif chart_type == 'hist':
        target = y if y else df.select_dtypes('number').columns.tolist()
        if isinstance(target, list):
            for col in target:
                plt.hist(df[col].dropna(), bins=bins or 30, alpha=0.5, label=col)
            if legend:
                plt.legend()
        else:
            plt.hist(df[target].dropna(), bins=bins or 30)

    elif chart_type == 'scatter':
        if not (x and y):
            raise ValueError("scatter requires x and y")
        if isinstance(y, list):
            for col in y:
                plt.scatter(df[x], df[col], label=col, alpha=0.7)
            if legend:
                plt.legend()
        else:
            plt.scatter(df[x], df[y], alpha=0.7)

    elif chart_type == 'box':
        target = y if y else df.select_dtypes('number').columns.tolist()
        plt.boxplot([df[col].dropna() for col in (target if isinstance(target, list) else [target])], labels=(target if isinstance(target, list) else [target]))

    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    fig = plt.gcf()
    data = to_bytes_figure(fig, fmt)
    plt.close(fig)
    return data


def plot_interactive_html(df: pd.DataFrame, chart_type: str, x: Optional[str], y: Any,
                          title: Optional[str], bins: Optional[int]) -> str:
    if chart_type == 'auto':
        chart_type = _auto_chart_type(df, x, y)

    if chart_type == 'line':
        if isinstance(y, list):
            fig = px.line(df, x=x, y=y, title=title)
        else:
            fig = px.line(df, x=x, y=y, title=title)
    elif chart_type == 'bar':
        fig = px.bar(df, x=x, y=y, title=title)
    elif chart_type == 'pie':
        if x and y:
            agg = df.groupby(x)[y].sum().reset_index()
            fig = px.pie(agg, names=x, values=y, title=title)
        elif x:
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, 'count']
            fig = px.pie(counts, names=x, values='count', title=title)
        else:
            num = df.select_dtypes('number').sum().reset_index()
            num.columns = ['metric', 'value']
            fig = px.pie(num, names='metric', values='value', title=title)
    elif chart_type == 'hist':
        target = y if y else df.select_dtypes('number').columns.tolist()[0]
        fig = px.histogram(df, x=target, nbins=bins or 30, title=title)
    elif chart_type == 'scatter':
        if not (x and y):
            raise ValueError("scatter requires x and y")
        fig = px.scatter(df, x=x, y=y, title=title)
    elif chart_type == 'box':
        target = y if y else df.select_dtypes('number').columns.tolist()
        fig = px.box(df, y=target, title=title)
    else:
        fig = px.line(df, x=x, y=y, title=title)

    return fig.to_html(full_html=True, include_plotlyjs='cdn')
