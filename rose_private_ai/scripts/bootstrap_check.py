from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


def status(name: str, ok: bool, detail: str = ""):
    mark = "✅" if ok else "❌"
    print(f"{mark} {name}" + (f" — {detail}" if detail else ""))


def check_python() -> bool:
    ok = sys.version_info >= (3, 11)
    status("Python >= 3.11", ok, platform.python_version())
    return ok


def check_env() -> bool:
    env = ROOT / ".env"
    if env.exists():
        status(".env exists", True, str(env.relative_to(ROOT)))
        return True
    status(".env exists", False, "run: cp .env.example .env")
    return False


def check_dirs() -> bool:
    needed = [
        ROOT / "backend/data/uploads",
        ROOT / "backend/data/index",
        ROOT / "backend/data/audit",
    ]
    ok_all = True
    for d in needed:
        d.mkdir(parents=True, exist_ok=True)
        ok = d.exists()
        ok_all = ok_all and ok
        status(f"directory {d.relative_to(ROOT)}", ok)
    return ok_all


def check_ollama() -> bool:
    base = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    url = base + "/api/tags"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=4) as res:
            data = json.loads(res.read().decode("utf-8"))
            models = [m.get("name") for m in data.get("models", [])]
            status("Ollama reachable", True, ", ".join(models) or "no models pulled yet")
            return True
    except Exception as exc:
        status("Ollama reachable", False, f"{exc}; run: ollama serve && ollama pull llama3.2:3b")
        return False


def main():
    print("ROSE Chromebook Bootstrap Check")
    print("-" * 34)
    checks = [check_python(), check_env(), check_dirs(), check_ollama()]
    print("\nResult:", "READY" if all(checks) else "NEEDS ATTENTION")


if __name__ == "__main__":
    main()
