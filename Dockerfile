# Multi-stage build for smaller image size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY list_groups.py .

# Create necessary directories
RUN mkdir -p session logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run as non-root user for security
RUN useradd -m -u 1000 telegrambot && \
    chown -R telegrambot:telegrambot /app
USER telegrambot

# Health check (optional)
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('session') else 1)"

# Default command
CMD ["python", "-u", "src/main.py"]
