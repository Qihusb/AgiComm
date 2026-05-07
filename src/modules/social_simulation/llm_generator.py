"""
LLM生成层 - 负责语义表达增强

功能：
- 根据Agent画像生成拟人化文本
- 支持多国家/多语言表达
- 支持记忆驱动的一致性表达
- 支持async批量生成
- enable_llm=False 时自动回退规则模板
"""
import os
import sys
import random
from typing import Dict, Optional, List
from .message import Message

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'utils'))
    from src.utils.llm_client import llm_client
except ImportError:
    llm_client = None


class LLMGenerator:
    """LLM语义生成器"""
    
    # 国家/文化表达风格模板
    CULTURE_TEMPLATES = {
        "CN": {
            "repost_prefix": ["转发", "分享", "同意观点"],
            "comment_prefix": ["补充一下", "我的看法是", "针对这点"],
            "emotional_markers": ["很", "特别", "非常"]
        },
        "US": {
            "repost_prefix": ["Reposting", "Sharing", "I agree"],
            "comment_prefix": ["To add on", "My take is", "On this point"],
            "emotional_markers": ["very", "quite", "really"]
        },
        "DE": {
            "repost_prefix": ["Weitergabe", "Teile diesen", "Ich stimme zu"],
            "comment_prefix": ["Dazu möchte ich", "Meine Sicht", "Bezüglich"],
            "emotional_markers": ["sehr", "ziemlich", "recht"]
        },
        "FR": {
            "repost_prefix": ["Partage", "Je partage", "D'accord"],
            "comment_prefix": ["Pour ajouter", "Mon avis est", "Sur ce point"],
            "emotional_markers": ["très", "assez", "plutôt"]
        },
        "default": {
            "repost_prefix": ["Share", "Forward", "Agree"],
            "comment_prefix": ["Add comment", "My view", "On this"],
            "emotional_markers": ["very", "quite", "really"]
        }
    }

    def __init__(self, enable_llm: bool = False):
        """
        初始化LLM生成器
        
        Args:
            enable_llm: 是否启用真实LLM调用
        """
        self.enable_llm = enable_llm and llm_client is not None
        self.cache = {}  # 简单缓存
        self.generation_history = {}

    def generate_forward_text(
        self,
        agent,
        message: Message,
        use_llm: bool = None
    ) -> str:
        """生成转发文本"""
        use_llm = use_llm if use_llm is not None else self.enable_llm
        
        cache_key = f"forward_{agent.id}_{message.id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if use_llm and llm_client is not None:
            try:
                text = self._llm_generate_forward(agent, message)
                self.cache[cache_key] = text
                return text
            except Exception as e:
                print(f"[LLMGenerator] LLM失败: {e}，回退规则模板")
        
        # 规则模板
        text = self._template_forward(agent, message)
        self.cache[cache_key] = text
        return text

    def generate_comment(
        self,
        agent,
        message: Message,
        use_llm: bool = None
    ) -> str:
        """生成评论文本"""
        use_llm = use_llm if use_llm is not None else self.enable_llm
        
        cache_key = f"comment_{agent.id}_{message.id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if use_llm and llm_client is not None:
            try:
                text = self._llm_generate_comment(agent, message)
                self.cache[cache_key] = text
                return text
            except Exception as e:
                print(f"[LLMGenerator] LLM失败: {e}，回退规则模板")
        
        # 规则模板
        text = self._template_comment(agent, message)
        self.cache[cache_key] = text
        return text

    def generate_emotion_expression(
        self,
        agent,
        emotion: float,
        language: str = "zh"
    ) -> str:
        """生成情绪表达"""
        if language == "zh":
            if emotion > 0.8:
                return random.choice(["很激烈", "特别强烈", "非常关注"])
            elif emotion > 0.6:
                return random.choice(["比较强烈", "有点激动", "很感兴趣"])
            elif emotion > 0.4:
                return random.choice(["有所关注", "挺关心", "在意"])
            else:
                return random.choice(["平稳", "一般", "不太关注"])
        elif language == "en":
            if emotion > 0.8:
                return random.choice(["very intense", "quite passionate", "extremely concerned"])
            elif emotion > 0.6:
                return random.choice(["fairly strong", "somewhat passionate", "quite interested"])
            elif emotion > 0.4:
                return random.choice(["somewhat interested", "kind of interested", "moderately concerned"])
            else:
                return random.choice(["calm", "neutral", "not much concern"])
        else:
            return "neutral"

    def _template_forward(self, agent, message: Message) -> str:
        """规则模板转发文本"""
        country = getattr(agent, "country", "default")
        language = getattr(agent, "language", "zh")
        culture = self.CULTURE_TEMPLATES.get(country, self.CULTURE_TEMPLATES["default"])
        
        prefix = random.choice(culture["repost_prefix"])
        emotion = self.generate_emotion_expression(agent, message.emotion, language)
        marker = random.choice(culture["emotional_markers"])
        
        if language == "zh":
            templates = [
                f"【转发】{message.content}\n\n{prefix}这条信息，{marker}{emotion}。",
                f"{prefix}：{message.content}\n\n— {agent.ideology}的观点",
                f"{message.content}\n\n我{marker}{emotion}这个话题。"
            ]
        else:
            templates = [
                f"[{prefix}] {message.content}\n\n{marker} {emotion} about this.",
                f"{prefix}: {message.content}\n\n— {agent.ideology} perspective",
                f"{message.content}\n\nI find this {emotion}."
            ]
        
        return random.choice(templates)

    def _template_comment(self, agent, message: Message) -> str:
        """规则模板评论文本 - 修复嵌套引用问题"""
        country = getattr(agent, "country", "default")
        language = getattr(agent, "language", "zh")
        culture = self.CULTURE_TEMPLATES.get(country, self.CULTURE_TEMPLATES["default"])
        
        prefix = random.choice(culture["comment_prefix"])
        emotion = self.generate_emotion_expression(agent, message.emotion, language)
        marker = random.choice(culture["emotional_markers"])
        
        # 避免直接引用message.content，使用更自然的表达
        if language == "zh":
            templates = [
                f"{prefix}：这条消息{marker}{emotion}。",
                f"对此我想说：虽然{emotion}，但我有不同的看法。",
                f"我的想法：这事确实{marker}{emotion}。"
            ]
        else:
            templates = [
                f"{prefix}: This message is {emotion}.",
                f"On this: While {emotion}, I have a different view.",
                f"My take: This is indeed {marker} {emotion}."
            ]
        
        return random.choice(templates)

    def _llm_generate_forward(self, agent, message: Message) -> str:
        """LLM生成转发文本"""
        if llm_client is None:
            return self._template_forward(agent, message)
        
        persona = self._build_persona(agent)
        prompt = f"""
你是一个{agent.country}的社交媒体用户，ID: {agent.id}。
个人资料：{persona}

你看到这条信息："{message.content}"
这条信息的情绪指数是 {message.emotion:.2f}，立场分数是 {message.stance:.2f}。

请生成一条简洁的转发文本（一句话，不超过50字）。
要求：
- 符合你的立场和情绪
- 如果你来自{agent.country}，使用该国的表达风格
- 显示你的观点而不仅仅是复述原文
"""
        try:
            response = llm_client.ask(
                system_prompt="你是一个社交媒体内容创作助手。",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=100
            )
            return response.strip()
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return self._template_forward(agent, message)

    def _llm_generate_comment(self, agent, message: Message) -> str:
        """LLM生成评论文本"""
        if llm_client is None:
            return self._template_comment(agent, message)
        
        persona = self._build_persona(agent)
        # 获取最近的立场相关记忆
        recent_views = self._get_recent_stance_views(agent)
        
        prompt = f"""
你是一个{agent.country}的社交媒体用户，ID: {agent.id}。
个人资料：{persona}

最近的立场观点：{recent_views}

你看到这条信息："{message.content}"
情绪指数: {message.emotion:.2f}，立场分数: {message.stance:.2f}

请生成一条简洁的评论（一句话，不超过60字）。
要求：
- 与你之前的观点保持一致性
- 显示你的个人观点
- 可以同意、部分同意或不同意，但要有理由
"""
        try:
            response = llm_client.ask(
                system_prompt="你是一个社交媒体内容创作助手。",
                user_prompt=prompt,
                temperature=0.6,
                max_tokens=120
            )
            return response.strip()
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return self._template_comment(agent, message)

    def _build_persona(self, agent) -> str:
        """构建Agent人设"""
        ideology = getattr(agent, "ideology", "neutral")
        stance = getattr(agent, "stance", 0.0)
        emotion = getattr(agent, "emotion", 0.5)
        
        if stance > 0.5:
            stance_desc = "支持科技创新"
        elif stance < -0.5:
            stance_desc = "对科技持谨慎态度"
        else:
            stance_desc = "立场中立"
        
        emotion_desc = "情绪易激动" if emotion > 0.6 else "情绪稳定"
        
        return f"意识形态: {ideology}, {stance_desc}, {emotion_desc}"

    def _get_recent_stance_views(self, agent, limit: int = 3) -> str:
        """获取最近的立场观点（用于一致性）"""
        if not hasattr(agent, "memory") or not agent.memory:
            return "暂无"
        
        recent = agent.memory[-limit:]
        views = []
        for entry in recent:
            if entry.get("narrative_type") == "stance":
                views.append(f"- {entry.get('content', 'N/A')}")
        
        return "\n".join(views) if views else "暂无"

    def compute_semantic_quality(
        self,
        generated_text: str,
        agent,
        message: Message
    ) -> float:
        """计算生成文本的语义质量"""
        quality = 0.5
        
        # 长度奖励
        text_len = len(generated_text)
        if 20 <= text_len <= 200:
            quality += 0.2
        
        # 多样性（避免纯模板）
        unique_words = len(set(generated_text.split()))
        if unique_words > 5:
            quality += 0.15
        
        # 观点一致性（如果涉及立场）
        agent_stance = getattr(agent, "stance", 0.0)
        message_stance = getattr(message, "stance", 0.0)
        stance_diff = abs(agent_stance - message_stance)
        if stance_diff < 0.5:
            quality += 0.15
        
        return max(0.0, min(1.0, quality))

    def compute_controversy_score(
        self,
        generated_text: str,
        message: Message
    ) -> float:
        """计算争议性指数"""
        controversy = 0.5
        
        # 情感强度贡献
        controversy += message.emotion * 0.2
        
        # 立场极端性
        if abs(message.stance) > 0.7:
            controversy += 0.2
        
        # 文本长度（更长=更详细=可能更有争议）
        if len(generated_text) > 100:
            controversy += 0.1
        
        return max(0.0, min(1.0, controversy))
