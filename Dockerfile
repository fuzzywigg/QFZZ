# QFZZ - The Pulse of the Quantum Realm
# Multi-stage Docker build for production deployment

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Audio processing
    libsndfile1 \
    ffmpeg \
    # Icecast streaming
    libshout3 \
    libshout3-dev \
    # Build tools (for pip packages)
    gcc \
    g++ \
    make \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    # Try to install python-shout for Icecast support (optional)
    pip install python-shout || echo "python-shout not available, Icecast disabled"

# =============================================================================
# Development stage
# =============================================================================
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p qfzz_audio_content honeycomb logs

# Expose ports
# 8000: Icecast streaming
# 8001: HTTP API/streaming server
# 3000: Frontend (if running)
EXPOSE 8000 8001 3000

# Default command
CMD ["python", "main.py"]

# =============================================================================
# Production stage
# =============================================================================
FROM base as production

# Create non-root user
RUN useradd -m -u 1000 qfzz && \
    mkdir -p /app/qfzz_audio_content /app/honeycomb /app/logs && \
    chown -R qfzz:qfzz /app

# Copy only necessary files
COPY --chown=qfzz:qfzz qfzz/ ./qfzz/
COPY --chown=qfzz:qfzz main.py run_server.py ./
COPY --chown=qfzz:qfzz config/ ./config/
COPY --chown=qfzz:qfzz examples/ ./examples/

# Switch to non-root user
USER qfzz

# Expose ports
EXPOSE 8000 8001 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import http.client; h = http.client.HTTPConnection('localhost', 8001); h.request('GET', '/playlist.json'); r = h.getresponse(); exit(0 if r.status == 200 else 1)"

# Default command
CMD ["python", "run_server.py"]

# =============================================================================
# Testing stage
# =============================================================================
FROM development as testing

# Copy test files
COPY tests/ ./tests/

# Run tests
RUN python -m unittest discover -s tests -v

# =============================================================================
# Metadata
# =============================================================================
LABEL maintainer="QFZZ Team <admin@qfzz.radio>"
LABEL version="1.0.0"
LABEL description="QFZZ - AI-powered personalized radio station"
LABEL org.opencontainers.image.source="https://github.com/fuzzywigg/QFZZ"
LABEL org.opencontainers.image.licenses="MIT"
