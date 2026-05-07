"""
Persona生成器（Persona Builder）
功能：
- 将Agent的数值属性转换为自然语言描述
- 用于LLM提示词的构建
- 为未来LLM集成做准备
"""
from typing import Dict


class PersonaBuilder:
    """
    将Agent属性转换为自然语言Person描述
    """
    
    # 立场描述映射
    STANCE_LEVELS = {
        "strong_support": (0.7, 1.0, "坚定支持者"),
        "support": (0.4, 0.7, "支持者"),
        "neutral": (-0.4, 0.4, "中立者"),
        "oppose": (-0.7, -0.4, "反对者"),
        "strong_oppose": (-1.0, -0.7, "坚定反对者")
    }
    
    # 情感水平描述
    EMOTION_LEVELS = {
        "very_high": (0.8, 1.0, "非常激情/愤怒"),
        "high": (0.6, 0.8, "较为激情"),
        "medium": (0.4, 0.6, "适度关注"),
        "low": (0.2, 0.4, "平淡无奇"),
        "very_low": (0.0, 0.2, "冷漠")
    }
    
    # 活跃度描述
    ACTIVENESS_LEVELS = {
        "very_active": (0.8, 1.0, "极度活跃"),
        "active": (0.6, 0.8, "活跃"),
        "moderate": (0.4, 0.6, "中等活跃"),
        "passive": (0.2, 0.4, "被动"),
        "very_passive": (0.0, 0.2, "极度被动")
    }
    
    # 影响力描述
    INFLUENCE_LEVELS = {
        "high_influence": (0.7, 1.0, "高影响力"),
        "medium_influence": (0.4, 0.7, "中等影响力"),
        "low_influence": (0.0, 0.4, "低影响力")
    }
    
    # 认知熵描述
    ENTROPY_LEVELS = {
        "high_entropy": (0.7, 1.0, "高认知熵（观点多元、不确定）"),
        "medium_entropy": (0.4, 0.7, "中等认知熵"),
        "low_entropy": (0.0, 0.4, "低认知熵（观点单一、确定性强）")
    }
    
    def __init__(self):
        """初始化Persona生成器"""
        pass
    
    def build_persona(self, agent) -> str:
        """
        生成Agent的自然语言Persona描述
        
        Args:
            agent: UserAgent对象
            
        Returns:
            Persona描述字符串
        """
        # 各维度的描述
        stance_desc = self._describe_stance(agent.stance)
        emotion_desc = self._describe_emotion(agent.emotion)
        activeness_desc = self._describe_activeness(agent.activeness)
        influence_desc = self._describe_influence(agent.influence)
        entropy_desc = self._describe_entropy(agent.entropy)
        
        # 构建完整的Persona
        persona = (
            f"网络用户 {agent.id}：\n"
            f"- 立场特征：{stance_desc}\n"
            f"- 情感状态：{emotion_desc}\n"
            f"- 活跃程度：{activeness_desc}\n"
            f"- 影响力：{influence_desc}\n"
            f"- 认知特点：{entropy_desc}"
        )
        
        return persona
    
    def build_persona_summary(self, agent) -> str:
        """
        生成Agent的简短Persona描述（用于快速参考）
        
        Args:
            agent: UserAgent对象
            
        Returns:
            简短Persona描述
        """
        stance_desc = self._describe_stance(agent.stance)
        emotion_desc = self._describe_emotion(agent.emotion)
        activeness_desc = self._describe_activeness(agent.activeness)
        
        summary = f"一个{stance_desc}、{emotion_desc}、{activeness_desc}的网络用户"
        
        return summary
    
    def build_persona_dict(self, agent) -> Dict:
        """
        生成Agent的Persona字典（用于结构化存储）
        
        Args:
            agent: UserAgent对象
            
        Returns:
            Persona字典
        """
        return {
            "user_id": agent.id,
            "stance": {
                "score": agent.stance,
                "description": self._describe_stance(agent.stance)
            },
            "emotion": {
                "score": agent.emotion,
                "description": self._describe_emotion(agent.emotion)
            },
            "activeness": {
                "score": agent.activeness,
                "description": self._describe_activeness(agent.activeness)
            },
            "influence": {
                "score": agent.influence,
                "description": self._describe_influence(agent.influence)
            },
            "entropy": {
                "score": agent.entropy,
                "description": self._describe_entropy(agent.entropy)
            },
            "agent_type": getattr(agent, "agent_type", "user")
        }
    
    def _describe_stance(self, score: float) -> str:
        """描述立场"""
        for level, (min_val, max_val, desc) in self.STANCE_LEVELS.items():
            if min_val <= score < max_val:
                return desc
        return "中立者"
    
    def _describe_emotion(self, score: float) -> str:
        """描述情感"""
        for level, (min_val, max_val, desc) in self.EMOTION_LEVELS.items():
            if min_val <= score < max_val:
                return desc
        return "适度关注"
    
    def _describe_activeness(self, score: float) -> str:
        """描述活跃度"""
        for level, (min_val, max_val, desc) in self.ACTIVENESS_LEVELS.items():
            if min_val <= score < max_val:
                return desc
        return "中等活跃"
    
    def _describe_influence(self, score: float) -> str:
        """描述影响力"""
        for level, (min_val, max_val, desc) in self.INFLUENCE_LEVELS.items():
            if min_val <= score < max_val:
                return desc
        return "低影响力"
    
    def _describe_entropy(self, score: float) -> str:
        """描述认知熵"""
        for level, (min_val, max_val, desc) in self.ENTROPY_LEVELS.items():
            if min_val <= score < max_val:
                return desc
        return "中等认知熵"
