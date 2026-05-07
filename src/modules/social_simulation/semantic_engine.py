"""
语义引擎（Semantic Engine）- 规则驱动传播 + LLM语义增强

架构：
- RuleDecisionLayer：规则决策（是否传播、情感/立场变化）
- LLMGenerationLayer：LLM生成（文本、表达、语义质量）
- SemanticEngine：统一入口
"""
import os
import sys
import random
from typing import Dict, Optional, Tuple
from .message import Message

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'configs'))
    from llm_settings import PROVIDERS_CONFIG, LLM_COMMON_CONFIG, PROVIDER_PRIORITY
except ImportError:
    PROVIDERS_CONFIG = None
    LLM_COMMON_CONFIG = None
    PROVIDER_PRIORITY = None


class RuleDecisionLayer:
    """规则驱动决策层 - 控制传播逻辑（不涉及LLM）"""
    
    STANCE_SIMILARITY_THRESHOLD = 0.6
    EMOTION_COMMENT_THRESHOLD = 0.7
    EMOTION_REPOST_THRESHOLD = 0.4

    @staticmethod
    def decide_action(
        agent_stance: float,
        message_stance: float,
        message_emotion: float,
        agent_emotion: float,
        agent_activeness: float,
        agent_bot_prob: float,
        memory_bonus: float = 0.0
    ) -> Tuple[str, float]:
        """决定传播行为（纯规则）"""
        stance_sim = max(0.0, min(1.0, 1 - abs(agent_stance - message_stance)))
        bot_penalty = agent_bot_prob * 0.5
        score = (
            stance_sim * 0.4 +
            message_emotion * 0.3 +
            agent_activeness * 0.2 +
            memory_bonus * 0.1
        )

        if score > 0.5 and bot_penalty < 0.3:
            action = "repost"
        elif score > 0.3 and agent_emotion > 0.3:
            action = "comment"
        else:
            action = "ignore"

        semantic_score = max(0.0, min(1.0, score * (1 - bot_penalty)))
        if action == "comment":
            semantic_score *= 0.85
        return action, semantic_score

    @staticmethod
    def compute_emotion_shift(
        agent_emotion: float,
        message_emotion: float,
        action: str
    ) -> float:
        """计算情感变化"""
        if action == "repost":
            return (message_emotion - agent_emotion) * 0.5
        elif action == "comment":
            return (message_emotion - agent_emotion) * 0.2
        return 0.0

    @staticmethod
    def compute_stance_shift(
        agent_stance: float,
        message_stance: float,
        action: str,
        stance_similarity_val: float
    ) -> float:
        """计算立场变化"""
        if action == "repost":
            return (message_stance - agent_stance) * 0.3 * stance_similarity_val
        elif action == "comment":
            return (message_stance - agent_stance) * 0.1
        return 0.0

    @staticmethod
    def compute_international_penalty(agent, message: Message) -> float:
        """计算国际/跨文化惩罚"""
        penalty = 0.0
        if getattr(agent, "country", None) and getattr(message, "origin_country", None):
            if agent.country != message.origin_country:
                penalty += 0.2
        if getattr(agent, "language", None) and getattr(message, "language", None):
            if agent.language != message.language:
                penalty += 0.15
        return min(0.4, penalty)

    @staticmethod
    def compute_memory_bias(agent, message: Message) -> float:
        """基于历史记忆的偏差"""
        if not getattr(agent, "memory", None):
            return 0.0
        related = [
            entry for entry in agent.memory
            if entry.get("narrative_type") == message.narrative_type
        ]
        return min(0.2, len(related) * 0.02)


class SemanticEngine:
    """统一语义引擎入口"""
    
    def __init__(self, enable_llm: bool = False):
        self.enable_llm = enable_llm and PROVIDERS_CONFIG is not None
        self.llm_generator = None
        if self.enable_llm:
            try:
                from .llm_generator import LLMGenerator
                self.llm_generator = LLMGenerator()
            except ImportError:
                self.enable_llm = False

    def process(
        self,
        agent,
        message: Message,
        use_llm: Optional[bool] = None
    ) -> Dict:
        """
        核心处理方法
        
        Returns:
        {
            "should_forward": bool,
            "action": "repost"|"comment"|"ignore",
            "emotion_shift": float,
            "stance_shift": float,
            "generated_text": str,
            "semantic_score": float
        }
        """
        if use_llm is None:
            use_llm = self.enable_llm
        else:
            use_llm = bool(use_llm and self.enable_llm)
        
        # 规则决策层 - 决定是否传播、情感/立场变化
        action, semantic_score = self._rule_decision(agent, message)
        
        # 生成文本
        if action == "ignore":
            generated_text = ""
            actual_llm_used = False
            llm_error = None
        else:
            generated_text, actual_llm_used, llm_error = self._generate_text(
                agent, message, action, use_llm
            )

        # 计算状态变化
        stance_sim = max(0.0, min(1.0, 1 - abs(agent.stance - message.stance)))
        emotion_shift = RuleDecisionLayer.compute_emotion_shift(
            agent.emotion, message.emotion, action
        )
        stance_shift = RuleDecisionLayer.compute_stance_shift(
            agent.stance, message.stance, action, stance_sim
        )
        
        return {
            "should_forward": action != "ignore",
            "action": action,
            "emotion_shift": emotion_shift,
            "stance_shift": stance_shift,
            "generated_text": generated_text,
            "semantic_score": semantic_score,
            "use_llm": bool(actual_llm_used),
            "llm_error": llm_error
        }

    def _rule_decision(self, agent, message: Message) -> Tuple[str, float]:
        """纯规则决策"""
        stance_sim = max(0.0, min(1.0, 1 - abs(agent.stance - message.stance)))
        international_penalty = RuleDecisionLayer.compute_international_penalty(agent, message)
        adjusted_sim = max(0.0, stance_sim - international_penalty)
        memory_bonus = RuleDecisionLayer.compute_memory_bias(agent, message)
        
        action, score = RuleDecisionLayer.decide_action(
            agent_stance=agent.stance,
            message_stance=message.stance,
            message_emotion=message.emotion,
            agent_emotion=agent.emotion,
            agent_activeness=agent.activeness,
            agent_bot_prob=agent.bot_prob,
            memory_bonus=memory_bonus
        )
        
        return action, score

    def _generate_text(
        self,
        agent,
        message: Message,
        action: str,
        use_llm: bool = False
    ) -> tuple[str, bool, Optional[str]]:
        """生成传播文本，返回文本、是否实际使用LLM和错误信息"""
        if use_llm and self.llm_generator:
            try:
                if action == "repost":
                    text = self.llm_generator.generate_forward_text(agent, message)
                else:
                    text = self.llm_generator.generate_comment(agent, message)
                return text, True, None
            except Exception as e:
                print(f"[SemanticEngine] LLM生成失败，回退到规则模板: {e}")
                return self._template_generation(agent, message, action), False, str(e)

        # 规则模板回退
        return self._template_generation(agent, message, action), False, None

    def _template_generation(
        self,
        agent,
        message: Message,
        action: str
    ) -> str:
        """规则模板生成"""
        emotion_word = self._emotion_to_word(message.emotion)
        stance_word = self._stance_to_word(
            agent.stance, message.stance,
            max(0.0, min(1.0, 1 - abs(agent.stance - message.stance)))
        )
        
        if action == "repost":
            templates = [
                f"分享：{message.content}。{emotion_word}，很{stance_word}。",
                f"转发：{message.content}。这条信息{emotion_word}。",
                f"{message.content} —— {stance_word}的观点。"
            ]
        else:
            templates = [
                f"评论：{message.content}。我的想法是{emotion_word}。",
                f"这条信息{emotion_word}，我觉得{stance_word}。",
                f"对于\"{message.content}\"，我有点{emotion_word}。"
            ]

        
        return random.choice(templates)

    @staticmethod
    def _emotion_to_word(emotion: float) -> str:
        if emotion > 0.8:
            return "很激烈"
        elif emotion > 0.6:
            return "比较强烈"
        elif emotion > 0.4:
            return "有所关注"
        return "平稳"

    @staticmethod
    def _stance_to_word(agent_stance: float, message_stance: float, similarity: float) -> str:
        if similarity > 0.7:
            return "一致"
        elif similarity > 0.4:
            return "部分认同"
        else:
            return "不同看法"
