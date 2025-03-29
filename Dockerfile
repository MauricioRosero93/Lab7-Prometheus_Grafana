FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt .       
COPY kafka-monitoring.py . 

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8765
CMD ["python", "kafka-monitoring.py"]