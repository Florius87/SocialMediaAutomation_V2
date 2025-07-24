import requests
from config import load_config

cfg = load_config()

DEPLOYMENT_ID = cfg.get("DEPLOYMENT_ID", "gpt-4.1-mini")
API_URL = cfg.get("API_URL")
API_KEY = cfg.get("API_KEY")

HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0',
    'Ocp-Apim-Subscription-Key': API_KEY
}

def ask_figure_api(prompt, image_url=None, temperature=0.7, model=None):
    """
    Sends a prompt (optionally with image_url) to the API and returns the response text.
    If image_url is supplied, both text and image are included as per OpenAI API format.
    """
    if not model:
        model = DEPLOYMENT_ID

    if image_url:
        # Compose as multimodal per OpenAI/ChatGPT vision API
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
    else:
        messages = [{
            "role": "user",
            "content": prompt
        }]

    payload = {
        "messages": messages,
        "temperature": temperature,
        "model": model
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Change this depending on your API format
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"FigureAPI call failed: {e}")
        return None

# Example usage (remove or comment for production)
if __name__ == "__main__":
    print(ask_figure_api("Describe this image for a Pinterest audience:", image_url="https://yourimageurl.com/img.png"))
    print(ask_figure_api("Summarize this text for Pinterest:", image_url=None))
