from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Literal


class Settings(BaseSettings):
    # LLM Provider settings
    llm_provider: Literal["anthropic", "openai", "google", "groq", "together"] = "together"
    llm_model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    # API Keys for different providers
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""
    together_api_key: str = ""

    # Data paths
    data_dir: Path = Path(__file__).parent.parent / "data"
    assessments_file: Path = Path(__file__).parent.parent / "data" / "assessments.json"
    axes_file: Path = Path(__file__).parent.parent / "data" / "axes.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_api_key(self) -> str:
        """Get the API key for the configured provider"""
        keys = {
            "anthropic": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "google": self.google_api_key,
            "groq": self.groq_api_key,
            "together": self.together_api_key,
        }
        return keys.get(self.llm_provider, "")


settings = Settings()
