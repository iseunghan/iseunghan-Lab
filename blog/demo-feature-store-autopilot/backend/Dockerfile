FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/. ./

# Copy feast_repo for feature store operations
COPY feast_repo ./feast_repo

# Expose port
EXPOSE 8000

# Apply Feast feature registry on container start
RUN cd /app/feast_repo && feast apply

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--access-log"]
