"""
改进的传播概率模型
核心变化：从"纯概率"升级为"语义+概率+社群+疲劳+国际差异+语义质量驱动"

新增：
- semantic_quality权重：高质量内容更容易传播
- controversy权重：争议性话题更容易激起传播
"""
import math
from typing import Dict, Optional


def sigmoid(x: float) -> float:
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def stance_similarity(agent_stance: float, message_stance: float) -> float:
    diff = abs(agent_stance - message_stance)
    return max(0.0, min(1.0, 1 - diff))


def _community_factor(agent, message) -> float:
    if getattr(agent, "community_id", None) and getattr(message, "origin_country", None):
        return 1.2 if agent.community_id == getattr(message, "origin_country", None) else 0.85
    return 1.0


def _fatigue_factor(agent) -> float:
    fatigue = getattr(agent, "fatigue", 0.0)
    return max(0.4, 1.0 - fatigue * 0.5)  # 降低疲劳惩罚


def _attention_factor(agent) -> float:
    capacity = max(1, getattr(agent, "attention_capacity", 3))
    current = getattr(agent, "current_attention", 0)
    return max(0.3, 1.0 - (current / capacity) * 0.4)


def _international_factor(agent, message) -> float:
    if getattr(agent, "country", None) and getattr(message, "origin_country", None):
        if agent.country == message.origin_country:
            return 1.0
        return 0.9 if getattr(agent, "language", None) == getattr(message, "language", None) else 0.8  # 提高国际传播概率
    return 1.0


def _competition_penalty(agent) -> float:
    active_memory = len(getattr(agent, "memory", []))
    return max(0.7, 1.0 - min(0.3, active_memory * 0.01))  # 降低竞争惩罚


def _semantic_quality_factor(message) -> float:
    """语义质量增益"""
    semantic_quality = getattr(message, "semantic_quality", 0.5)
    return 0.9 + semantic_quality * 0.3  # [0.9, 1.2] 提高基础值


def _controversy_factor(message) -> float:
    """争议性增益"""
    controversy = getattr(message, "controversy_score", 0.5)
    return 0.9 + controversy * 0.3  # [0.9, 1.2]


def compute_propagation_prob(
    agent_i,
    message,
    semantic_result: Optional[Dict] = None
) -> float:
    """
    计算传播概率（纳入语义质量与争议性）
    
    Args:
        agent_i: 传播Agent
        message: Message对象
        semantic_result: 语义引擎结果（可选）
    
    Returns:
        最终传播概率 [0, 1]
    """
    A = getattr(agent_i, "activeness", 0.5)
    I = getattr(agent_i, "influence", 0.0)
    E = getattr(message, "emotion", 0.5)
    B = getattr(agent_i, "bot_prob", 0.0)
    S = stance_similarity(getattr(agent_i, "stance", 0.0), getattr(message, "stance", 0.0))

    base_score = 0.3 * A + 0.3 * I + 0.25 * E + 0.25 * S - 0.1 * B
    P_base = sigmoid(base_score)

    if semantic_result is None:
        return P_base

    semantic_score = semantic_result.get("semantic_score", 0.5)
    action = semantic_result.get("action", "ignore")
    if action == "ignore":
        return 0.0

    action_multiplier = {
        "repost": 1.5,  # 进一步增加转发概率
        "comment": 1.0  # 增加评论概率到1.0
    }.get(action, 1.0)

    community_factor = _community_factor(agent_i, message)
    fatigue_factor = _fatigue_factor(agent_i)
    attention_factor = _attention_factor(agent_i)
    international_factor = _international_factor(agent_i, message)
    competition_factor = _competition_penalty(agent_i)
    
    # 新增：语义质量与争议性权重
    semantic_quality_factor = _semantic_quality_factor(message)
    controversy_factor = _controversy_factor(message)

    P_final = (
        P_base
        * semantic_score
        * action_multiplier
        * community_factor
        * fatigue_factor
        * attention_factor
        * international_factor
        * competition_factor
        * semantic_quality_factor  # 语义质量增益
        * controversy_factor  # 争议性增益
    )
    return max(0.0, min(1.0, P_final))


def propagation_prob(agent_i, message, semantic_result: Optional[Dict] = None) -> float:
    """向后兼容的传播概率计算函数"""
    if hasattr(message, "content"):
        return compute_propagation_prob(agent_i, message, semantic_result)
    else:
        agent_j = message
        class TempMessage:
            def __init__(self, agent):
                self.emotion = agent.emotion
                self.stance = agent.stance
                self.origin_country = getattr(agent, "country", None)
                self.language = getattr(agent, "language", None)
                self.semantic_quality = 0.5
                self.controversy_score = 0.5
        temp_message = TempMessage(agent_j)
        return compute_propagation_prob(agent_i, temp_message, semantic_result)
