"""Centralised environment variable loading via Pydantic Settings.

All application code must access configuration through this module only.
Never read os.environ directly in service or function code.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,        # Loaded from environment / local.settings.json at runtime
        case_sensitive=True,
        extra="ignore",
    )

    # Google Generative AI
    GOOGLE_API_KEY: str = Field(..., description="Gemini API key from Google AI Studio")
    GOOGLE_CLOUD_PROJECT: str = Field(
        default="", description="GCP project ID (optional for API-key auth)"
    )
    LLM_MODEL: str = Field(
        default="gemini-2.0-flash", description="Gemini model name for LLM (e.g. gemini-2.0-flash)"
    )
    EMBEDDING_MODEL: str = Field(
        default="models/text-embedding-004", description="Gemini model name for embeddings"
    )

    # Azure Cosmos DB
    COSMOS_ENDPOINT: str = Field(..., description="Cosmos DB account endpoint URL")
    COSMOS_DATABASE_NAME: str = Field(default="knowledgebase")

    # Azure Blob Storage
    STORAGE_ACCOUNT_NAME: str = Field(..., description="Azure Storage account name")
    PDF_CONTAINER_NAME: str = Field(default="pdfs")

    # Azure Application Insights
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = Field(
        default="", description="App Insights connection string for structured logging"
    )


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Return a cached singleton AppConfig instance."""
    return AppConfig()
