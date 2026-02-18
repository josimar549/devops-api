"""
tests/test_api.py
Unit and integration tests for the DevOps REST API.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Create test client
client = TestClient(app)


# ── Root endpoint tests ───────────────────────────────────────────────────────

class TestRoot:
    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_has_api_info(self):
        response = client.get("/")
        data = response.json()
        assert "api" in data
        assert "version" in data
        assert "endpoints" in data

    def test_root_lists_endpoints(self):
        response = client.get("/")
        data = response.json()
        endpoints = data["endpoints"]
        assert "/health" in endpoints.values()
        assert "/metrics" in endpoints.values()


# ── Health endpoint tests ─────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_status(self):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_has_timestamp(self):
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
        assert data["timestamp"].endswith("Z")

    def test_health_has_uptime(self):
        response = client.get("/health")
        data = response.json()
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] > 0


# ── System endpoint tests ─────────────────────────────────────────────────────

class TestSystem:
    def test_system_returns_200(self):
        response = client.get("/system")
        assert response.status_code == 200

    def test_system_has_required_fields(self):
        response = client.get("/system")
        data = response.json()
        required = ["hostname", "os", "os_release", "architecture", 
                   "python_version", "boot_time", "uptime_seconds"]
        for field in required:
            assert field in data

    def test_system_hostname_not_empty(self):
        response = client.get("/system")
        data = response.json()
        assert len(data["hostname"]) > 0

    def test_system_uptime_positive(self):
        response = client.get("/system")
        data = response.json()
        assert data["uptime_seconds"] > 0


# ── Metrics endpoint tests ────────────────────────────────────────────────────

class TestMetrics:
    def test_metrics_returns_200(self):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_has_all_sections(self):
        response = client.get("/metrics")
        data = response.json()
        sections = ["timestamp", "system", "cpu", "memory", "disk", 
                   "network", "top_processes"]
        for section in sections:
            assert section in data

    def test_metrics_cpu_has_percent(self):
        response = client.get("/metrics")
        data = response.json()
        assert "percent" in data["cpu"]
        assert 0 <= data["cpu"]["percent"] <= 100

    def test_metrics_memory_has_ram(self):
        response = client.get("/metrics")
        data = response.json()
        assert "ram" in data["memory"]
        assert "percent" in data["memory"]["ram"]
        assert 0 <= data["memory"]["ram"]["percent"] <= 100

    def test_metrics_disk_has_path(self):
        response = client.get("/metrics")
        data = response.json()
        assert "path" in data["disk"]
        assert data["disk"]["path"] == "/"


# ── Individual metric endpoint tests ──────────────────────────────────────────

class TestCpuEndpoint:
    def test_cpu_returns_200(self):
        response = client.get("/metrics/cpu")
        assert response.status_code == 200

    def test_cpu_has_timestamp_and_cpu(self):
        response = client.get("/metrics/cpu")
        data = response.json()
        assert "timestamp" in data
        assert "cpu" in data

    def test_cpu_percent_in_range(self):
        response = client.get("/metrics/cpu")
        data = response.json()
        assert 0 <= data["cpu"]["percent"] <= 100


class TestMemoryEndpoint:
    def test_memory_returns_200(self):
        response = client.get("/metrics/memory")
        assert response.status_code == 200

    def test_memory_has_ram_and_swap(self):
        response = client.get("/metrics/memory")
        data = response.json()
        assert "memory" in data
        assert "ram" in data["memory"]
        assert "swap" in data["memory"]


class TestDiskEndpoint:
    def test_disk_returns_200(self):
        response = client.get("/metrics/disk")
        assert response.status_code == 200

    def test_disk_default_path(self):
        response = client.get("/metrics/disk")
        data = response.json()
        assert data["disk"]["path"] == "/"

    def test_disk_custom_path(self):
        response = client.get("/metrics/disk?path=/tmp")
        data = response.json()
        assert data["disk"]["path"] == "/tmp"

    def test_disk_invalid_path_returns_400(self):
        response = client.get("/metrics/disk?path=/nonexistent/path/that/does/not/exist")
        assert response.status_code == 400


class TestNetworkEndpoint:
    def test_network_returns_200(self):
        response = client.get("/metrics/network")
        assert response.status_code == 200

    def test_network_has_sent_and_recv(self):
        response = client.get("/metrics/network")
        data = response.json()
        assert "network" in data
        assert "bytes_sent_mb" in data["network"]
        assert "bytes_recv_mb" in data["network"]


# ── Processes endpoint tests ──────────────────────────────────────────────────

class TestProcesses:
    def test_processes_returns_200(self):
        response = client.get("/processes")
        assert response.status_code == 200

    def test_processes_default_limit(self):
        response = client.get("/processes")
        data = response.json()
        assert "processes" in data
        assert len(data["processes"]) <= 10

    def test_processes_custom_limit(self):
        response = client.get("/processes?limit=5")
        data = response.json()
        assert len(data["processes"]) <= 5

    def test_processes_limit_too_high_returns_400(self):
        response = client.get("/processes?limit=100")
        assert response.status_code == 400

    def test_processes_have_required_fields(self):
        response = client.get("/processes?limit=1")
        data = response.json()
        if len(data["processes"]) > 0:
            proc = data["processes"][0]
            assert "pid" in proc
            assert "name" in proc
            assert "cpu_percent" in proc
            assert "memory_percent" in proc


# ── Error handling tests ──────────────────────────────────────────────────────

class TestErrorHandling:
    def test_404_custom_handler(self):
        response = client.get("/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "available_endpoints" in data

    def test_404_lists_real_endpoints(self):
        response = client.get("/nonexistent")
        data = response.json()
        endpoints = data["available_endpoints"]
        assert "/health" in endpoints
        assert "/metrics" in endpoints
        assert "/docs" in endpoints


# ── OpenAPI docs tests ────────────────────────────────────────────────────────

class TestDocs:
    def test_openapi_schema_exists(self):
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_docs_page_exists(self):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_page_exists(self):
        response = client.get("/redoc")
        assert response.status_code == 200
