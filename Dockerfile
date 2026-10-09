FROM node:24-bookworm-slim AS frontend
WORKDIR /build/src/frontend
COPY src/frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY src/frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt requirements-teams.txt ./
ARG INSTALL_TEAMS_BOT=false
RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$INSTALL_TEAMS_BOT" = "true" ]; then pip install --no-cache-dir -r requirements-teams.txt; fi
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY main.py README.md LICENSE THIRD_PARTY_NOTICES.md ./
COPY --from=frontend /build/src/api/static/ ./src/api/static/
RUN useradd --create-home netra && mkdir -p sqlite_db chat_sessions logs && chown -R netra:netra /app
USER netra
EXPOSE 8001
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8001"]
