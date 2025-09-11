# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for WeasyPrint and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango1.0-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf-xlib-2.0-dev \
    libglib2.0-dev \
    libgtk-3-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads/pdfs

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port 5002
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Run the application on port 5002 (override the default port 5000)
CMD ["python", "-c", "import main; main.app.run(debug=False, host='0.0.0.0', port=5002, use_reloader=False)"]
