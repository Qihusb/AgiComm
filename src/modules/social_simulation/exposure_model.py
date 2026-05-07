"""
曝光模型（Exposure Layer）
功能：
- 计算用户是否接触到信息
- 将媒介接触行为作为传播决策前的第一层
"""
from typing import Any, Dict

from .propagation_model import stance_similarity


def compute_exposure_prob(agent, message, context: Dict[str, Any] = None) -> float:
    """计算信息曝光概率。

    Args:
        agent: UserAgent对象
        message: Message对象
        context: 可选上下文字段，包括兴趣匹配、关系强度、热度、平台权重

    Returns:
        曝光概率 [0, 1]
    """
    if context is None:
        context = {}

    activeness = getattr(agent, "activeness", 0.5)
    interest_match = context.get("interest_match")
    if interest_match is None:
        interest_match = stance_similarity(getattr(agent, "stance", 0.0), getattr(message, "stance", 0.0))

    relationship_strength = context.get("relationship_strength", 0.5)
    hotness = context.get("hotness", getattr(message, "emotion", 0.5))
    platform_weight = context.get("platform_weight", 0.5)
    timezone_factor = context.get("timezone_factor", 1.0)

    score = (
        0.25 * activeness
        + 0.25 * interest_match
        + 0.2 * relationship_strength
        + 0.2 * hotness
        + 0.1 * platform_weight
    )

    score *= timezone_factor
    score = max(0.0, min(1.0, score))
    return score
