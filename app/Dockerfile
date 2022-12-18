FROM python:latest

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT bash entrypoint.sh