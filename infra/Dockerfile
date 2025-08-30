FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        netcat-traditional \
        curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend first
COPY backend/ /app/backend/

# Copy ui package.json first to leverage Docker layer caching
COPY ui/package.json /app/ui/package.json

# Install frontend dependencies in a separate step to ensure they're always installed
RUN cd /app/ui && \
    npm install && \
    echo "=== NPM INSTALL COMPLETED ===" && \
    ls -la node_modules/.bin/ && \
    echo "=== ESLINT VERSION ===" && \
    ./node_modules/.bin/eslint --version

# Copy the rest of ui files
COPY ui/ /app/ui/

# Verify frontend tools are available after copying all files
RUN cd /app/ui && \
    echo "=== FINAL VERIFICATION ===" && \
    ls -la && \
    ls -la node_modules/.bin/ | head -5 && \
    ./node_modules/.bin/eslint --version

# Set working directory to backend
WORKDIR /app/backend

# Create staticfiles directory
RUN mkdir -p /app/backend/staticfiles

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
