import os
from dotenv import load_dotenv

load_dotenv()

# ===================== 模型多级配置 =====================
# 每个供应商可以配置多个模型名，按列表顺序尝试
PROVIDERS_CONFIG = {
    "zhipu": {
        "api_key": os.getenv("ZHIPU_API_KEY"),
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-0520", "glm-4-flash"], # 高级模型在前
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com",
        "models": ["deepseek-chat"],
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini"],
    }
}

# 优先级顺序：指定哪个供应商优先
PROVIDER_PRIORITY = os.getenv("PROVIDER_PRIORITY", "zhipu,deepseek,openai").split(",")

LLM_COMMON_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 800,
    "timeout": 30
}