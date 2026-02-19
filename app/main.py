"""
app/main.py — DevOps REST API
A production-style FastAPI backend with system monitoring endpoints.
Demonstrates REST API development, Docker deployment, and CI/CD integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import Dict, Any
import platform
import psutil
import os

# ── App initialization ────────────────────────────────────────────────────────

app = FastAPI(
    title="DevOps REST API",
    description="System monitoring and health check API built with FastAPI",
    version="1.0.0",
    contact={
        "name": "Josimar Arias",
        "email": "josimar85209@gmail.com",
        "url": "https://github.com/josimar549",
    },
)

# CORS middleware (allows frontend apps to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper functions ──────────────────────────────────────────────────────────

def get_cpu_info() -> Dict[str, Any]:
    """Collect CPU metrics."""
    return {
        "percent": round(psutil.cpu_percent(interval=1), 2),
        "percent_per_core": [round(p, 2) for p in psutil.cpu_percent(interval=0.1, percpu=True)],
        "core_count": psutil.cpu_count(logical=True),
        "core_count_physical": psutil.cpu_count(logical=False),
        "load_avg": [round(x, 2) for x in psutil.getloadavg()],
    }


def get_memory_info() -> Dict[str, Any]:
    """Collect memory metrics."""
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "ram": {
            "total_gb": round(ram.total / 1e9, 2),
            "used_gb": round(ram.used / 1e9, 2),
            "available_gb": round(ram.available / 1e9, 2),
            "percent": round(ram.percent, 2),
        },
        "swap": {
            "total_gb": round(swap.total / 1e9, 2),
            "used_gb": round(swap.used / 1e9, 2),
            "percent": round(swap.percent, 2),
        },
    }


def get_disk_info(path: str = "/") -> Dict[str, Any]:
    """Collect disk metrics for a given path."""
    try:
        usage = psutil.disk_usage(path)
        io = psutil.disk_io_counters()
        result = {
            "path": path,
            "total_gb": round(usage.total / 1e9, 2),
            "used_gb": round(usage.used / 1e9, 2),
            "free_gb": round(usage.free / 1e9, 2),
            "percent": round(usage.percent, 2),
        }
        if io:
            result["io"] = {
                "read_mb": round(io.read_bytes / 1e6, 2),
                "write_mb": round(io.write_bytes / 1e6, 2),
            }
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid disk path: {path}")


def get_network_info() -> Dict[str, Any]:
    """Collect network I/O metrics."""
    net = psutil.net_io_counters()
    return {
        "bytes_sent_mb": round(net.bytes_sent / 1e6, 2),
        "bytes_recv_mb": round(net.bytes_recv / 1e6, 2),
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
        "errors_in": net.errin,
        "errors_out": net.errout,
    }


def get_system_info() -> Dict[str, Any]:
    """Collect static system information."""
    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
    uptime_seconds = int((datetime.now(timezone.utc) - boot_time).total_seconds())
    
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "boot_time": boot_time.isoformat(),
        "uptime_seconds": uptime_seconds,
        "process_count": len(psutil.pids()),
    }


def get_top_processes(limit: int = 5) -> list:
    """Return top N processes by CPU usage."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            procs.append({
                "pid": p.info["pid"],
                "name": p.info["name"],
                "cpu_percent": round(p.info["cpu_percent"] or 0, 2),
                "memory_percent": round(p.info["memory_percent"] or 0, 2),
                "status": p.info["status"],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(procs, key=lambda x: x["cpu_percent"], reverse=True)[:limit]


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "api": "DevOps REST API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "system": "/system",
            "metrics": "/metrics",
            "cpu": "/metrics/cpu",
            "memory": "/metrics/memory",
            "disk": "/metrics/disk",
            "network": "/metrics/network",
            "processes": "/processes",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring systems.
    Returns 200 OK if the API is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "uptime_seconds": get_system_info()["uptime_seconds"],
    }


@app.get("/system", tags=["System"])
async def get_system():
    """
    Get static system information.
    Returns hostname, OS, architecture, Python version, boot time, and uptime.
    """
    return get_system_info()


@app.get("/metrics", tags=["Metrics"])
async def get_all_metrics():
    """
    Get all system metrics in a single response.
    Includes CPU, memory, disk, network, and top processes.
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": get_system_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info("/"),
        "network": get_network_info(),
        "top_processes": get_top_processes(5),
    }


@app.get("/metrics/cpu", tags=["Metrics"])
async def get_cpu():
    """Get CPU usage metrics."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu": get_cpu_info(),
    }


@app.get("/metrics/memory", tags=["Metrics"])
async def get_memory():
    """Get memory (RAM + swap) usage metrics."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "memory": get_memory_info(),
    }


@app.get("/metrics/disk", tags=["Metrics"])
async def get_disk(path: str = "/"):
    """
    Get disk usage metrics for a specific path.
    
    Parameters:
    - path: Disk path to check (default: /)
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "disk": get_disk_info(path),
    }


@app.get("/metrics/network", tags=["Metrics"])
async def get_network():
    """Get network I/O metrics."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "network": get_network_info(),
    }


@app.get("/processes", tags=["Processes"])
async def get_processes(limit: int = 10):
    """
    Get top processes by CPU usage.
    
    Parameters:
    - limit: Number of processes to return (default: 10, max: 50)
    """
    if limit > 50:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 50")
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": limit,
        "processes": get_top_processes(limit),
    }


# ── Exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The endpoint {request.url.path} does not exist",
            "available_endpoints": [
                "/", "/health", "/system", "/metrics",
                "/metrics/cpu", "/metrics/memory", "/metrics/disk",
                "/metrics/network", "/processes", "/docs",
            ],
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        },
    )


# ── Startup event ─────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    print("=" * 60)
    print("🚀 DevOps REST API Starting...")
    print(f"   Hostname: {platform.node()}")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {platform.python_version()}")
    print(f"   Docs: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
