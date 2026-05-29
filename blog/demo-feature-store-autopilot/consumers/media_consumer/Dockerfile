FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy media consumer specific files
COPY media_consumer.py .

# Run the media consumer
CMD ["python", "media_consumer.py"]
