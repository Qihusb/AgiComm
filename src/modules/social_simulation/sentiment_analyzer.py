"""
情感分析器（Sentiment Analyzer）
功能：
- 对生成文本进行情感分析
- 更新Agent状态（情感反馈闭环）
- 结合疲劳与历史记忆影响立场演化
"""
from typing import Dict, Tuple


class SentimentAnalyzer:
    """简单情感分析器"""

    EMOTION_KEYWORDS = {
        "positive": ["支持", "赞同", "同意", "好的", "太好了", "很棒", "喜欢"],
        "negative": ["反对", "不同意", "反感", "可怕", "可恶", "讨厌", "愤怒", "震惊"],
        "neutral": ["可能", "也许", "不确定", "需要", "考虑"]
    }

    EMOTION_WEIGHTS = {
        "positive": 0.6,
        "negative": 0.8,
        "neutral": 0.4
    }

    STANCE_KEYWORDS = {
        "support": ["支持", "赞同", "同意", "好的", "认可", "拥护"],
        "oppose": ["反对", "不同意", "反感", "否决", "拒绝"],
        "neutral": ["可能", "有可能", "不确定", "中立", "平衡"]
    }

    def __init__(self):
        pass

    def analyze_sentiment(self, text: str) -> float:
        if not text:
            return 0.5

        positive_score = self._count_keywords(text, self.EMOTION_KEYWORDS["positive"])
        negative_score = self._count_keywords(text, self.EMOTION_KEYWORDS["negative"])
        neutral_score = self._count_keywords(text, self.EMOTION_KEYWORDS["neutral"])

        if positive_score > 0 or negative_score > 0 or neutral_score > 0:
            total = (
                positive_score * self.EMOTION_WEIGHTS["positive"]
                + negative_score * self.EMOTION_WEIGHTS["negative"]
                + neutral_score * self.EMOTION_WEIGHTS["neutral"]
            )
            emotion = total / max(positive_score, negative_score, neutral_score, 1)
            return min(1.0, emotion)

        return 0.5

    def analyze_stance(self, text: str) -> float:
        if not text:
            return 0.0

        support_score = self._count_keywords(text, self.STANCE_KEYWORDS["support"])
        oppose_score = self._count_keywords(text, self.STANCE_KEYWORDS["oppose"])
        neutral_score = self._count_keywords(text, self.STANCE_KEYWORDS["neutral"])

        if support_score > 0 or oppose_score > 0:
            stance = (support_score - oppose_score) / (support_score + oppose_score)
            return max(-1.0, min(1.0, stance))

        if neutral_score > 0:
            return 0.0

        return 0.0

    def update_agent_state(
        self,
        agent,
        generated_text: str,
        emotion_shift: float,
        stance_shift: float,
        action: str,
        consecutive_exposure: int = 1
    ) -> Tuple[float, float]:
        text_emotion = self.analyze_sentiment(generated_text)
        text_stance = self.analyze_stance(generated_text)

        update_strength = {
            "repost": 0.5,
            "comment": 0.3,
            "ignore": 0.0
        }.get(action, 0.0)

        combined_emotion = text_emotion + emotion_shift
        combined_emotion = max(0.0, min(1.0, combined_emotion))
        new_emotion = 0.7 * agent.emotion + 0.3 * combined_emotion
        new_emotion = max(0.0, min(1.0, new_emotion))

        combined_stance = text_stance + stance_shift
        combined_stance = max(-1.0, min(1.0, combined_stance))
        new_stance = 0.7 * agent.stance + 0.3 * combined_stance
        new_stance = max(-1.0, min(1.0, new_stance))

        agent.emotion = new_emotion
        agent.stance = new_stance

        if action == "repost":
            agent.activeness = min(1.0, agent.activeness + 0.05)
            agent.fatigue = min(1.0, agent.fatigue + 0.05)
        elif action == "comment":
            agent.activeness = min(1.0, agent.activeness + 0.02)
            agent.fatigue = min(1.0, agent.fatigue + 0.03)
        else:
            agent.activeness = max(0.0, agent.activeness - 0.01)
            agent.fatigue = min(1.0, agent.fatigue + 0.02)

        if consecutive_exposure > 2 and text_emotion > 0.7:
            agent.fatigue = min(1.0, agent.fatigue + 0.05)

        self._decay_long_term_memory(agent, text_stance, text_emotion)

        return new_emotion, new_stance

    def _decay_long_term_memory(self, agent, stance_value: float, emotion_value: float):
        if hasattr(agent, "memory"):
            agent.memory = agent.memory[-50:]
            if getattr(agent, "memory", None) is not None:
                if len(agent.memory) > 0 and agent.memory[-1].get("stance") == stance_value:
                    agent.memory[-1]["weight"] = min(1.0, agent.memory[-1].get("weight", 0.5) + 0.05)

    def _count_keywords(self, text: str, keywords: list) -> int:
        count = 0
        for keyword in keywords:
            count += text.count(keyword)
        return count

    def analyze_text(self, text: str) -> Dict:
        emotion = self.analyze_sentiment(text)
        stance = self.analyze_stance(text)
        is_strong = emotion > 0.6 and abs(stance) > 0.4
        return {
            "emotion": emotion,
            "stance": stance,
            "is_strong_opinion": is_strong
        }
