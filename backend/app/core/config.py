from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    app_name: str = "PO Agent API"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])


settings = Settings()
