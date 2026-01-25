# Dockerfile for Gut Health Management App
# Flask + SQLite + SocketIO

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies (including C++ compiler for chromadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for persistent data and initial data backup
RUN mkdir -p /app/static/uploads /app/instance /app/initial_data

# Copy the initial database to a safe location (won't be overwritten by volume mount)
RUN if [ -f /app/instance/gut_health.db ]; then \
        cp /app/instance/gut_health.db /app/initial_data/gut_health.db; \
    fi

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Use entrypoint to initialize database if needed
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Run the application with gunicorn for production
# Using eventlet worker for SocketIO support
CMD ["python", "-c", "from app import app, socketio; socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)"]
