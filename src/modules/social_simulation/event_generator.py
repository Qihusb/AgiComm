"""
事件生成器（Event Generator）
功能：
- 生成初始事件（种子Message）
- 支持多种事件类型
- 为传播仿真提供初始消息
"""
import random
from datetime import datetime
from typing import List, Dict, Optional
from .message import Message


class EventGenerator:
    """
    事件生成器 - 生成初始事件/消息
    """
    
    # 预定义的事件模板库
    EVENT_TEMPLATES = {
        "tech_positive": {
            "contents": [
                "科技创新带来了新的机遇和希望",
                "某公司发布了革命性的新技术产品",
                "科研突破为人类进步打开了新大门",
                "新兴技术应用改善了人们的生活质量"
            ],
            "stance_range": (0.5, 1.0),
            "emotion_range": (0.6, 0.9)
        },
        "tech_negative": {
            "contents": [
                "科技发展带来的隐私泄露问题愈发严重",
                "人工智能可能威胁人类未来",
                "某科技公司的垄断行为引发争议",
                "技术失误导致了严重的社会影响"
            ],
            "stance_range": (-1.0, -0.5),
            "emotion_range": (0.6, 0.9)
        },
        "tech_neutral": {
            "contents": [
                "关于科技发展方向的学术讨论",
                "业内对技术标准的不同看法",
                "技术应用的多角度分析报告",
                "科技政策的平衡性思考"
            ],
            "stance_range": (-0.3, 0.3),
            "emotion_range": (0.3, 0.5)
        },
        "social_hotspot": {
            "contents": [
                "最近发生的社会热点事件引发讨论",
                "舆论聚焦的新闻话题",
                "公众高度关注的突发事件",
                "引起广泛争议的社会现象"
            ],
            "stance_range": (-0.8, 0.8),
            "emotion_range": (0.7, 1.0)
        },
        "science_breakthrough": {
            "contents": [
                "科学家取得了重要研究突破",
                "新发现改变了人们的理解",
                "学术界评价这一成果意义重大",
                "这项研究可能产生深远影响"
            ],
            "stance_range": (0.4, 1.0),
            "emotion_range": (0.5, 0.8)
        },
        "controversial_opinion": {
            "contents": [
                "引起争议的观点被提出",
                "专家发表了有争议的言论",
                "社会观点发生了分歧",
                "不同群体对此有完全相反的看法"
            ],
            "stance_range": (-1.0, 1.0),
            "emotion_range": (0.6, 0.95)
        }
    }
    
    def __init__(self):
        """初始化事件生成器"""
        pass
    
    def generate_event(
        self,
        event_type: str = "social_hotspot",
        custom_content: Optional[str] = None,
        custom_emotion: Optional[float] = None,
        custom_stance: Optional[float] = None,
        source_id: Optional[str] = None
    ) -> Message:
        """
        生成初始事件
        
        Args:
            event_type: 事件类型（tech_positive/tech_negative/tech_neutral/social_hotspot/etc）
            custom_content: 自定义内容（如果提供则覆盖模板）
            custom_emotion: 自定义情感强度
            custom_stance: 自定义立场
            source_id: 事件源ID（如媒体ID）
            
        Returns:
            Message对象
        """
        # 获取模板
        template = self.EVENT_TEMPLATES.get(
            event_type,
            self.EVENT_TEMPLATES["social_hotspot"]
        )
        
        # 生成内容
        if custom_content is None:
            content = random.choice(template["contents"])
        else:
            content = custom_content
        
        # 生成情感强度
        if custom_emotion is None:
            emotion_min, emotion_max = template["emotion_range"]
            emotion = random.uniform(emotion_min, emotion_max)
        else:
            emotion = custom_emotion
        
        # 生成立场
        if custom_stance is None:
            stance_min, stance_max = template["stance_range"]
            stance = random.uniform(stance_min, stance_max)
        else:
            stance = custom_stance
        
        return Message(
            content=content,
            emotion=emotion,
            stance=stance,
            source_id=source_id,
            timestamp=datetime.now(),
            propagation_depth=0
        )
    
    def generate_multiple_events(
        self,
        count: int = 5,
        event_types: Optional[List[str]] = None
    ) -> List[Message]:
        """
        生成多个事件
        
        Args:
            count: 要生成的事件数量
            event_types: 事件类型列表（如果None则随机）
            
        Returns:
            Message列表
        """
        events = []
        
        for i in range(count):
            if event_types:
                event_type = random.choice(event_types)
            else:
                event_type = random.choice(list(self.EVENT_TEMPLATES.keys()))
            
            event = self.generate_event(
                event_type=event_type,
                source_id=f"media_{i}"
            )
            events.append(event)
        
        return events
    
    def generate_custom_event(
        self,
        content: str,
        emotion: float,
        stance: float,
        source_id: Optional[str] = None
    ) -> Message:
        """
        生成自定义事件
        
        Args:
            content: 事件内容
            emotion: 情感强度 [0, 1]
            stance: 立场 [-1, 1]
            source_id: 事件源ID
            
        Returns:
            Message对象
        """
        return Message(
            content=content,
            emotion=max(0.0, min(1.0, emotion)),
            stance=max(-1.0, min(1.0, stance)),
            source_id=source_id,
            timestamp=datetime.now(),
            propagation_depth=0
        )
    
    def list_event_types(self) -> List[str]:
        """
        列出所有可用的事件类型
        
        Returns:
            事件类型列表
        """
        return list(self.EVENT_TEMPLATES.keys())
    
    def get_event_template_info(self, event_type: str) -> Dict:
        """
        获取事件类型的详细信息
        
        Args:
            event_type: 事件类型
            
        Returns:
            包含情感范围和立场范围的字典
        """
        template = self.EVENT_TEMPLATES.get(event_type)
        if template:
            return {
                "type": event_type,
                "emotion_range": template["emotion_range"],
                "stance_range": template["stance_range"],
                "sample_contents": template["contents"][:2]
            }
        return None
