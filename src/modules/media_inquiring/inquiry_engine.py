import random
import pandas as pd
from src.agents.media_agent import MediaAgent
from src.utils.llm_client import llm_client

class InquiryEngine:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self.agents = [MediaAgent(row) for _, row in self.df.iterrows()]

    def simulate_press_conference(self, event_description, top_k=5):
        """
        模拟发布会：选择媒体并生成提问
        """
        # 1. 筛选有“科学关注度”的媒体（排除Universal_Reporter或随机抽样）
        eligible_agents = [a for a in self.agents if a.persona['breadth'] > 0]
        if not eligible_agents: eligible_agents = self.agents
        
        participants = random.sample(eligible_agents, min(len(eligible_agents), top_k))
        
        results = []
        for agent in participants:
            question = self._generate_question(agent, event_description)
            results.append({
                "media_name": agent.name,
                "country": agent.country,
                "behavior_tag": "媒体提问",
                "content": question
            })
        return results

    def _generate_question(self, agent, event):
        # 依据：基于权重分布的随机采样，模拟人类行为的不确定性
        intent_list = list(agent.intents.keys())
        weights = list(agent.intents.values())
        
        # 选出本次提问的核心意图
        chosen_intent = random.choices(intent_list, weights=weights, k=1)[0]
        
        # 构造系统人设 (System Prompt)
        system_prompt = (
            f"你是一名来自{agent.country}的{agent.ownership}媒体资深记者。 "
            f"你的报道风格具有{agent.persona['dominant_tag']}倾向。 "
            f"在新闻发布会上，你的目标是针对事件进行深度提问。"
        )
        
        # 构造具体指令 (User Prompt)
        # 依据：Prompt Engineering 里的“分面指令”设计
        user_prompt = (
            f"当前科学事件：{event}\n"
            f"请以此事件为背景，基于你的【{chosen_intent}】意图提出一个专业提问。\n"
            f"要求：\n"
            f"1. 语气符合你的身份和国别立场。\n"
            f"2. 问题要具体，避免空泛。\n"
            f"3. 直接输出问题文本，不要有任何多余的解释。"
        )
        
        return llm_client.ask(system_prompt, user_prompt)