# MAGAgents - Docker Deployment
# Make AI Agents Great Again! 🇺🇸

FROM python:3.11-slim

LABEL maintainer="MAGAgents"
LABEL description="Trump-style US Government AI Multi-Agent System"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/reports

# Expose dashboard port
EXPOSE 7892

# Environment variables
ENV PYTHONPATH=/app
ENV MAGAGENTS_DATA_DIR=/app/data
ENV MAGAGENTS_SCHEDULER_ENABLED=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7892/api/stats || exit 1

# Default command: Start dashboard server
CMD ["python3", "dashboard/server.py", "--static", "--port", "7892"]
