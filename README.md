# NAS Observability Agent

A self-hosted observability stack for OpenMediaVault NAS with a natural language LLM agent interface. Ask questions like *"is my NAS healthy?"* and get plain English answers backed by live Prometheus metrics.

## Architecture

```
OpenMediaVault NAS (192.168.1.116)
├── node-exporter      :9100   CPU, RAM, network, disk capacity
├── cadvisor           :8080   Docker container metrics (Immich, Photoprism)
├── smartctl-exporter  :9633   Disk SMART health
├── blackbox-exporter  :9115   Service uptime probes
└── prometheus         :9090   Metrics store (existing Immich instance)
    └── grafana        :3000   Dashboards (existing Immich instance)

Dell Vostro 270 (Windows, GTX 1650)
├── ollama             :11434  Local LLM (llama3.2:3b)
├── agent/             Python  FastAPI observability agent
└── open-webui         :8080   Browser chat interface
```

## Stack

| Component | Purpose | Host |
|---|---|---|
| Prometheus | Metrics storage | NAS |
| Grafana | Dashboards | NAS |
| Node Exporter | Host metrics | NAS |
| cAdvisor | Container metrics | NAS |
| smartctl Exporter | Disk SMART health | NAS |
| Blackbox Exporter | Service uptime | NAS |
| Ollama | Local LLM runtime | Dell |
| Python agent | NL→PromQL→LLM | Dell |
| Open WebUI | Chat interface | Dell |

## Setup

### Phase 1 — NAS collectors

```bash
cd nas/
# add collector services to your existing Immich compose
docker compose up -d node-exporter cadvisor smartctl-exporter blackbox-exporter
# reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

### Phase 2 — Grafana dashboards

Import these dashboard IDs from grafana.com in your Grafana UI:
- `1860` — Node Exporter Full
- `14282` — Docker container metrics (cAdvisor)
- `20204` — smartctl disk health

### Phase 3 — Ollama on Dell

```powershell
# download from https://ollama.com/download
ollama pull llama3.2:3b
ollama serve
```

### Phase 4 — Observability agent

```bash
cd agent/
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env       # edit with your Prometheus URL
uvicorn main:app --reload
```

### Phase 5 — Open WebUI

```bash
docker run -d -p 3001:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  ghcr.io/open-webui/open-webui:main
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `PROMETHEUS_URL` | `http://192.168.1.116:9090` | Prometheus endpoint |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2:3b` | Model to use |
| `AGENT_PORT` | `8000` | Agent API port |

## Hardware

- NAS: OpenMediaVault 7.7 · Debian 12 · 1 Gbps
- Dell: i7-3770K · 16 GB RAM · GTX 1650 4 GB VRAM
