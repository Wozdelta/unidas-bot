FROM python:3.11-slim

# Environment
ENV DOCKER_CONTAINER=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:99

# Install system dependencies and headless browser (Chromium) + driver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    xvfb \
    ca-certificates \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (if needed)
EXPOSE 8080

# Start command (unbuffered stdout + immediate logs)
CMD ["sh", "-c", "echo '🚀 CONTAINER INICIADO' && xvfb-run -a python -u monitor_bot.py"]
