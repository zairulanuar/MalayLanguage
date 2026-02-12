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

# ===== ADD THIS BLOCK =====
# Pre-download Malaya models (run as root)
RUN python -c "import malaya; \
    print('Downloading translation model...'); \
    malaya.translation.huggingface(model='mesolitica/translation-t5-small-standard-bahasa-cased', force_check=True); \
    print('Downloading spelling correction model...'); \
    malaya.spelling_correction.transformer(model='mesolitica/bert-tiny-standard-bahasa-cased', force_check=True); \
    print('Downloading normalizer model...'); \
    malaya.normalizer.transformer(model='mesolitica/normalizer-t5-small-standard-bahasa-cased', force_check=True); \
    print('All models downloaded successfully!')" || echo "Model pre-download failed, will download at runtime"
# ===== END OF BLOCK =====

# Create directory for model cache and set correct permissions
RUN mkdir -p /tmp/.malaya && \
    chmod 777 /tmp/.malaya

# Create non-root user and switch to it
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /tmp/.malaya
USER appuser

# Expose port for HTTP server
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MALAYA_CACHE=/tmp/.malaya
ENV PORT=8080

# Default command (HTTP mode for Cloud Run)
CMD ["python", "http_server.py"]
