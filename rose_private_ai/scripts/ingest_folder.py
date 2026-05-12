from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.core.ingest import SUPPORTED_EXTENSIONS
from backend.core.rag import ingest_file


def main(folder: str):
    base = Path(folder)
    if not base.exists():
        raise SystemExit(f"Folder not found: {base}")

    count = 0
    for path in base.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            print(f"Ingesting {path}")
            print(ingest_file(path))
            count += 1
    print(f"Done. Files ingested: {count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/ingest_folder.py <folder>")
    main(sys.argv[1])
