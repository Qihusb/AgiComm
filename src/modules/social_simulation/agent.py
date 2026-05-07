import random
from datetime import datetime
from typing import Any, Dict, List, Optional


class UserAgent:
    def __init__(self, data_row: Any, agent_type: str = "user"):
        """
        用户/媒体代理初始化
        """
        self.id = data_row["handle"]
        self.agent_type = agent_type

        self.followers = float(data_row.get("followers", 0.0))
        self.activeness = float(data_row.get("daily_activeness", 0.0))
        self.influence = float(data_row.get("influence_index", 0.0))
        self.bot_prob = float(data_row.get("bot_probability", 0.0))
        self.stance = float(data_row.get("tech_stance_score", 0.0))
        self.emotion = float(data_row.get("emotion_intensity", 0.0))
        self.speed = float(data_row.get("propagation_speed", 0.0))
        self.entropy = float(data_row.get("cognitive_entropy", 0.0))

        self.country = data_row.get("country") or self._random_country()
        self.language = data_row.get("language") or self._language_by_country(self.country)
        self.ideology = data_row.get("ideology") or self._random_ideology()
        self.culture_bias = float(data_row.get("culture_bias", random.uniform(0.0, 1.0)))
        self.community_id = data_row.get("community_id") or self.country or f"community_{random.randint(0, 3)}"

        self.active = False
        self.fatigue = float(data_row.get("fatigue", 0.0))
        self.attention_capacity = int(max(1, data_row.get("attention_capacity", 3 + round(self.activeness * 4))))
        self.current_attention = 0
        self.exposure_count = 0
        self.exposure_history: List[Dict[str, Any]] = []
        self.memory: List[Dict[str, Any]] = []
        self.trust_history: List[Dict[str, Any]] = []
        self.interaction_history: List[Dict[str, Any]] = []
        self.timezone_offset = int(data_row.get("timezone_offset", random.choice([-8, -5, 0, 1, 8, 9])))
        self.active_time_distribution = data_row.get("active_time_distribution") or self._default_time_distribution()
        self.last_exposure_time: Optional[datetime] = None

        self.initial_emotion = self.emotion
        self.initial_stance = self.stance
        self.initial_activeness = self.activeness

    def _random_country(self) -> str:
        return random.choice(["US", "CN", "IN", "DE", "FR", "BR", "JP"])

    def _language_by_country(self, country: str) -> str:
        mapping = {
            "US": "en",
            "CN": "zh",
            "IN": "en",
            "DE": "de",
            "FR": "fr",
            "BR": "pt",
            "JP": "ja"
        }
        return mapping.get(country, "en")

    def _random_ideology(self) -> str:
        return random.choice(["liberal", "conservative", "neutral", "tech_optimist", "tech_skeptic"])

    def _default_time_distribution(self) -> Dict[str, float]:
        return {
            "morning": random.uniform(0.2, 0.8),
            "afternoon": random.uniform(0.2, 0.9),
            "evening": random.uniform(0.3, 0.9),
            "night": random.uniform(0.05, 0.4)
        }

    def is_active_at(self, current_time: datetime) -> bool:
        local_hour = (current_time.hour + self.timezone_offset) % 24
        if 6 <= local_hour < 12:
            probability = self.active_time_distribution.get("morning", 0.4)
        elif 12 <= local_hour < 18:
            probability = self.active_time_distribution.get("afternoon", 0.6)
        elif 18 <= local_hour < 23:
            probability = self.active_time_distribution.get("evening", 0.7)
        else:
            probability = self.active_time_distribution.get("night", 0.2)
        return random.random() < probability

    def can_process_message(self) -> bool:
        return self.current_attention < self.attention_capacity and self.fatigue < 0.95

    def record_exposure(self, message, probability: float, current_time: datetime):
        self.exposure_count += 1
        self.exposure_history.append({
            "message_id": getattr(message, "id", None),
            "timestamp": current_time.isoformat(),
            "probability": probability
        })
        self.last_exposure_time = current_time

    def record_interaction(self, action: str, message, score: float):
        self.interaction_history.append({
            "action": action,
            "message_id": getattr(message, "id", None),
            "score": score,
            "time": datetime.now().isoformat()
        })

    def add_memory(self, entry: Dict[str, Any]):
        self.memory.append(entry)
        if len(self.memory) > 50:
            self.memory.pop(0)

    def update_state(self, influencer=None, influence_factor: float = 0.1):
        """
        动态更新机制（Dynamic Update）⭐
        """
        if influencer is None:
            self.emotion = max(0.0, self.emotion - 0.01)
            self.entropy = min(1.0, self.entropy + 0.005)
            self.activeness = max(0.0, self.activeness - 0.02)
            self.fatigue = max(0.0, self.fatigue - 0.01)
            self.current_attention = 0
            return

        fatigue_penalty = min(0.3, self.fatigue)
        emotion_weight = influence_factor * (0.3 - fatigue_penalty * 0.1)
        self.emotion = (1 - emotion_weight) * self.emotion + emotion_weight * influencer.emotion
        self.emotion = max(0.0, min(1.0, self.emotion))

        stance_weight = influence_factor * 0.2
        stance_diff = influencer.stance - self.stance
        self.stance += stance_weight * stance_diff
        self.stance = max(-1.0, min(1.0, self.stance))

        entropy_reduction = influence_factor * 0.1
        self.entropy = max(0.0, self.entropy - entropy_reduction)

        activeness_boost = influence_factor * 0.05
        activeness_decay = 0.01
        self.activeness = max(0.0, min(1.0, self.activeness + activeness_boost - activeness_decay))

        influence_boost = influence_factor * 0.02
        self.influence = min(1.0, self.influence + influence_boost)

        self.fatigue = min(1.0, self.fatigue + 0.03)
        self.current_attention = min(self.attention_capacity, self.current_attention + 1)

    def reset_attention(self):
        self.current_attention = 0

    def apply_overload(self):
        if self.current_attention >= self.attention_capacity or self.fatigue > 0.8:
            self.fatigue = min(1.0, self.fatigue + 0.05)
            self.activeness = max(0.0, self.activeness - 0.03)
