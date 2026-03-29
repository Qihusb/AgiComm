import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ===================== 模型服务商配置（智谱/深度求索/OpenAI）=====================
PROVIDERS = {
    "zhipu": {
        "api_key": os.getenv("ZHIPU_API_KEY"),
        # OpenAI 兼容 SDK 会自动在 base_url 后拼接 /chat/completions，此处切勿再写 /chat/completions
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_name": "glm-4.7-flash",
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com",
        "model_name": "deepseek-chat",
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o",
    }
}

# 默认使用的模型服务商（可在 .env 中指定，默认智谱）
DEFAULT_PROVIDER = os.getenv("PRIMARY_PROVIDER", "zhipu")

# ===================== 统一 LLM 调用参数配置 =====================
# 从默认服务商自动获取 key 和地址，无需重复填写
selected_provider = PROVIDERS[DEFAULT_PROVIDER]

LLM_CONFIG = {
    "api_key": selected_provider["api_key"],
    "base_url": selected_provider["base_url"],
    "model_name": selected_provider["model_name"],
    "temperature": 0.7,      # 记者风格：专业性 + 创造性
    "max_tokens": 500       # 单轮提问最大长度
}