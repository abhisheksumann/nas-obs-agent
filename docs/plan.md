# Project plan

## Phase 0 — Repo setup ✅
- Initialised git repo
- Pushed to github.com/abhisheksumann/nas-obs-agent

## Phase 1 — NAS collectors (next)
- Copy nas/prometheus.yml to NAS, replacing existing file
- Add collector services to Immich compose and start them
- Reload Prometheus: curl -X POST http://192.168.1.116:9090/-/reload
- Verify at http://192.168.1.116:9090/targets

## Phase 2 — Grafana dashboards
- Add Prometheus datasource in Grafana UI
- Import dashboards: 1860, 14282, 20204

## Phase 3 — Ollama on Dell
- Install Ollama for Windows, pull llama3.2:3b

## Phase 4 — Observability agent
- venv + pip install requirements.txt
- Copy .env.example to .env, set PROMETHEUS_URL
- uvicorn main:app --reload

## Phase 5 — Open WebUI
- Run Open WebUI container pointing at Ollama