# syntax=docker/dockerfile:1

FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY ./flask_app/requirements.txt .
RUN apt-get update && apt-get install -y build-essential \
    && pip install --upgrade pip \
    && pip install numpy==1.18.5 \
    && pip install -r requirements.txt

# Copy app code
COPY ./flask_app/. .

# Expose port
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]
