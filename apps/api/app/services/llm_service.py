import logging

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self.url = f"{settings.ollama_url.rstrip('/')}/api/generate"
        self.model = settings.ollama_model

    def generate_response(
        self,
        prompt: str,
        provider: str = "ollama",
        api_key: str | None = None,
        model: str | None = None,
        ollama_url: str | None = None,
    ) -> str | None:
        if provider == "openai":
            return self._call_openai(prompt, api_key, model)
        elif provider == "gemini":
            return self._call_gemini(prompt, api_key, model)
        else:
            return self._call_ollama(prompt, model, ollama_url)

    def _call_ollama(self, prompt: str, model: str | None, ollama_url: str | None) -> str | None:
        target_url = (ollama_url or settings.ollama_url).rstrip("/") + "/api/generate"
        target_model = model or settings.ollama_model
        try:
            payload = {
                "model": target_model,
                "prompt": prompt,
                "stream": False,
            }
            logger.info(f"Sending prompt to Ollama model {target_model} at {target_url}...")
            response = httpx.post(target_url, json=payload, timeout=30.0)
            if response.status_code == 200:
                return response.json().get("response", "")
            logger.warning(f"Ollama returned {response.status_code}: {response.text}")
            return None
        except Exception as e:
            logger.warning(f"Ollama call failed: {e}")
            return None

    def _call_openai(self, prompt: str, api_key: str | None, model: str | None) -> str | None:
        if not api_key:
            logger.warning("OpenAI API key is missing.")
            return None
        target_model = model or "gpt-4o-mini"
        target_url = "https://api.openai.com/v1/chat/completions"
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": target_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }
            logger.info(f"Sending prompt to OpenAI model {target_model}...")
            response = httpx.post(target_url, headers=headers, json=payload, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            logger.warning(f"OpenAI returned {response.status_code}: {response.text}")
            return None
        except Exception as e:
            logger.warning(f"OpenAI call failed: {e}")
            return None

    def _call_gemini(self, prompt: str, api_key: str | None, model: str | None) -> str | None:
        if not api_key:
            logger.warning("Gemini API key is missing.")
            return None
        target_model = model or "gemini-1.5-flash"
        target_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{target_model}:generateContent?key={api_key}"
        )
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            logger.info(f"Sending prompt to Gemini model {target_model}...")
            response = httpx.post(target_url, json=payload, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            logger.warning(f"Gemini returned {response.status_code}: {response.text}")
            return None
        except Exception as e:
            logger.warning(f"Gemini call failed: {e}")
            return None
