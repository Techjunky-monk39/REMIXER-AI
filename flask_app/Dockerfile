# syntax=docker/dockerfile:1

FROM python:3.8.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg git build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port for Cloud Run
EXPOSE 8080

# Healthcheck for container stability
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:8080/healthz || exit 1

# Run the Flask app with Gunicorn on port 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
