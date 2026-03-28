import pandas as pd

class MediaAgent:
    def __init__(self, profile_row):
        """
        基于GSS范式的媒体智能体初始化
        :param profile_row: pd.Series, 包含泛化后的媒体属性
        """
        self.id = profile_row['media_id']
        self.name = profile_row['media_name']
        self.country = profile_row['country']
        self.ownership = profile_row['ownership_type']
        
        # 科学认知偏好
        self.persona = {
            "breadth": profile_row['sci_interest_breadth'],
            "dominant_tag": profile_row['sci_dominant_tag'],
            "specialization": profile_row['sci_specialization']
        }
        
        # 提问意图矩阵 (Intent Matrix)
        self.intents = {
            "agenda_setting": profile_row.get('intent_agenda_setting', 0.1),
            "fact_checking": profile_row.get('intent_fact_checking', 0.1),
            "diplomacy": profile_row.get('intent_diplomacy_collab', 0.1),
            "social_impact": profile_row.get('intent_social_impact', 0.1),
            "risk_assessment": profile_row.get('intent_risk_assessment', 0.1)
        }

    def get_persona_description(self):
        """生成供LLM阅读的人设描述"""
        return f"你是一家来自{self.country}的{self.ownership}媒体记者。你的报道核心偏向于{self.persona['dominant_tag']}。"
        