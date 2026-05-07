"""
推荐引擎（Recommendation Engine）
功能：
- 计算平台推荐评分
- 支持 feed / 热榜 / 社交推荐
- 输出推荐日志信息
"""
import random
from typing import Dict, List, Tuple

from .propagation_model import stance_similarity


class RecommendationEngine:
    """模拟平台推荐算法。"""

    def score(
        self,
        agent,
        message,
        source: str = "feed"
    ) -> float:
        """计算推荐评分。"""
        interest = stance_similarity(getattr(agent, "stance", 0.0), getattr(message, "stance", 0.0))
        emotion = getattr(message, "emotion", 0.5)
        interaction_rate = min(1.0, getattr(agent, "activeness", 0.5) * 0.6 + (1 - getattr(agent, "bot_prob", 0.5)) * 0.4)
        hotness = min(1.0, 0.4 + 0.6 * emotion)
        controversy = min(1.0, abs(getattr(message, "stance", 0.0)))

        score = (
            0.3 * interest
            + 0.2 * emotion
            + 0.2 * hotness
            + 0.2 * interaction_rate
            + 0.1 * controversy
        )

        source_bonus = {
            "feed": 1.0,
            "hotlist": 1.1,
            "social": 0.95
        }.get(source, 1.0)

        score *= source_bonus
        score = max(0.0, min(1.0, score))

        # 增加一定噪声，避免完全确定性
        score = max(0.0, min(1.0, score + random.uniform(-0.05, 0.05)))
        return score

    def recommend(
        self,
        G,
        message,
        exclude_ids: List[str],
        source: str = "feed",
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """为非邻居节点生成推荐列表。"""
        candidates: List[Tuple[float, str]] = []

        for node_id, data in G.nodes(data=True):
            if node_id in exclude_ids:
                continue
            agent = data.get("obj")
            if agent is None:
                continue
            score = self.score(agent, message, source)
            if score > 0.1:
                candidates.append((score, node_id))

        candidates.sort(key=lambda item: item[0], reverse=True)
        return [(node_id, score) for score, node_id in candidates[:top_k]]

    def recommend_to_neighbors_of_neighbors(
        self,
        G,
        message,
        source: str = "social",
        top_k: int = 5
    ) -> List[Tuple[str, float, str]]:
        """基于社交关系进行推荐。"""
        results: List[Tuple[str, float, str]] = []
        for node_id, data in G.nodes(data=True):
            agent = data.get("obj")
            if agent is None:
                continue
            neighbors = list(G.predecessors(node_id))
            if not neighbors:
                continue
            score = self.score(agent, message, source)
            if score > 0.1:
                results.append((node_id, score, source))

        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]
