import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file at project root
root_dir = Path(__file__).resolve().parent.parent
env_path = root_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from app import create_app

env_name = os.environ.get("FLASK_ENV", "development")
app = create_app(env_name)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1").lower() in ("1", "true")
    print(f"[*] CyberQuest Command Center starting on http://127.0.0.1:{port}")
    print("[*] Environment:", env_name)
    app.run(host="127.0.0.1", port=port, debug=debug)
