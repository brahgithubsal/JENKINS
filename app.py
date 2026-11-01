"""
DevOps Health Checker — Application Flask
Bootcamp DevOps Engineering — INNOTWIST 2026
Chapitre 4 — Lab Jenkins CI/CD Pipeline

API REST légère et autonome (sans base de données).
Expose /health, /api/info et /api/metrics pour tester le pipeline CI/CD Jenkins.
"""
import platform
import os
import socket

try:
    import shutil
    SHUTIL_OK = True
except ImportError:
    SHUTIL_OK = False

from flask import Flask, jsonify

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
ENV = os.environ.get("APP_ENV", "development")


def get_system_summary():
    """Retourne un dictionnaire d'information système."""
    summary = {
        "status": "HEALTHY",
        "version": APP_VERSION,
        "env": ENV,
        "os": platform.system(),
        "release": platform.release(),
        "hostname": socket.gethostname(),
        "python": platform.python_version(),
    }

    if SHUTIL_OK:
        try:
            total, used, free = shutil.disk_usage("/")
            summary["disk"] = {
                "total_gb": round(total / (1024 ** 3), 2),
                "used_gb": round(used / (1024 ** 3), 2),
                "free_gb": round(free / (1024 ** 3), 2),
            }
        except Exception:
            pass

    return summary


@app.route("/")
def index():
    return jsonify({
        "app": "DevOps Health Checker",
        "version": APP_VERSION,
        "message": "Bienvenue dans le lab Jenkins — Bootcamp INNOTWIST 2026",
        "endpoints": ["/health", "/api/info", "/api/metrics"],
    })


@app.route("/health")
def health():
    return jsonify({"status": "UP", "version": APP_VERSION})


@app.route("/api/info")
def info():
    return jsonify(get_system_summary())


@app.route("/api/metrics")
def metrics():
    summary = get_system_summary()
    return jsonify({
        "app_version": APP_VERSION,
        "environment": ENV,
        "system_ok": summary["status"] == "HEALTHY",
        "disk_free_gb": summary.get("disk", {}).get("free_gb", "N/A"),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=(ENV == "development"))
