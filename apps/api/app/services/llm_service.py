import logging

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self.url = f"{settings.ollama_url.rstrip('/')}/api/generate"
        self.model = settings.ollama_model

    def generate_response(self, prompt: str) -> str | None:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
            logger.info(f"Sending prompt to Ollama model {self.model} at {self.url}...")

            response = httpx.post(self.url, json=payload, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                logger.warning(
                    f"Ollama returned status code {response.status_code}: {response.text}"
                )
                return None
        except Exception as e:
            logger.warning(f"Failed to communicate with Ollama: {e}")
            return None
