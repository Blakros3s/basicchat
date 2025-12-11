# Use a lightweight Python 3.11 image as the base
FROM python:3.11-slim

# -----------------------------
# Set environment variables
# -----------------------------
# Prevent Python from writing .pyc files (compiled bytecode)
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure Python output is sent straight to terminal (useful for logs)
ENV PYTHONUNBUFFERED=1

# -----------------------------
# Set working directory inside container
# -----------------------------
WORKDIR /app

# -----------------------------
# Install system dependencies
# -----------------------------
# - postgresql-client: required if connecting to Postgres database
# - apt-get update: updates package list
# - rm -rf /var/lib/apt/lists/*: clean up cache to reduce image size
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Python dependencies
# -----------------------------
# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt /app/
# Upgrade pip and install all dependencies without cache (reduces image size)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Copy project code into container
# -----------------------------
COPY . /app/

# -----------------------------
# Expose port for the container
# -----------------------------
EXPOSE 8000

# -----------------------------
# Run migrations and start the server
# -----------------------------
# CMD executes when the container starts:
# 1. Run database migrations
# 2. Start Django development server accessible on all interfaces
CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
