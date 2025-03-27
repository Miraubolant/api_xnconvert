FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    graphicsmagick \
    ffmpeg \
    libvips-tools \
    wget \
    unzip \
    gimp \
    libopencv-dev \
    python3-opencv \
    libsm6 \
    libxext6 \
    libgl1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install XnConvert (utilisez l'exécutable XnConvert au lieu de nconvert)
RUN mkdir -p /tmp/xnconvert && \
    cd /tmp/xnconvert && \
    wget https://download.xnview.com/XnConvert-linux-x64.tgz && \
    tar -xzvf XnConvert-linux-x64.tgz && \
    cp /tmp/xnconvert/XnConvert/XnConvert /usr/local/bin/xnconvert && \
    chmod +x /usr/local/bin/xnconvert && \
    mkdir -p /usr/local/share/XnConvert && \
    cp -r /tmp/xnconvert/XnConvert/Plugins /usr/local/share/XnConvert/ && \
    rm -rf /tmp/xnconvert

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