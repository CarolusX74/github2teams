import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "config.json"

# Clave secreta usada para verificar la firma HMAC de GitHub
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "").encode()
# Si no se define, queda como b"" (y la verificación fallará, como debe ser)

def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def get_webhooks_for_repo(repo_full_name):
    config = load_config()
    return config.get("repos", {}).get(repo_full_name, [])

    
def get_webhooks_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_config(config: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
