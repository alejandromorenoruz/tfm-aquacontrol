FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpcap-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir scapy

WORKDIR /app
COPY sensor.py .

CMD ["python3", "-u", "sensor.py"]
