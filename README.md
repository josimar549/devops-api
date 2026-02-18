# ⚡ DevOps REST API

![CI](https://github.com/josimar549/devops-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)

A production-grade REST API for system monitoring and health checks. Built with FastAPI, containerized with Docker, and deployed via CI/CD pipelines.

**Live API Docs:** Auto-generated at `/docs` (Swagger UI) and `/redoc` (ReDoc)

---

## Features

- **RESTful endpoints** — `/health`, `/system`, `/metrics`, `/processes`
- **Real-time system metrics** — CPU, memory, disk, network via `psutil`
- **Auto-generated API docs** — Interactive Swagger UI at `/docs`
- **CORS-enabled** — Ready for frontend integration
- **Dockerized** — Multi-stage build with health checks
- **CI/CD pipeline** — GitHub Actions: lint → test → Docker build → integration tests
- **Production patterns** — Non-root container user, structured logging, error handling

---

## Quick Start

### Run with Python (local development)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

Then open **http://localhost:8000/docs** to see the interactive API documentation.

### Run with Docker

```bash
# Build image
docker build -t devops-api .

# Run container
docker run -d -p 8000:8000 --name api devops-api

# View logs
docker logs -f api

# Stop
docker stop api && docker rm api
```

### Run with Docker Compose

```bash
docker compose up -d       # Start in background
docker compose logs -f     # Tail logs
docker compose down        # Stop
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and available endpoints |
| `/health` | GET | Health check for load balancers |
| `/system` | GET | Static system info (hostname, OS, uptime) |
| `/metrics` | GET | All system metrics in one response |
| `/metrics/cpu` | GET | CPU usage and load average |
| `/metrics/memory` | GET | RAM and swap usage |
| `/metrics/disk` | GET | Disk usage (supports `?path=/custom`) |
| `/metrics/network` | GET | Network I/O statistics |
| `/processes` | GET | Top processes by CPU (supports `?limit=N`) |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API docs (ReDoc) |

---

## Example API Responses

**GET `/health`**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-01T14:30:00Z",
  "uptime_seconds": 18430
}
```

**GET `/metrics/cpu`**
```json
{
  "timestamp": "2025-06-01T14:30:00Z",
  "cpu": {
    "percent": 23.4,
    "percent_per_core": [18.2, 31.5, 20.1, 24.8],
    "core_count": 4,
    "core_count_physical": 4,
    "load_avg": [1.23, 1.45, 1.32]
  }
}
```

**GET `/metrics`** (all metrics combined)
```json
{
  "timestamp": "2025-06-01T14:30:00Z",
  "system": { "hostname": "server-01", "os": "Linux", ... },
  "cpu": { "percent": 23.4, ... },
  "memory": { "ram": { "percent": 68.2, ... }, "swap": { ... } },
  "disk": { "path": "/", "percent": 42.1, ... },
  "network": { "bytes_sent_mb": 1234.5, ... },
  "top_processes": [ ... ]
}
```

---

## Project Structure

```
devops-api/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_api.py          # pytest test suite (40+ tests)
├── .github/
│   └── workflows/
│       └── ci.yml           # CI pipeline: lint → test → Docker
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Compose setup with health checks
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern async Python web framework |
| **Uvicorn** | ASGI server for running FastAPI |
| **psutil** | Cross-platform system metrics library |
| **pytest** | Testing framework (40+ tests) |
| **Docker** | Containerization with multi-stage builds |
| **GitHub Actions** | CI/CD automation |

---

## Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## CI/CD Pipeline

Every push to `main` triggers:
1. **Lint** — flake8 checks for syntax errors and style issues
2. **Unit tests** — pytest runs 40+ tests covering all endpoints
3. **Docker build** — multi-stage image build
4. **Integration tests** — spin up container, test live endpoints via curl
5. **Health check** — verify `/health` endpoint returns `healthy`

See `.github/workflows/ci.yml` for full pipeline definition.

---

## What I Learned / Demonstrated

- Building production-grade REST APIs with **FastAPI** and automatic OpenAPI docs
- Async Python web development with **Uvicorn** ASGI server
- Writing comprehensive test suites with **pytest** (unit + integration tests)
- **Dockerizing** Python applications with multi-stage builds and non-root users
- Implementing **health checks** for container orchestration (Docker, Kubernetes)
- **CI/CD pipelines** with GitHub Actions (lint → test → build → deploy)
- RESTful API design patterns and error handling
- System monitoring and metrics collection via **psutil**

---

## Deployment

This API is designed to run in:
- **Docker containers** (single-instance or orchestrated)
- **Kubernetes** (with Deployment, Service, ConfigMap, HPA)
- **Cloud platforms** (AWS ECS, Google Cloud Run, Azure Container Apps)
- **VM instances** with systemd service management

Example systemd service file included in `/docs/systemd/devops-api.service`.

---

## Author

**Josimar Arias** — Software Engineer · Mesa, AZ  
[josimar85209@gmail.com](mailto:josimar85209@gmail.com) · [GitHub](https://github.com/josimar549) · [Portfolio](https://josimar549.github.io)

---

## License

MIT
