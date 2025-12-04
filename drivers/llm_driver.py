# Clara - Driver LLM
"""
Driver pour les appels au LLM (OpenAI)
"""

import os
import yaml
from openai import OpenAI
from pathlib import Path


class LLMDriver:
    """Driver pour communiquer avec OpenAI"""
    
    def __init__(self, config_path="config/settings.yaml"):
        # Charger la configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser le client OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        base_url = os.getenv('OPENAI_BASE_URL')
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        
        # Paramètres du modèle
        self.model = self.config.get('model', 'gpt-4')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 4096)
    
    def generate(self, messages):
        """
        Envoie les messages au LLM et retourne la réponse
        
        Args:
            messages: Liste de dict avec 'role' et 'content'
        
        Returns:
            dict: {
                'text': str,
                'usage': {
                    'prompt_tokens': int,
                    'completion_tokens': int,
                    'total_tokens': int
                }
            }
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return {
                'text': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")

