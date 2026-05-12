import requests
from backend.config import settings


class LLMError(RuntimeError):
    pass


def ollama_chat(system_prompt: str, user_prompt: str) -> str:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": 0.2, "top_p": 0.9},
    }

    try:
        response = requests.post(url, json=payload, timeout=180)
    except requests.RequestException as exc:
        raise LLMError(
            f"Could not reach Ollama at {settings.ollama_base_url}. "
            "Confirm Ollama is running and the model is pulled."
        ) from exc

    if response.status_code >= 400:
        raise LLMError(f"Ollama HTTP {response.status_code}: {response.text}")

    data = response.json()
    return data.get("message", {}).get("content", "").strip()
