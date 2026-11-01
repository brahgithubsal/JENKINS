# ─── Étape 1 : Build stage (installe les dépendances dans un venv isolé) ─────
FROM python:3.11-slim AS builder

WORKDIR /build

# Copier uniquement les fichiers de dépendances (optimise le cache Docker)
COPY requirements.txt .

# Créer un environnement virtuel propre et installer les dépendances
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip --quiet && \
    /opt/venv/bin/pip install -r requirements.txt --quiet

# ─── Étape 2 : Production stage (image finale légère) ─────────────────────────
FROM python:3.11-slim AS production

# Métadonnées de l'image
LABEL maintainer="INNOTWIST DevOps Bootcamp 2026"
LABEL description="DevOps Health Checker — Lab Jenkins CI/CD"
LABEL version="1.0.0"

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copier uniquement le venv compilé depuis le builder stage (pas pip)
COPY --from=builder /opt/venv /opt/venv

# Copier uniquement le code de l'application (pas les tests ni les configs dev)
COPY app.py .

# Définir les variables d'environnement
ENV PATH="/opt/venv/bin:$PATH"
ENV APP_ENV=production
ENV APP_VERSION=1.0.0
ENV PORT=5000

# Changer le propriétaire des fichiers
RUN chown -R appuser:appuser /app

# Basculer vers l'utilisateur non-root
USER appuser

# Exposer le port applicatif
EXPOSE 5000

# Health check intégré dans l'image
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Démarrer avec gunicorn (serveur WSGI de production)
CMD ["/opt/venv/bin/gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
