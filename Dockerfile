# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY http_server.py .
COPY server.json .

# Create directory for model cache
RUN mkdir -p /root/.malaya

# Expose port for HTTP server
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MALAYA_CACHE=/root/.malaya

# Default command (stdio mode)
CMD ["python", "server.py"]

# To run HTTP server instead, use:
# CMD ["python", "http_server.py"]
