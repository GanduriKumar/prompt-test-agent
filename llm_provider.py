"""
Multi-Provider LLM Integration Module

Supports multiple LLM service providers:
- Ollama (local models)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Azure OpenAI
- AWS Bedrock

Usage:
    from llm_provider import LLMProvider
    
    # Initialize with provider
    llm = LLMProvider(provider="openai", model="gpt-4")
    
    # Generate text
    response = llm.generate(prompt="Write a test case", format="json")
    
    # Generate with vision
    response = llm.generate_vision(prompt="Describe this image", image_base64="...")
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with connection pooling"""
        session = requests.Session()
        session.headers.update({'Content-Type': 'application/json'})
        return session
    
    @abstractmethod
    def generate(self, prompt: str, format: str = "json", max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Generate text response from prompt"""
        pass
    
    @abstractmethod
    def generate_vision(self, prompt: str, image_base64: str, format: str = "json") -> str:
        """Generate response from prompt with image (vision models)"""
        pass
    
    def _truncate_prompt(self, prompt: str, max_length: int = 50000) -> str:
        """Truncate prompt to prevent DoS"""
        if len(prompt) > max_length:
            logging.warning(f"Prompt truncated from {len(prompt)} to {max_length} characters")
            return prompt[:max_length]
        return prompt


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, model: str, base_url: Optional[str] = None):
        super().__init__(
            model=model,
            base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("OLLAMA_BASE_URL must start with http:// or https://")
    
    def generate(self, prompt: str, format: str = "json", max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Generate text using Ollama API"""
        prompt = self._truncate_prompt(prompt)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": format if format == "json" else None,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                # timeout=500  # 5 minutes for large models
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama API request failed: {e}")
            raise ValueError(f"Failed to generate output: {e}")
    
    def generate_vision(self, prompt: str, image_base64: str, format: str = "json") -> str:
        """Generate using Ollama vision model"""
        prompt = self._truncate_prompt(prompt)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "images": [image_base64],
            "format": format if format == "json" else None,
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                # timeout=500
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama vision API request failed: {e}")
            raise ValueError(f"Failed to extract elements: {e}")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider (GPT-4, GPT-3.5, etc.)"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(
            model=model,
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}'
        })
    
    def generate(self, prompt: str, format: str = "json", max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Generate text using OpenAI API"""
        prompt = self._truncate_prompt(prompt)
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that generates structured responses."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add response format for JSON mode (GPT-4 and newer)
        if format == "json" and self.model.startswith(("gpt-4", "gpt-3.5-turbo-1106")):
            payload["response_format"] = {"type": "json_object"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logging.error(f"OpenAI API request failed: {e}")
            raise ValueError(f"Failed to generate output: {e}")
    
    def generate_vision(self, prompt: str, image_base64: str, format: str = "json") -> str:
        """Generate using OpenAI vision model (GPT-4 Vision)"""
        prompt = self._truncate_prompt(prompt)
        
        payload = {
            "model": self.model if "vision" in self.model else "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logging.error(f"OpenAI vision API request failed: {e}")
            raise ValueError(f"Failed to extract elements: {e}")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider"""
    
    def __init__(self, model: str, api_key: Optional[str] = None):
        super().__init__(
            model=model,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url="https://api.anthropic.com/v1"
        )
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.session.headers.update({
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        })
    
    def generate(self, prompt: str, format: str = "json", max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Generate text using Anthropic API"""
        prompt = self._truncate_prompt(prompt)
        
        # Add JSON instruction to system prompt
        system_message = "You are a helpful assistant that generates structured responses."
        if format == "json":
            system_message += " Always respond with valid JSON format."
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_message,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/messages",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Anthropic API request failed: {e}")
            raise ValueError(f"Failed to generate output: {e}")
    
    def generate_vision(self, prompt: str, image_base64: str, format: str = "json") -> str:
        """Generate using Anthropic vision model (Claude 3)"""
        prompt = self._truncate_prompt(prompt)
        
        system_message = "You are a helpful assistant that analyzes images and generates structured responses."
        if format == "json":
            system_message += " Always respond with valid JSON format."
        
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_message,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/messages",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Anthropic vision API request failed: {e}")
            raise ValueError(f"Failed to extract elements: {e}")


class GoogleProvider(BaseLLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self, model: str, api_key: Optional[str] = None):
        super().__init__(
            model=model,
            api_key=api_key or os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta"
        )
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    def generate(self, prompt: str, format: str = "json", max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Generate text using Google Gemini API"""
        prompt = self._truncate_prompt(prompt)
        
        # Add JSON instruction if needed
        if format == "json":
            prompt = f"Respond only with valid JSON format.\n\n{prompt}"
        
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Google API request failed: {e}")
            raise ValueError(f"Failed to generate output: {e}")
    
    def generate_vision(self, prompt: str, image_base64: str, format: str = "json") -> str:
        """Generate using Google Gemini vision model"""
        prompt = self._truncate_prompt(prompt)
        
        if format == "json":
            prompt = f"Respond only with valid JSON format.\n\n{prompt}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Google vision API request failed: {e}")
            raise ValueError(f"Failed to extract elements: {e}")


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI LLM provider"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(
            model=model,
            api_key=api_key or os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=base_url or os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        if not self.base_url:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", self.model)
        
        self.session.headers.update({
            'api-key': self.api_key
        })
    
    def generate(self, prompt: str, format: str = "json", max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Generate text using Azure OpenAI API"""
        prompt = self._truncate_prompt(prompt)
        
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that generates structured responses."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add response format for JSON mode
        if format == "json":
            payload["response_format"] = {"type": "json_object"}
        
        try:
            url = f"{self.base_url}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            response = self.session.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Azure OpenAI API request failed: {e}")
            raise ValueError(f"Failed to generate output: {e}")
    
    def generate_vision(self, prompt: str, image_base64: str, format: str = "json") -> str:
        """Generate using Azure OpenAI vision model"""
        prompt = self._truncate_prompt(prompt)
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }
        
        try:
            url = f"{self.base_url}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            response = self.session.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Azure OpenAI vision API request failed: {e}")
            raise ValueError(f"Failed to extract elements: {e}")


class LLMProvider:
    """Factory class for creating LLM provider instances"""
    
    PROVIDERS = {
        'ollama': OllamaProvider,
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'google': GoogleProvider,
        'azure': AzureOpenAIProvider,
    }
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None, 
                 vision_model: Optional[str] = None, coding_model: Optional[str] = None,
                 api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize LLM provider.
        
        Args:
            provider: Provider name ('ollama', 'openai', 'anthropic', 'google', 'azure')
            model: Main model for text generation
            vision_model: Model for vision tasks (optional, defaults to main model)
            coding_model: Model for code generation (optional, defaults to main model)
            api_key: API key (optional, will use env var if not provided)
            base_url: Base URL for API (optional, will use default/env var)
        
        Environment Variables:
            LLM_PROVIDER: Default provider ('ollama', 'openai', etc.)
            LLM_MODEL: Default text model
            LLM_VISION_MODEL: Default vision model
            LLM_CODING_MODEL: Default coding model
        """
        # Get provider and models from env if not specified
        self.provider_name = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower()
        self.model = model or os.getenv("LLM_MODEL") or self._get_default_model()
        self.vision_model = vision_model or os.getenv("LLM_VISION_MODEL") or self.model
        self.coding_model = coding_model or os.getenv("LLM_CODING_MODEL") or self.model
        
        if self.provider_name not in self.PROVIDERS:
            raise ValueError(f"Unsupported provider: {self.provider_name}. Supported: {list(self.PROVIDERS.keys())}")
        
        # Create provider instances
        provider_class = self.PROVIDERS[self.provider_name]
        
        # Create text generation provider
        if self.provider_name == 'ollama':
            self.text_provider = provider_class(model=self.model, base_url=base_url)
            self.vision_provider = provider_class(model=self.vision_model, base_url=base_url)
            self.coding_provider = provider_class(model=self.coding_model, base_url=base_url)
        elif self.provider_name == 'azure':
            self.text_provider = provider_class(model=self.model, api_key=api_key, base_url=base_url)
            self.vision_provider = provider_class(model=self.vision_model, api_key=api_key, base_url=base_url)
            self.coding_provider = provider_class(model=self.coding_model, api_key=api_key, base_url=base_url)
        else:
            self.text_provider = provider_class(model=self.model, api_key=api_key)
            self.vision_provider = provider_class(model=self.vision_model, api_key=api_key)
            self.coding_provider = provider_class(model=self.coding_model, api_key=api_key)
        
        logging.info(f"Initialized LLM provider: {self.provider_name} (model: {self.model})")
    
    def _get_default_model(self) -> str:
        """Get default model based on provider"""
        defaults = {
            'ollama': 'llama3.2',
            'openai': 'gpt-4-turbo-preview',
            'anthropic': 'claude-3-opus-20240229',
            'google': 'gemini-pro',
            'azure': 'gpt-4'
        }
        return defaults.get(self.provider_name, 'llama3.2')
    
    def generate(self, prompt: str, format: str = "json", max_tokens: int = 4096, 
                 temperature: float = 0.7, use_coding_model: bool = False) -> str:
        """
        Generate text response.
        
        Args:
            prompt: Input prompt
            format: Response format ('json' or 'text')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            use_coding_model: Use coding model instead of default
        
        Returns:
            Generated text response
        """
        provider = self.coding_provider if use_coding_model else self.text_provider
        return provider.generate(prompt, format, max_tokens, temperature)
    
    def generate_vision(self, prompt: str, image_base64: str, format: str = "json") -> str:
        """
        Generate response with vision model.
        
        Args:
            prompt: Input prompt
            image_base64: Base64-encoded image
            format: Response format ('json' or 'text')
        
        Returns:
            Generated text response
        """
        return self.vision_provider.generate_vision(prompt, image_base64, format)
    
    def generate_code(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """
        Generate code using coding model.
        
        Args:
            prompt: Code generation prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated code
        """
        return self.coding_provider.generate(prompt, format="text", max_tokens=max_tokens, temperature=temperature)


# Singleton instance for backward compatibility
_provider_instance: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """Get singleton LLM provider instance"""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = LLMProvider()
    return _provider_instance


def set_llm_provider(provider: str, model: Optional[str] = None, 
                    vision_model: Optional[str] = None, coding_model: Optional[str] = None):
    """Set global LLM provider"""
    global _provider_instance
    _provider_instance = LLMProvider(provider, model, vision_model, coding_model)
