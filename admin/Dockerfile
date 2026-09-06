FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY src /app/src
COPY manage.py /app/manage.py
CMD ["gunicorn", "tgs_admin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
