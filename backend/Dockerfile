# Consider using Bookworm for more recent libraries
FROM python:3.9-slim-bookworm  

# Set working directory and create required directories
WORKDIR /app
RUN mkdir -p src models cache

# Update CA certificates and install base dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install system dependencies with retries
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    libmagic1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && chmod -R 777 /app/models /app/cache

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libstdc++-12-dev \
    libpthread-stubs0-dev \
    libomp-dev  # OpenMP (needed for llama.cpp)

# Set compiler and linker flags to include pthread
ENV CFLAGS="-pthread"
ENV CXXFLAGS="-pthread"

# If issues persist, try "-lpthread" instead
ENV LDFLAGS="-pthread"  

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment configuration
ENV PYTHONPATH="${PYTHONPATH}:/app/src"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
