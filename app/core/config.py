from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )

    APP_NAME: str = "goody2-2api"
    APP_VERSION: str = "1.0.0"
    DESCRIPTION: str = "一个将 goody2.ai 转换为兼容 OpenAI 格式 API 的高性能代理，由创世纪协议 · Ω 版自主生成。"

    # 安全密钥
    API_MASTER_KEY: Optional[str] = None
    
    # 部署配置
    NGINX_PORT: int = 8088

    # 模型配置
    DEFAULT_MODEL: str = "goody2-ai"
    KNOWN_MODELS: List[str] = ["goody2-ai"]

settings = Settings()
