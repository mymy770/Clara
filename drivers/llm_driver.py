# Clara - Driver LLM
"""
Driver pour les appels au LLM (OpenAI)
"""

import os
import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMDriver:
    def __init__(self, config_path: str = "config/settings.yaml") -> None:
        # Charger la config YAML
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        self.model = cfg.get("model", "gpt-5.1")
        self.temperature = float(cfg.get("temperature", 0.7))
        self.max_tokens = int(cfg.get("max_tokens", 4096))

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found in environment variables")

        # IMPORTANT : aucun proxies ici
        self.client = OpenAI(api_key=api_key)

    def generate(self, messages: list[dict]) -> dict:
        """
        messages = [
          {"role": "system", "content": "..."},
          {"role": "user", "content": "..."},
          ...
        ]
        Retourne un dict avec { "text": str, "usage": {...} }
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        choice = resp.choices[0]
        text = choice.message.content or ""
        usage = getattr(resp, "usage", None)
        return {"text": text, "usage": usage}
