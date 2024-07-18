FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/scan_and_notify.py .

COPY config/servers.yaml /config/servers.yaml

RUN apt-get update && apt-get install -y docker.io && apt-get clean

VOLUME /var/run/docker.sock

ENTRYPOINT ["sh", "-c", "service docker start && python3 scan_and_notify.py"]
