# ── Build stage ─────────────────────────────────────────────────────────────
FROM python:3.9-slim AS build

# Install build dependencies for compiling Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ── Runtime stage ───────────────────────────────────────────────────────────
FROM python:3.9-slim

WORKDIR /app

# Copy installed dependencies from build stage
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy app code
COPY app ./app

# Fix permissions so Kubernetes can read/execute files
RUN chmod -R 755 /app

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
