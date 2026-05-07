"""
语义引擎（Semantic Engine）
核心功能：
- 替代原"纯概率决策"
- 实现：基于 Agent 属性 + 输入文本 → 生成行为决策 + 文本内容
- 分阶段实现（阶段1：规则+模板；阶段2：LLM驱动）
"""
import os
import sys
import random
from typing import Dict, Optional, Tuple
from .message import Message
from .propagation_model import stance_similarity

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'configs'))
    from llm_settings import PROVIDERS_CONFIG, LLM_COMMON_CONFIG, PROVIDER_PRIORITY
except ImportError:
    PROVIDERS_CONFIG = None
    LLM_COMMON_CONFIG = None
    PROVIDER_PRIORITY = None

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'utils'))
    from src.utils.llm_client import llm_client
except ImportError:
    llm_client = None


class SemanticEngine:
    STANCE_SIMILARITY_THRESHOLD = 0.6
    EMOTION_COMMENT_THRESHOLD = 0.7
    EMOTION_REPOST_THRESHOLD = 0.4

    def __init__(self, enable_llm: bool = False):
        self.enable_llm = enable_llm and PROVIDERS_CONFIG is not None and llm_client is not None

    def process(
        self,
        agent,
        message: Message,
        use_llm: bool = False
    ) -> Dict:
        use_llm = use_llm and self.enable_llm
        if use_llm:
            return self._process_llm_based(agent, message)
        return self._process_rule_based(agent, message)

    def _process_rule_based(self, agent, message: Message) -> Dict:
        stance_similarity_value = self._compute_stance_similarity(agent.stance, message.stance)
        cultural_penalty = self._compute_international_penalty(agent, message)
        adjusted_similarity = max(0.0, stance_similarity_value - cultural_penalty)
        agent_emotion = agent.emotion

        action, semantic_score = self._decide_action(
            stance_similarity=adjusted_similarity,
            emotion=message.emotion,
            agent_emotion=agent_emotion,
            agent_activeness=agent.activeness,
            agent_bot_prob=agent.bot_prob,
            memory_bonus=self._memory_bias(agent, message)
        )

        generated_text = self._generate_text_template(
            action=action,
            agent=agent,
            message=message,
            stance_similarity=adjusted_similarity
        )

        emotion_shift = self._compute_emotion_shift(
            agent_emotion=agent_emotion,
            message_emotion=message.emotion,
            action=action
        )

        stance_shift = self._compute_stance_shift(
            agent_stance=agent.stance,
            message_stance=message.stance,
            action=action,
            stance_similarity=adjusted_similarity
        )

        return {
            "action": action,
            "generated_text": generated_text,
            "semantic_score": semantic_score,
            "emotion_shift": emotion_shift,
            "stance_shift": stance_shift,
            "confidence": adjusted_similarity if action != "ignore" else 0.0
        }

    def _process_llm_based(self, agent, message: Message) -> Dict:
        if llm_client is None:
            return self._process_rule_based(agent, message)

        persona = self._build_agent_persona(agent)
        prompt = self._build_prompt(persona, message)

        try:
            response = llm_client.ask(
                system_prompt="你是一个国际社交网络用户，结合文化背景和历史记忆生成传播行为。",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=200
            )
            return self._parse_llm_response(response, agent, message)
        except Exception as e:
            print(f"[SemanticEngine] LLM调用失败: {e}，回退到规则模式")
            return self._process_rule_based(agent, message)

    def _decide_action(
        self,
        stance_similarity: float,
        emotion: float,
        agent_emotion: float,
        agent_activeness: float,
        agent_bot_prob: float,
        memory_bonus: float = 0.0
    ) -> Tuple[str, float]:
        bot_penalty = agent_bot_prob * 0.5
        score = stance_similarity * 0.4 + emotion * 0.3 + agent_activeness * 0.2 + memory_bonus * 0.1

        if score > 0.65 and bot_penalty < 0.3:
            action = "repost"
        elif score > 0.4 and agent_emotion > 0.4:
            action = "comment"
        else:
            action = "ignore"

        semantic_score = max(0.0, min(1.0, score * (1 - bot_penalty)))
        if action == "comment":
            semantic_score *= 0.85
        return action, semantic_score

    def _memory_bias(self, agent, message: Message) -> float:
        if not getattr(agent, "memory", None):
            return 0.0
        related = [entry for entry in agent.memory if entry.get("narrative_type") == message.narrative_type]
        return min(0.2, len(related) * 0.02)

    def _compute_stance_similarity(self, agent_stance: float, message_stance: float) -> float:
        diff = abs(agent_stance - message_stance)
        return max(0.0, min(1.0, 1 - diff))

    def _compute_international_penalty(self, agent, message: Message) -> float:
        penalty = 0.0
        if getattr(agent, "country", None) and getattr(message, "origin_country", None):
            if agent.country != message.origin_country:
                penalty += 0.2
        if getattr(agent, "language", None) and getattr(message, "language", None):
            if agent.language != message.language:
                penalty += 0.15
        return min(0.4, penalty)

    def _generate_text_template(
        self,
        action: str,
        agent,
        message: Message,
        stance_similarity: float
    ) -> str:
        if action == "ignore":
            return ""

        emotion_words = self._get_emotion_words(message.emotion)
        stance_words = self._get_stance_words(
            agent_stance=agent.stance,
            message_stance=message.stance,
            similarity=stance_similarity
        )

        if action == "repost":
            templates = [
                f"分享：{message.content}。我觉得这条信息很{stance_words}，且{emotion_words}。",
                f"转发这条内容：{message.content}。整体来说，它让我感觉{emotion_words}。",
                f"这个观点显得{stance_words}，值得关注。{message.content}"
            ]
        else:
            templates = [
                f"评论一下：{message.content}，我的感觉是{emotion_words}，我认为...",
                f"虽然{message.content}有{emotion_words}，但我觉得需要从另一个角度看。",
                f"这件事让我想到{emotion_words}，我更倾向于{stance_words}的看法。"
            ]

        return random.choice(templates)

    def _compute_emotion_shift(
        self,
        agent_emotion: float,
        message_emotion: float,
        action: str
    ) -> float:
        if action == "repost":
            return (message_emotion - agent_emotion) * 0.5
        elif action == "comment":
            return (message_emotion - agent_emotion) * 0.2
        return 0.0

    def _compute_stance_shift(
        self,
        agent_stance: float,
        message_stance: float,
        action: str,
        stance_similarity: float
    ) -> float:
        if action == "repost":
            return (message_stance - agent_stance) * 0.3 * stance_similarity
        elif action == "comment":
            return (message_stance - agent_stance) * 0.1
        return 0.0

    def _get_emotion_words(self, emotion: float) -> str:
        if emotion > 0.8:
            return "激烈"
        elif emotion > 0.6:
            return "强烈"
        elif emotion > 0.4:
            return "关注"
        return "平稳"

    def _get_stance_words(self, agent_stance: float, message_stance: float, similarity: float) -> str:
        if similarity > 0.7:
            return "一致"
        elif similarity > 0.4:
            return "部分认同"
        return "谨慎"

    def _build_agent_persona(self, agent) -> str:
        stance_desc = "支持" if agent.stance > 0.5 else "反对" if agent.stance < -0.5 else "中立"
        emotion_desc = "高" if agent.emotion > 0.6 else "低"
        return f"一个来自{agent.country}的{stance_desc}用户，语言是{agent.language}，情绪{emotion_desc}。"

    def _build_prompt(self, persona: str, message: Message) -> str:
        return (
            f"你是{persona}。\n"
            f"你看到一条来自{message.origin_country or '未知'}的信息：{message.content}\n"
            f"请判断是否要转发、评论或忽略，并给出简短文本。\n"
            f"格式：行为: [repost|comment|ignore]；文本: [如果有]\n"
        )

    def _parse_llm_response(self, response: str, agent, message: Message) -> Dict:
        parts = response.strip().split("；")
        action = "ignore"
        generated_text = ""
        for part in parts:
            if part.startswith("行为:"):
                if "repost" in part:
                    action = "repost"
                elif "comment" in part:
                    action = "comment"
                elif "ignore" in part:
                    action = "ignore"
            elif part.startswith("文本:"):
                generated_text = part.replace("文本:", "").strip()

        if not generated_text and action != "ignore":
            generated_text = self._generate_text_template(action, agent, message, self._compute_stance_similarity(agent.stance, message.stance))

        semantic_score = 0.75 if action != "ignore" else 0.0
        return {
            "action": action,
            "generated_text": generated_text,
            "semantic_score": semantic_score,
            "emotion_shift": self._compute_emotion_shift(agent.emotion, message.emotion, action),
            "stance_shift": self._compute_stance_shift(agent.stance, message.stance, action, self._compute_stance_similarity(agent.stance, message.stance))
        }

    def _compute_emotion_shift(
        self,
        agent_emotion: float,
        message_emotion: float,
        action: str
    ) -> float:
        """
        计算情感偏移
        
        - "repost": 完全同步 (偏移 = 0.5)
        - "comment": 部分影响 (偏移 = 0.2)
        - "ignore": 无影响 (偏移 = 0.0)
        """
        if action == "repost":
            return (message_emotion - agent_emotion) * 0.5  # 50% 影响
        elif action == "comment":
            return (message_emotion - agent_emotion) * 0.2  # 20% 影响
        else:
            return 0.0
    
    def _compute_stance_shift(
        self,
        agent_stance: float,
        message_stance: float,
        action: str,
        stance_similarity: float
    ) -> float:
        """
        计算立场偏移
        
        - "repost": 完全同向 (偏移 = 0.3)
        - "comment": 轻微影响 (偏移 = 0.1)
        - "ignore": 无影响 (偏移 = 0.0)
        """
        if action == "repost":
            return (message_stance - agent_stance) * 0.3 * stance_similarity
        elif action == "comment":
            return (message_stance - agent_stance) * 0.1
        else:
            return 0.0
    
    def _get_emotion_words(self, emotion: float) -> str:
        """根据情感强度选择词汇"""
        if emotion > 0.8:
            return "愤怒/震惊"
        elif emotion > 0.6:
            return "关注/在意"
        elif emotion > 0.4:
            return "有点惊讶"
        else:
            return "平淡"
    
    def _get_stance_words(
        self,
        agent_stance: float,
        message_stance: float,
        similarity: float
    ) -> str:
        """根据立场生成表达"""
        if similarity > 0.7:
            return "赞同"
        elif similarity > 0.4:
            return "有同感"
        else:
            return "值得思考"
    
    def _build_agent_persona(self, agent) -> str:
        """构建Agent的人设（用于LLM提示）"""
        stance_desc = "支持" if agent.stance > 0.5 else "反对" if agent.stance < -0.5 else "中立"
        emotion_desc = "高" if agent.emotion > 0.6 else "低"
        
        return f"一个{stance_desc}、情绪{emotion_desc}、活跃度{agent.activeness:.1f}的网络用户"
    
    def _build_prompt(self, persona: str, message: Message) -> str:
        """构建LLM提示词（阶段2预留）"""
        prompt = f"""
        你是{persona}。
        
        你看到了一条信息：
        {message.content}
        
        这条信息的立场倾向度：{message.stance}（-1为反对，1为支持）
        这条信息的情感强度：{message.emotion}（0-1）
        
        请决定你的反应：
        1. 是否转发/评论/忽略
        2. 如果转发/评论，请生成你的文本
        
        格式：
        行为: [repost|comment|ignore]
        文本: [如果是转发或评论，生成文本]
        """
        return prompt
    
    def _parse_llm_response(self, response: str, agent, message: Message) -> Dict:
        """解析LLM响应（阶段2预留）"""
        # 这里应该解析LLM的响应，但现在先返回规则结果
        return self._process_rule_based(agent, message)
