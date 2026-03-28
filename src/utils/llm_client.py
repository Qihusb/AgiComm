import openai
from configs.llm_settings import PROVIDERS, DEFAULT_PROVIDER

class MultiProviderClient:
    def __init__(self):
        self.current_provider = DEFAULT_PROVIDER

    def _get_client(self, provider_name):
        conf = PROVIDERS[provider_name]
        return openai.OpenAI(api_key=conf["api_key"], base_url=conf["base_url"]), conf["model_name"]

    def ask(self, system_prompt, user_prompt):
        # 尝试顺序：默认提供商 -> 备选提供商
        attempt_order = [self.current_provider] + [p for p in PROVIDERS.keys() if p != self.current_provider]
        
        for provider in attempt_order:
            try:
                client, model = self._get_client(provider)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    timeout=15 # 设置超时，防止死等
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️ {provider} 调用失败: {e}，正在尝试切换...")
                continue
        
        return "所有模型供应商均不可用，请检查配置。"

llm_client = MultiProviderClient()