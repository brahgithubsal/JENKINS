"""
Tests unitaires — DevOps Health Checker
Bootcamp DevOps Engineering — INNOTWIST 2026
Chapitre 4 — Lab Jenkins CI/CD
"""
import pytest
import sys
import os

# S'assurer que app.py est trouvable
sys.path.insert(0, os.path.dirname(__file__))

from app import app, get_system_summary


@pytest.fixture
def client():
    """Client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ─── Tests unitaires de la fonction get_system_summary() ─────────────────────

def test_system_summary_status():
    """Le statut doit être HEALTHY."""
    summary = get_system_summary()
    assert summary["status"] == "HEALTHY"


def test_system_summary_has_os():
    """Le résumé doit contenir des infos OS."""
    summary = get_system_summary()
    assert "os" in summary
    assert len(summary["os"]) > 0


def test_system_summary_has_release():
    """Le résumé doit contenir la version de l'OS."""
    summary = get_system_summary()
    assert "release" in summary


def test_system_summary_has_python_version():
    """Le résumé doit contenir la version Python."""
    summary = get_system_summary()
    assert "python" in summary
    assert summary["python"].count(".") >= 1


def test_disk_metrics():
    """Les métriques disque doivent être des nombres positifs."""
    summary = get_system_summary()
    if "disk" in summary:
        assert summary["disk"]["total_gb"] > 0
        assert summary["disk"]["free_gb"] >= 0
        assert summary["disk"]["used_gb"] >= 0


# ─── Tests d'intégration des routes HTTP ────────────────────────────────────

def test_route_index(client):
    """GET / doit retourner 200 avec les infos de l'app."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "app" in data
    assert "version" in data
    assert "endpoints" in data


def test_route_health(client):
    """GET /health doit retourner status UP."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"


def test_route_api_info(client):
    """GET /api/info doit retourner les informations système."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "HEALTHY"
    assert "os" in data
    assert "python" in data


def test_route_api_metrics(client):
    """GET /api/metrics doit retourner les métriques applicatives."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.get_json()
    assert "app_version" in data
    assert "system_ok" in data
    assert data["system_ok"] is True


def test_404_not_found(client):
    """Une route inconnue doit retourner 404."""
    response = client.get("/route-inconnue")
    assert response.status_code == 404
