# Use official Python image 
FROM python:3.11-slim

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Redis-client dependencies
RUN apt-get update && apt-get install -y redis-tools

# Copy requirement.txt file to /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port 8000 for the app
EXPOSE 8000

# Start the service of daphne
CMD service redis-server start && daphne -b 0.0.0.0 -p 8000 project.asgi:application
