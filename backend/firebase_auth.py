import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during setup
    load_dotenv = None

try:
    import firebase_admin
    from firebase_admin import auth, credentials
except ImportError:  # pragma: no cover - optional during setup
    firebase_admin = None
    auth = None
    credentials = None

REPO_ROOT = Path(__file__).resolve().parent.parent
_initialized = False

if load_dotenv is not None:
    load_dotenv(REPO_ROOT / ".env")


def _credentials_path() -> Path | None:
    raw_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "").strip()
    if not raw_path:
        return None

    path = Path(raw_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path if path.is_file() else None


def get_firebase_web_config() -> dict | None:
    config = {
        "apiKey": os.getenv("FIREBASE_API_KEY", "").strip(),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "").strip(),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", "").strip(),
        "appId": os.getenv("FIREBASE_APP_ID", "").strip(),
    }
    if not all(config.values()):
        return None
    return config


def init_firebase() -> bool:
    global _initialized
    if _initialized:
        return True
    if firebase_admin is None or credentials is None:
        return False

    # Try loading from the JSON string environment variable first (great for production/Render)
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    if service_account_json:
        import json
        try:
            cert_dict = json.loads(service_account_json)
            firebase_admin.initialize_app(credentials.Certificate(cert_dict))
            _initialized = True
            return True
        except ValueError as exc:
            try:
                firebase_admin.get_app()
                _initialized = True
                return True
            except ValueError:
                if "already exists" not in str(exc).lower():
                    print(f"[firebase] Failed to initialize Firebase using service account JSON: {exc}")
        except Exception as exc:
            print(f"[firebase] Failed to initialize Firebase using service account JSON: {exc}")

    # Fallback to local credential file path
    credential_path = _credentials_path()
    if credential_path is None:
        return False

    try:
        firebase_admin.initialize_app(credentials.Certificate(str(credential_path)))
    except ValueError as exc:
        try:
            firebase_admin.get_app()
        except ValueError:
            if "already exists" not in str(exc).lower():
                return False
    except Exception:
        return False

    _initialized = True
    return True


def verify_firebase_id_token(id_token: str) -> dict | None:
    if not id_token or auth is None or not init_firebase():
        print("[firebase] verify_firebase_id_token: skipped — auth not initialized or empty token")
        return None

    try:
        return auth.verify_id_token(id_token)
    except Exception as exc:
        print(f"[firebase] Token verification failed: {type(exc).__name__}: {exc}")
        return None
