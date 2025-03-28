FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    graphicsmagick \
    ffmpeg \
    libopencv-dev \
    python3-opencv \
    libsm6 \
    libxext6 \
    libgl1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /tmp/image_processing

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]