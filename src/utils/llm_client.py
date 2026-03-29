from __future__ import annotations

import openai

from configs.llm_settings import DEFAULT_PROVIDER, PROVIDERS


class LLMUnavailableError(Exception):
    """所有已配置的大模型供应商均调用失败时抛出，供 HTTP 层返回统一错误体。"""

    def __init__(self, message: str, attempts: list[dict]):
        super().__init__(message)
        self.message = message
        self.attempts = attempts  # [{"provider": str, "error": str}, ...]


class MultiProviderClient:
    def __init__(self):
        self.current_provider = DEFAULT_PROVIDER

    def _get_client(self, provider_name: str):
        conf = PROVIDERS[provider_name]
        return openai.OpenAI(api_key=conf["api_key"], base_url=conf["base_url"]), conf["model_name"]

    def ask(self, system_prompt: str, user_prompt: str) -> str:
        attempt_order = [self.current_provider] + [
            p for p in PROVIDERS.keys() if p != self.current_provider
        ]
        attempts: list[dict] = []

        for provider in attempt_order:
            try:
                client, model = self._get_client(provider)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=60,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                err_text = str(e)
                attempts.append({"provider": provider, "error": err_text})
                print(f"⚠️ {provider} 调用失败: {e}，正在尝试切换...")
                continue

        raise LLMUnavailableError(
            "所有已配置的模型供应商均不可用",
            attempts=attempts,
        )


llm_client = MultiProviderClient()
