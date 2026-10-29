# ==============================================================================
# StudentPulse — Student Performance Analytics Dashboard
# Production-ready, lightweight Dockerfile
# Developer: Daniel Richard Xavier
# ==============================================================================

# Base image: Official Python slim image for minimal footprint and low vulnerability surface
FROM python:3.11-slim

# Container runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Set container working directory
WORKDIR /app

# Create non-root system user for security compliance
RUN useradd -m -u 1000 appuser

# Install Python dependencies first for layer caching efficiency
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code, sample dataset, and entrypoint
COPY app.py ./
COPY src/ ./src/
COPY data/ ./data/

# Adjust file ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Streamlit default network port
EXPOSE 8501

# Health check to query Streamlit native health status endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Launch the Streamlit application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
