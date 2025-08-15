
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

# Системные зависимости для pandas/matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     libjpeg62-turbo-dev     libpng-dev     libfreetype6-dev     libopenblas-dev     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Убедимся, что entrypoint исполняемый
RUN chmod +x /app/entrypoint.sh && sed -i 's/\r$//' /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
