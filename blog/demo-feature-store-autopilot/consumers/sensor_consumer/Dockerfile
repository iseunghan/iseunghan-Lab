FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy sensor consumer specific files
COPY sensor_consumer.py .

# Run the sensor consumer
CMD ["python", "sensor_consumer.py"]
