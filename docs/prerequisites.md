# Project Setup Guide

## Prerequisites
Before setting up the project, ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **pip** (Python package manager)
- **Virtual environment** (`venv`)
- **Docker & Docker Compose** ([Install Guide](https://docs.docker.com/get-docker/))
- **C++ Compiler** (Required for `llama-cpp-python`)
  - Ubuntu/Debian: `sudo apt install build-essential cmake`
  - Fedora: `sudo dnf groupinstall "Development Tools" && sudo dnf install cmake`
  - Arch Linux: `sudo pacman -S base-devel cmake`
  - macOS: `xcode-select --install && brew install gcc cmake`
  - Windows: Install **Visual Studio Build Tools** ([Download](https://visualstudio.microsoft.com/visual-cpp-build-tools/)) and enable **C++ CMake tools for Windows**

## Setting Up the Project

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/my-chatbot.git
cd my-chatbot/backend
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate    # Windows
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Additional Dependencies
```bash
pip install fastapi
pip install redis
pip install pydantic-settings
pip install langchain-community
pip install langchain-chroma
pip install langchain-huggingface
pip install transformers
pip install whisper
pip install chromadb
pip install python-magic  # Use python-magic-bin on Windows
pip install PyPDF2
pip install opencv-python
pip install python-multipart
pip install llama-cpp-python
```

### 5. Ensure C++ Compiler and CMake are Set Up
If you encounter build errors for `llama-cpp-python`, manually set the compiler:
```bash
export CC=gcc
export CXX=g++
```
Then retry installation:
```bash
pip install llama-cpp-python
```

### 6. Verify Installation
```bash
python -c "import fastapi, redis, pydantic, langchain_community, chromadb, whisper, transformers, cv2, PyPDF2, magic, llama_cpp; print('All dependencies installed successfully!')"
```

### 7. Run the Application
```bash
uvicorn src.main:app --reload
```

---

# Docker Setup

## Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN apt update && apt install -y build-essential cmake && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## docker-compose.yml
```yaml
version: "3.8"

services:
  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - .:/app
    depends_on:
      - redis

  redis:
    image: "redis:alpine"
    ports:
      - "6379:6379"
```

## Running the Application with Docker
### 1. Build the Docker Image
```bash
docker-compose build
```

### 2. Start the Services
```bash
docker-compose up -d
```

### 3. Stop the Services
```bash
docker-compose down
```

---

Your chatbot application is now set up and running in a containerized environment. 🚀

