# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directory for custom tools
RUN mkdir -p custom_tools

# Set environment variables
ENV PYTHONPATH=/app
ENV CUSTOM_TOOLS_DIR=/app/custom_tools

# Expose port
EXPOSE 3001

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001", "--proxy-headers"] 