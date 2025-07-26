ARG PYTHON_VERSION=3.13
ARG PORT=8000
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]