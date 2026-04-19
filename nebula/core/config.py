from dataclasses import dataclass
import os


@dataclass(slots=True)
class AppConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    default_provider: str = "mock"
    enable_console: bool = False
    database_path: str = "data/nebulabot.db"
    system_prompt: str = (
        "You are NebulaBot, a practical AI assistant for communities, operators, and makers."
    )
    openai_model: str = "gpt-4.1-mini"
    gemini_model: str = "gemini-1.5-flash"
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"
    zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    zhipu_model: str = "glm-5.1"
    claude_model: str = "claude-sonnet-4-20250514"
    claude_base_url: str = ""
    claude_api_style: str = "anthropic"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            host=os.getenv("NEBULA_HOST", "0.0.0.0"),
            port=int(os.getenv("NEBULA_PORT", "8000")),
            default_provider=os.getenv("NEBULA_PROVIDER", "mock").lower(),
            enable_console=os.getenv("NEBULA_ENABLE_CONSOLE", "false").lower()
            in {"1", "true", "yes", "on"},
            database_path=os.getenv("NEBULA_DB_PATH", "data/nebulabot.db"),
            system_prompt=os.getenv(
                "NEBULA_SYSTEM_PROMPT",
                "You are NebulaBot, a practical AI assistant for communities, operators, and makers.",
            ),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            qwen_base_url=os.getenv(
                "QWEN_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
            qwen_model=os.getenv("QWEN_MODEL", "qwen-plus"),
            zhipu_base_url=os.getenv(
                "ZHIPU_BASE_URL",
                "https://open.bigmodel.cn/api/paas/v4",
            ),
            zhipu_model=os.getenv("ZHIPU_MODEL", "glm-5.1"),
            claude_model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            claude_base_url=os.getenv("CLAUDE_BASE_URL", ""),
            claude_api_style=os.getenv("CLAUDE_API_STYLE", "anthropic").lower(),
        )
