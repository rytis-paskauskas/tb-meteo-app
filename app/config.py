import json
from pathlib import Path
import os
import getpass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

APP_NAME = "tb-meteo-app"


def _config_path():
    if os.name == "nt":
        base = Path(os.getenv("APPDATA"))
    else:
        base = Path.home() / ".config"

    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)

    return path / "config.json"


def configure():
    print("=== ThingsBoard Configuration ===")

    endpoint = input("API endpoint: ")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    while True:    
        timezone = input("Preferred timezone (e.g. Europe/Rome): ").strip()
        try:
            ZoneInfo(timezone)
            break
        except ZoneInfoNotFoundError:
            print(f"Invalid timezone '{timezone}'. Please try again")

    config = {
        "endpoint": endpoint,
        "username": username,
        "password": password,
        "timezone": timezone,
    }

    with open(_config_path(), "w") as f:
        json.dump(config, f, indent=2)

    print(f"\nConfiguration saved to {_config_path()}")


def load_config():
    path = _config_path()

    if not path.exists():
        raise RuntimeError(
            "Configuration not found. Run the app with --configure first."
        )

    with open(path) as f:
        return json.load(f)
