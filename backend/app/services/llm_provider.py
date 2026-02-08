"""LLM Provider abstraction layer for easy model switching"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def chat(self, messages: List[Dict], json_format: bool = False, temperature: float = None) -> str:
        """Send chat messages and get response"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get current model name"""
        pass


class OllamaProvider(LLMProvider):
    """Ollama LLM provider"""

    def __init__(self, model_name: str = None):
        import ollama
        self.ollama = ollama
        self.model = model_name or os.getenv("OLLAMA_MODEL", "llama3.2")

    def chat(self, messages: List[Dict], json_format: bool = False, temperature: float = None) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        if json_format:
            kwargs["format"] = "json"
        if temperature is not None:
            kwargs["options"] = {"temperature": temperature}

        response = self.ollama.chat(**kwargs)
        return response['message']['content']

    def get_model_name(self) -> str:
        return f"ollama:{self.model}"


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""

    def __init__(self, model_name: str = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model_name or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def chat(self, messages: List[Dict], json_format: bool = False, temperature: float = None) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        if json_format:
            kwargs["response_format"] = {"type": "json_object"}
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def get_model_name(self) -> str:
        return f"openai:{self.model}"


class UpstageProvider(LLMProvider):
    """Upstage Solar LLM provider"""

    def __init__(self, model_name: str = None):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=os.getenv("UPSTAGE_API_KEY"),
            base_url="https://api.upstage.ai/v1"
        )
        self.model = model_name or os.getenv("UPSTAGE_MODEL", "solar-pro2")

    def chat(self, messages: List[Dict], json_format: bool = False, temperature: float = None) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        if json_format:
            kwargs["response_format"] = {"type": "json_object"}
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def get_model_name(self) -> str:
        return f"upstage:{self.model}"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, model_name: str = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model_name or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

    def chat(self, messages: List[Dict], json_format: bool = False, temperature: float = None) -> str:
        # Anthropic uses different message format
        system_message = ""
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append(msg)

        kwargs = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": chat_messages
        }
        if system_message:
            kwargs["system"] = system_message
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def get_model_name(self) -> str:
        return f"anthropic:{self.model}"


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self, model_name: str = None):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(self.model_name)

    def chat(self, messages: List[Dict], json_format: bool = False, temperature: float = None) -> str:
        # Gemini message format conversion
        gemini_messages = []
        system_instruction = ""

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})

        # Configure generation settings
        generation_config = {}
        if temperature is not None:
            generation_config["temperature"] = temperature

        # Start chat with history
        chat = self.model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

        # Add system instruction to the last user message if exists
        last_message = gemini_messages[-1]["parts"][0] if gemini_messages else ""
        if system_instruction:
            last_message = f"{system_instruction}\n\n{last_message}"

        # Generate response
        if json_format:
            last_message += "\n\nRespond with valid JSON only."

        response = chat.send_message(last_message, generation_config=generation_config if generation_config else None)
        return response.text

    def get_model_name(self) -> str:
        return f"gemini:{self.model_name}"


def get_llm_provider(provider_type: str = None, model_name: str = None) -> LLMProvider:
    """Factory function to get LLM provider based on config"""

    provider_type = provider_type or os.getenv("LLM_PROVIDER", "ollama")

    if provider_type == "ollama":
        return OllamaProvider(model_name)
    elif provider_type == "openai":
        return OpenAIProvider(model_name)
    elif provider_type == "upstage":
        return UpstageProvider(model_name)
    elif provider_type == "anthropic":
        return AnthropicProvider(model_name)
    elif provider_type == "gemini":
        return GeminiProvider(model_name)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}")


# Singleton instance
_llm_provider: Optional[LLMProvider] = None


def get_default_llm() -> LLMProvider:
    """Get default LLM provider (singleton)"""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = get_llm_provider()
    return _llm_provider
