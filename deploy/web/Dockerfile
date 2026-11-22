FROM python:3.12.5-slim-bookworm@sha256:c24c34b502635f1f7c4e99dc09a2cbd85d480b7dcfd077198c6b5af138906390 AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    XDG_CACHE_HOME=/tmp/.cache
WORKDIR /app
RUN groupadd --gid 10001 appuser && useradd --uid 10001 --gid appuser --create-home appuser

FROM base AS api
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && pip check
COPY --chown=appuser:appuser deploy/__init__.py ./deploy/__init__.py
COPY --chown=appuser:appuser deploy/web/__init__.py ./deploy/web/__init__.py
COPY --chown=appuser:appuser deploy/web/api/ ./deploy/web/api/
COPY --chown=appuser:appuser src/__init__.py src/config.py src/predict.py ./src/
COPY --chown=appuser:appuser outputs/models/serving/logistic_regression_drybean.joblib outputs/models/serving/model_manifest.json ./outputs/models/serving/
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=3)"]
CMD ["python", "-m", "uvicorn", "deploy.web.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

FROM base AS dashboard
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && pip check
COPY --chown=appuser:appuser deploy/__init__.py ./deploy/__init__.py
COPY --chown=appuser:appuser deploy/web/__init__.py ./deploy/web/__init__.py
COPY --chown=appuser:appuser deploy/web/api/__init__.py deploy/web/api/schemas.py ./deploy/web/api/
COPY --chown=appuser:appuser deploy/web/dashboard/ ./deploy/web/dashboard/
COPY --chown=appuser:appuser deploy/web/main.py ./deploy/web/main.py
COPY --chown=appuser:appuser deploy/web/.streamlit/ ./deploy/web/.streamlit/
USER appuser
EXPOSE 8501
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"]
CMD ["python", "-m", "streamlit", "run", "deploy/web/main.py", "--server.address=0.0.0.0", "--server.port=8501"]
