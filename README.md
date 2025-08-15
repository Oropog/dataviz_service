# DataViz Service

Запуск:

```bash
docker compose up --build
```

Документация API: http://localhost:8000/api/docs

Основные эндпоинты:
- `POST /api/upload` — загрузка CSV/XLSX
- `GET /api/files` — список загруженных файлов
- `GET /api/files/{id}/preview` — предпросмотр (первые 10 строк)
- `POST /api/plot` — построение графика

Параметры `/api/plot` (в теле JSON или form-data):
- `file_id` (int) — ID загруженного файла
- `chart_type` (str) — line | bar | pie | hist | scatter | box | auto
- `x` (str, опционально) — имя колонки для оси X
- `y` (str|list, опционально) — имя(ена) колонок для оси Y
- `format` (str) — png | jpeg | html
- `title`, `xlabel`, `ylabel`, `legend` (bool), `figsize` ([w,h]), `color` (str)
- `bins` (int, для hist)
- `filters` (list[ {col, op, value} ]) — условия фильтрации (op: eq, ne, gt, lt, ge, le, contains, in)
