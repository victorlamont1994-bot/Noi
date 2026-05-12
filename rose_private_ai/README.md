# ROSE Private AI — Chromebook Functional Build

ROSE is a local-first private AI assistant for UCC, consumer-law, contract, evidence, and forensic-audit education.

This branch is optimized for a Chromebook with limited storage. It avoids heavyweight vector databases and uses a local JSONL source index.

## Chromebook verdict

Yes, this can work with 20 GB free, but use the light profile:

- Backend: FastAPI
- Model runtime: Ollama
- Recommended model: `llama3.2:3b` or another small local model
- Search index: local JSONL keyword scoring
- Avoid heavyweight vector DBs until storage is upgraded

## Install

Enable Linux on Chromebook first.

```bash
cd rose_private_ai
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/bootstrap_check.py
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd rose_private_ai
python3 -m http.server 3000 -d frontend
```

Open:

```text
http://127.0.0.1:3000
```

## Ollama

Install Ollama and pull a small model:

```bash
ollama pull llama3.2:3b
```

If that model is unavailable on your device, use any small Ollama chat model and set it in `.env`.

## Local files

Runtime data is stored locally and ignored by git:

```text
backend/data/uploads/
backend/data/index/chunks.jsonl
backend/data/audit/events.jsonl
backend/data/audit/source_ledger.jsonl
```

## Operating rule

For court-safe or audit-safe output, use strict-source mode. No source, no conclusion.
