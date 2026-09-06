from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_PATH = Path(__file__).with_name("models.json")
REPO_ROOT = Path(__file__).resolve().parent.parent
# pass


def load_dotenv() -> None:
    path = Path(os.environ.get("ENV_FILE", REPO_ROOT / ".env"))
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_dotenv()


def load_models() -> list[dict]:
    path = Path(os.environ.get("MODELS_CONFIG", DEFAULT_PATH))
    with path.open(encoding="utf-8") as handle:
        models = json.load(handle)["models"]
    return [m for m in models if m.get("enabled")]
