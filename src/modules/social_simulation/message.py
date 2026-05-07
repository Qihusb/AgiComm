"""
Message类 - 文本传播对象
核心特性：
- 所有传播必须传递 Message，而不是"节点状态"
- 不同 Agent 对同一 Message 产生不同响应
- Message 包含内容、情感、立场、叙事和国际化信息
"""
from typing import Optional
from datetime import datetime


class Message:
    """
    文本传播对象
    
    新增语义属性：
    - semantic_quality: 文本语义质量 [0, 1]
    - controversy_score: 争议性指数 [0, 1]
    - emotional_intensity: 情绪强度 [0, 1]
    """

    def __init__(
        self,
        content: str,
        emotion: float,
        stance: float,
        source_id: Optional[str] = None,
        narrative_id: Optional[str] = None,
        narrative_type: str = "general",
        origin_country: Optional[str] = None,
        language: Optional[str] = None,
        hotness: float = 0.5,
        timestamp: Optional[datetime] = None,
        propagation_depth: int = 0,
        semantic_quality: float = 0.5,
        controversy_score: float = 0.5,
        emotional_intensity: float = None
    ):
        self.content = content
        self.emotion = max(0.0, min(1.0, emotion))
        self.stance = max(-1.0, min(1.0, stance))
        self.source_id = source_id
        self.narrative_id = narrative_id or "narrative_0"
        self.narrative_type = narrative_type
        self.origin_country = origin_country
        self.language = language
        self.hotness = max(0.0, min(1.0, hotness))
        self.timestamp = timestamp or datetime.now()
        self.propagation_count = 0
        self.propagation_depth = propagation_depth
        
        # 语义质量属性
        self.semantic_quality = max(0.0, min(1.0, semantic_quality))
        self.controversy_score = max(0.0, min(1.0, controversy_score))
        self.emotional_intensity = max(0.0, min(1.0, emotional_intensity if emotional_intensity is not None else emotion))
        
        self.id = f"{self.narrative_id}_{self.source_id}_{int(self.timestamp.timestamp())}" if self.source_id else f"{self.narrative_id}_{int(self.timestamp.timestamp())}"

    def clone_with_modifications(
        self,
        new_content: str,
        new_emotion: float,
        new_stance: float,
        source_agent_id: str,
        narrative_id: Optional[str] = None,
        narrative_type: Optional[str] = None,
        hotness: Optional[float] = None,
        semantic_quality: Optional[float] = None,
        controversy_score: Optional[float] = None
    ) -> "Message":
        """基于当前Message创建新的Message（代表repost/comment）。"""
        return Message(
            content=new_content,
            emotion=new_emotion,
            stance=new_stance,
            source_id=source_agent_id,
            narrative_id=narrative_id or self.narrative_id,
            narrative_type=narrative_type or self.narrative_type,
            origin_country=self.origin_country,
            language=self.language,
            hotness=hotness if hotness is not None else self.hotness,
            propagation_depth=self.propagation_depth + 1,
            semantic_quality=semantic_quality if semantic_quality is not None else self.semantic_quality * 0.95,
            controversy_score=controversy_score if controversy_score is not None else self.controversy_score * 0.9,
            emotional_intensity=new_emotion
        )

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "emotion": self.emotion,
            "stance": self.stance,
            "source_id": self.source_id,
            "narrative_id": self.narrative_id,
            "narrative_type": self.narrative_type,
            "origin_country": self.origin_country,
            "language": self.language,
            "hotness": self.hotness,
            "timestamp": self.timestamp.isoformat(),
            "propagation_count": self.propagation_count,
            "propagation_depth": self.propagation_depth,
            "semantic_quality": self.semantic_quality,
            "controversy_score": self.controversy_score,
            "emotional_intensity": self.emotional_intensity
        }

    def __repr__(self):
        return (
            f"Message(narrative={self.narrative_id}, source={self.source_id}, "
            f"emotion={self.emotion:.2f}, stance={self.stance:.2f}, depth={self.propagation_depth})"
        )
