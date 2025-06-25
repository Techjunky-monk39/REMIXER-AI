# syntax=docker/dockerfile:1

FROM python:3.8.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY ./flask_app/requirements.txt .
RUN pip install --upgrade pip && pip install numpy==1.18.5 && pip install -r requirements.txt

# Copy app code
COPY ./flask_app/. .

# Expose port
EXPOSE 8080

# Run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
