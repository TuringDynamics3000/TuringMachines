# TuringCapture™ Production Dockerfile
# Bank-grade container image for identity capture service
# Multi-stage build for optimal security and size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set labels for container metadata
LABEL maintainer="TuringDynamics3000"
LABEL service="turing-capture"
LABEL version="2.0.0"
LABEL description="TuringCapture™ - Identity & Document Capture Service"

# Create non-root user for security
RUN groupadd -r turing && useradd -r -g turing turing

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=turing:turing . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R turing:turing /app

# Switch to non-root user
USER turing

# Expose port
EXPOSE 8101

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8101/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8101 \
    LOG_LEVEL=INFO

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8101", "--workers", "4"]
