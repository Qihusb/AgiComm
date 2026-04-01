from __future__ import annotations
import openai
import threading
from typing import List, Dict, Any
from configs.llm_settings import PROVIDERS_CONFIG, PROVIDER_PRIORITY, LLM_COMMON_CONFIG

class LLMUnavailableError(Exception):
    def __init__(self, message: str, attempts: list[dict]):
        super().__init__(message)
        self.attempts = attempts

class MultiProviderClient:
    def __init__(self):
        self._lock = threading.Lock()
        # 初始状态下，将配置中的所有模型平铺为一个优先级队列
        self.model_pool: List[Dict[str, Any]] = []
        self._build_model_pool()

    def _build_model_pool(self):
        """将配置转换为平铺的模型列表，用于按序尝试"""
        new_pool = []
        for p_name in PROVIDER_PRIORITY:
            if p_name in PROVIDERS_CONFIG:
                conf = PROVIDERS_CONFIG[p_name]
                for m_name in conf["models"]:
                    new_pool.append({
                        "provider": p_name,
                        "model_name": m_name,
                        "api_key": conf["api_key"],
                        "base_url": conf["base_url"]
                    })
        self.model_pool = new_pool

    def check_health(self) -> List[Dict]:
        """系统自检：尝试对每个供应商的第一个模型进行极简调用"""
        health_results = []
        valid_pool = []
        
        print("🔍 正在进行 LLM 供应商可用性自检...")
        for item in self.model_pool:
            # 这里可以根据需要只检查每个 Provider 的第一个模型以节省 Token
            try:
                client = openai.OpenAI(api_key=item["api_key"], base_url=item["base_url"])
                # 使用极短的测试文本
                client.models.list() # 仅检查 API Key 是否能连接
                valid_pool.append(item)
                health_results.append({"model": item["model_name"], "status": "ok"})
            except Exception as e:
                health_results.append({"model": item["model_name"], "status": "failed", "error": str(e)})
        
        # 如果自检通过，可以更新 model_pool 过滤掉确定无效的
        # self.model_pool = valid_pool 
        return health_results

    def ask(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> str:
        attempts = []
        # 合并参数
        temp = kwargs.get("temperature", LLM_COMMON_CONFIG["temperature"])
        tokens = kwargs.get("max_tokens", LLM_COMMON_CONFIG["max_tokens"])

        # 遍历模型池：先换型号，再换供应商
        for target in self.model_pool:
            try:
                client = openai.OpenAI(
                    api_key=target["api_key"], 
                    base_url=target["base_url"],
                    timeout=LLM_COMMON_CONFIG["timeout"]
                )
                
                response = client.chat.completions.create(
                    model=target["model_name"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temp,
                    max_tokens=tokens,
                )
                return response.choices[0].message.content.strip()
            
            except Exception as e:
                err_msg = str(e)
                attempts.append({
                    "provider": target["provider"], 
                    "model": target["model_name"], 
                    "error": err_msg
                })
                print(f"⚠️ {target['provider']}({target['model_name']}) 失败: {err_msg[:50]}...")
                continue

        raise LLMUnavailableError("所有配置的模型及备选型号均不可用", attempts)

llm_client = MultiProviderClient()

