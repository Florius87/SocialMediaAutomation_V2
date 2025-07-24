import os

def load_config(filename="config.txt"):
    config = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                if line.strip() and not line.strip().startswith("#"):
                    key, sep, value = line.strip().partition("=")
                    if sep:
                        config[key.strip()] = value.strip()
    return config

def get_platforms_from_config(filename="config.txt"):
    config = load_config(filename)
    # Split, strip, and ignore blanks
    return [p.strip() for p in config.get("PLATFORMS", "").split(",") if p.strip()]