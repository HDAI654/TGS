FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

EXPOSE 5500

CMD ["python3", "-m", "http.server", "5500", "--bind", "0.0.0.0"]