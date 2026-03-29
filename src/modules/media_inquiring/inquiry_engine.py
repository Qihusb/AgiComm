import random
import pandas as pd

from src.agents.media_agent import MediaAgent
from src.utils.llm_client import llm_client


class InquiryEngine:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self.agents = [MediaAgent(row) for _, row in self.df.iterrows()]

    def simulate_press_conference(self, event_description):
        """
        模拟发布会：全部媒体画像各生成一条提问（顺序与 CSV 一致）。
        """
        results = []
        for agent in self.agents:
            question = self._generate_question(agent, event_description)
            results.append(
                {
                    "media_id": agent.id,
                    "media_name": agent.name,
                    "country": agent.country,
                    "behavior_tag": "媒体提问",
                    "content": question,
                }
            )
        return results

    def _generate_question(self, agent, event):
        intent_list = list(agent.intents.keys())
        weights = [max(agent.intents[k], 0.0) for k in intent_list]
        s = sum(weights)
        if s <= 0:
            weights = [1.0 / len(intent_list)] * len(intent_list)
        else:
            weights = [w / s for w in weights]

        chosen_intent = random.choices(intent_list, weights=weights, k=1)[0]
        intent_zh = agent.intent_label_zh(chosen_intent)

        system_prompt = (
            "你正在参加一场科技/外交主题新闻发布会，需要以记者身份提出一个英文或中文均可、但应专业、具体的问题。\n"
            f"{agent.get_persona_description()}\n"
            "请严格保持上述身份、地区立场与报道风格，不要自称 AI 或模型。"
        )

        user_prompt = (
            f"当前科学/科技事件：{event}\n"
            f"本次提问侧重意图：【{intent_zh}】（内部键：{chosen_intent}）。\n"
            "要求：\n"
            "1. 语气符合你的身份和国别立场。\n"
            "2. 问题要具体，避免空泛。\n"
            "3. 直接输出问题文本，不要有任何多余的解释或前缀。"
        )

        return llm_client.ask(system_prompt, user_prompt)
