import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during bootstrap
    load_dotenv = None

from secure_it import create_app


BASE_DIR = Path(__file__).resolve().parent

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")


app = create_app()


def _get_port() -> int:
    port_value = os.getenv("PORT", "5000").strip()
    try:
        port = int(port_value)
    except ValueError:
        port = 5000
    return port if 1 <= port <= 65535 else 5000


def _is_debug_enabled() -> bool:
    return os.getenv("NODE_ENV", "development").strip().lower() == "development"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=_get_port(), debug=_is_debug_enabled())
