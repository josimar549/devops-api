# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --target=/build/deps -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="Josimar Arias <josimar85209@gmail.com>" \
      description="DevOps REST API - System monitoring FastAPI backend" \
      version="1.0.0"

WORKDIR /app

# Copy dependencies and application
COPY --from=builder /build/deps /app/deps
COPY app/ /app/app/

# Add deps to Python path
ENV PYTHONPATH="/app/deps:/app"
ENV PYTHONUNBUFFERED=1

# Create non-root user (security best practice)
RUN useradd --system --no-create-home apiuser && \
    chown -R apiuser:apiuser /app

USER apiuser

# Expose port
EXPOSE 8000

# Health check (Docker will periodically verify the container is healthy)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the API
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
