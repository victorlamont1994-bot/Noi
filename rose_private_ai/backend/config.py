from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="ROSE Private AI", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2:3b", alias="OLLAMA_MODEL")
    upload_dir: str = Field(default="backend/data/uploads", alias="UPLOAD_DIR")
    index_path: str = Field(default="backend/data/index/chunks.jsonl", alias="INDEX_PATH")
    audit_log_path: str = Field(default="backend/data/audit/events.jsonl", alias="AUDIT_LOG_PATH")
    source_ledger_path: str = Field(default="backend/data/audit/source_ledger.jsonl", alias="SOURCE_LEDGER_PATH")
    chunk_size: int = Field(default=900, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")
    default_top_k: int = Field(default=5, alias="DEFAULT_TOP_K")
    strict_source_mode: bool = Field(default=False, alias="STRICT_SOURCE_MODE")
    require_api_key: bool = Field(default=False, alias="REQUIRE_API_KEY")
    rose_api_key: str = Field(default="change-me-before-network-use", alias="ROSE_API_KEY")
    max_upload_mb: int = Field(default=20, alias="MAX_UPLOAD_MB")
    log_full_prompts: bool = Field(default=False, alias="LOG_FULL_PROMPTS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()

for path in [
    Path(settings.upload_dir),
    Path(settings.index_path).parent,
    Path(settings.audit_log_path).parent,
    Path(settings.source_ledger_path).parent,
]:
    path.mkdir(parents=True, exist_ok=True)
