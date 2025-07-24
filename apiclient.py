import requests
from config import load_config
cfg = load_config()

# API configuration (can move these to a config file or env vars)
DEPLOYMENT_ID = 'gpt-4.1-mini'
API_URL = cfg.get("API_URL")
API_KEY = cfg.get("API_KEY")

HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0',
    'Ocp-Apim-Subscription-Key': API_KEY
}

def ask_gpt(prompt, temperature=0.7, model=DEPLOYMENT_ID):
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "model": model
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"API call failed: {e}")
        return None
