import random
import pandas as pd
from typing import Optional, List

from src.agents.media_agent import MediaAgent
from src.utils.llm_client import llm_client


class InquiryEngine:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self.agents = [MediaAgent(row) for _, row in self.df.iterrows()]
        self.agents_dict = {agent.id: agent for agent in self.agents}

    def simulate_press_conference(self, event_description):
        """
        模拟发布会：全部媒体画像各生成一条提问（顺序与 CSV 一致）。
        """
        print(f"\n{'='*80}")
        print(f"🎤 模拟发布会：为 {len(self.agents)} 个媒体生成提问")
        print(f"{'='*80}")
        print(f"📝 事件描述：{event_description}\n")
        
        results = []
        for idx, agent in enumerate(self.agents, 1):
            print(f"\n[{idx}/{len(self.agents)}] 处理媒体: {agent.name} ({agent.id})")
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
        
        print(f"\n{'='*80}")
        print(f"✅ 完成发布会仿真：共生成 {len(results)} 条提问")
        print(f"{'='*80}\n")
        return results

    def simulate_press_conference_stream(self, event_description: str, media_ids: Optional[List[str]] = None):
        """
        流式模拟发布会：逐个媒体判断是否参与，参与则生成提问并返回（支持媒体过滤）。
        
        Args:
            event_description: 事件描述
            media_ids: 指定的媒体 ID 列表，为 None 或空列表则使用全部媒体
            
        Yields:
            dict: 每个媒体的提问结果（包含 media_id, media_name, country, behavior_tag, content, is_participating）
        """
        # 确定处理的媒体列表
        if media_ids and len(media_ids) > 0:
            # 过滤指定的媒体
            target_agents = [self.agents_dict[mid] for mid in media_ids if mid in self.agents_dict]
            print(f"\n{'='*80}")
            print(f"🎤 媒体提问流式仿真：为 {len(target_agents)} 个指定媒体判断并生成提问")
            print(f"   选定媒体: {', '.join([a.name for a in target_agents])}")
            print(f"{'='*80}")
        else:
            # 使用全部媒体
            target_agents = self.agents
            print(f"\n{'='*80}")
            print(f"🎤 媒体提问流式仿真：为全部 {len(self.agents)} 个媒体判断并生成提问")
            print(f"{'='*80}")
        
        print(f"📝 事件描述：{event_description}\n")
        
        for idx, agent in enumerate(target_agents, 1):
            print(f"\n[{idx}/{len(target_agents)}] 处理媒体: {agent.name} ({agent.id})")
            try:
                # 第一步：判断是否参与提问
                print(f"  ⏳ 判断是否参与提问...")
                is_participating = self._decide_participation(agent, event_description)
                
                if is_participating:
                    print(f"  ✓ 决定参与提问，开始生成提问内容...")
                    question = self._generate_question(agent, event_description)
                    print(f"  ✅ 生成完成")
                    yield {
                        "media_id": agent.id,
                        "media_name": agent.name,
                        "country": agent.country,
                        "behavior_tag": "媒体提问",
                        "content": question,
                        "is_participating": True,
                    }
                else:
                    print(f"  ✗ 决定不参与提问")
                    yield {
                        "media_id": agent.id,
                        "media_name": agent.name,
                        "country": agent.country,
                        "behavior_tag": "媒体提问",
                        "content": "此媒体对该事件不感兴趣，选择不参与提问",
                        "is_participating": False,
                    }
            except Exception as e:
                print(f"   ✗ 错误: {type(e).__name__}: {str(e)[:100]}")
                yield {
                    "media_id": agent.id,
                    "media_name": agent.name,
                    "country": agent.country,
                    "behavior_tag": "媒体提问",
                    "content": f"提问生成失败：{str(e)[:100]}",
                    "is_participating": False,
                }
        
        print(f"\n{'='*80}")
        print(f"✅ 完成流式仿真：共处理 {len(target_agents)} 个媒体")
        print(f"{'='*80}\n")

    def _decide_participation(self, agent, event):
        """
        判断某个媒体是否应该参与提问。
        基于媒体的特征（国家、关注领域、所有制类型等）和事件内容，用 LLM 判断。
        
        Args:
            agent: MediaAgent 对象
            event: 事件描述
            
        Returns:
            bool: 是否参与提问
        """
        system_prompt = (
            "你是一名新闻评论专家，需要判断某个特定的媒体记者是否会对给定的科技/外交事件表现出兴趣，"
            "以及是否会在新闻发布会上提出相关问题。\n\n"
            "判断标准：\n"
            "1. 事件的内容是否与该媒体的报道重点相关（如经济、国际政治、科学技术）\n"
            "2. 该媒体所在国家对事件中涉及的国家和地区的态度如何\n"
            "3. 该媒体的所有制类型（私营/公共）对事件话题的敏感度\n"
            "4. 通常情况下，大多数有国际影响力的媒体都会对重大科技事件感兴趣\n\n"
            "请直接回答\"是\"或\"否\"，不要有任何其他解释。"
        )

        user_prompt = (
            f"媒体信息：\n"
            f"- 媒体名称：{agent.name}\n"
            f"- 所在国家/地区：{agent.country}\n"
            f"- 媒体类型：{agent.ownership_type if hasattr(agent, 'ownership_type') else '未知'}\n"
            f"- 主要报道领域：{', '.join(list(agent.intents.keys())[:3]) if hasattr(agent, 'intents') else '未知'}\n\n"
            f"事件描述：{event}\n\n"
            f"请判断：这个媒体的记者是否会对此事件感兴趣，并在新闻发布会上提出问题？\n"
            f"请直接回答【是】或【否】。"
        )

        print(f"    🤔 发送参与决策提示词给 LLM...")
        print(f"    {'-'*72}")
        print(f"    系统: {system_prompt[:100]}...")
        print(f"    用户: {user_prompt[:100]}...")
        print(f"    {'-'*72}")
        
        response = llm_client.ask(system_prompt, user_prompt, max_tokens=10)
        
        print(f"    LLM 回复: {response}")
        
        # 判断响应中是否包含"是"
        decision = "是" in response or "yes" in response.lower() or "参与" in response
        
        print(f"    决策结果: {'参与' if decision else '不参与'}")
        
        return decision

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
        
        # 打印媒体信息和提示词
        print(f"  📋 媒体身份：")
        print(f"     - 国家：{agent.country}")
        print(f"     - 提问意图：{intent_zh}")
        print(f"\n  🔧 系统提示词：")
        print(f"  {'-'*76}")
        for line in system_prompt.split('\n'):
            print(f"  {line}")
        print(f"  {'-'*76}")
        print(f"\n  👤 用户提示词：")
        print(f"  {'-'*76}")
        for line in user_prompt.split('\n'):
            print(f"  {line}")
        print(f"  {'-'*76}")
        
        # 调用 LLM
        print(f"\n  ⏳ 调用 LLM...")
        question = llm_client.ask(system_prompt, user_prompt)
        
        # 打印返回的问题
        print(f"  ✅ 生成的提问：")
        print(f"  {'-'*76}")
        print(f"  {question}")
        print(f"  {'-'*76}\n")
        
        return question
