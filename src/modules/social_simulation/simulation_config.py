"""
社会传播仿真系统配置
支持实验可控性、参数配置、可复现性

配置优先级：
1. 代码传入的参数
2. 配置文件设置
3. 默认值
"""
import random
import os
from typing import Dict, Optional


class SimulationConfig:
    """仿真配置类"""
    
    # 传播机制参数
    STANCE_SIMILARITY_THRESHOLD = 0.6
    EMOTION_COMMENT_THRESHOLD = 0.7
    EMOTION_REPOST_THRESHOLD = 0.4
    
    # 状态变化参数
    EMOTION_SHIFT_REPOST = 0.5  # 转发时的情感影响系数
    EMOTION_SHIFT_COMMENT = 0.2  # 评论时的情感影响系数
    STANCE_SHIFT_REPOST = 0.3  # 转发时的立场影响系数
    STANCE_SHIFT_COMMENT = 0.1  # 评论时的立场影响系数
    
    # 国际化参数
    INTERNATIONAL_PENALTY_COUNTRY = 0.2  # 不同国家的惩罚
    INTERNATIONAL_PENALTY_LANGUAGE = 0.15  # 不同语言的惩罚
    INTERNATIONAL_PENALTY_MAX = 0.4  # 最大惩罚值
    
    # 社群参数
    COMMUNITY_SAME_BONUS = 1.2  # 同社群传播增益
    COMMUNITY_CROSS_PENALTY = 0.85  # 跨社群传播惩罚
    
    # 疲劳和注意力参数
    FATIGUE_MULTIPLIER = 0.7  # 疲劳对传播的影响
    ATTENTION_CAPACITY_BASE = 3  # 基础注意力容量
    ATTENTION_FACTOR_MULTIPLIER = 0.4  # 注意力对传播的影响
    
    # 记忆参数
    MEMORY_BIAS_PER_ENTRY = 0.02  # 每条记忆增加的偏差
    MEMORY_BIAS_MAX = 0.2  # 最大记忆偏差
    
    # 竞争参数
    COMPETITION_PENALTY_MULTIPLIER = 0.02  # 每条活跃记忆的竞争惩罚
    COMPETITION_PENALTY_MIN = 0.5  # 最小竞争惩罚值
    
    # 语义质量参数
    SEMANTIC_QUALITY_MIN = 0.8  # 最小传播倍数
    SEMANTIC_QUALITY_MAX = 1.2  # 最大传播倍数
    
    # 争议性参数
    CONTROVERSY_MIN = 0.9  # 最小传播倍数
    CONTROVERSY_MAX = 1.2  # 最大传播倍数
    
    # 推荐引擎参数
    RECOMMENDATION_RELATIONSHIP_STRENGTH = 0.3  # 推荐的关系强度
    RECOMMENDATION_PLATFORM_WEIGHT = 0.6  # 推荐的平台权重
    RECOMMENDATION_TIMEZONE_FACTOR = 0.9  # 推荐的时区因子
    RECOMMENDATION_TOP_K = 4  # 推荐数量
    
    # LLM参数
    LLM_TEMPERATURE = 0.7  # 生成文本的温度
    LLM_COMMENT_TEMPERATURE = 0.6  # 评论文本的温度
    LLM_MAX_TOKENS = 100  # 最大生成token数
    LLM_COMMENT_MAX_TOKENS = 120  # 评论最大token数
    LLM_CACHE_SIZE = 1000  # 缓存大小
    
    # 性能参数
    BATCH_MODE = False  # 是否使用批量模式（大规模仿真）
    ASYNC_LLM = False  # 是否异步调用LLM
    LLM_BATCH_SIZE = 10  # LLM批量处理大小
    
    # 随机种子
    RANDOM_SEED = None  # None表示每次随机，否则固定
    
    # 实验模式
    EXPERIMENT_MODE = "hybrid"  # "hybrid" (规则+LLM) / "rule_only" (纯规则) / "llm_only" (仅LLM)
    
    @classmethod
    def set_seed(cls, seed: Optional[int] = None):
        """设置随机种子以保证可复现性"""
        cls.RANDOM_SEED = seed
        if seed is not None:
            random.seed(seed)
            import numpy as np
            np.random.seed(seed)
    
    @classmethod
    def update_from_dict(cls, config_dict: Dict):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
    
    @classmethod
    def to_dict(cls) -> Dict:
        """导出配置为字典"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and key.isupper()
        }
    
    @classmethod
    def load_from_file(cls, config_file: str):
        """从配置文件加载（JSON格式）"""
        import json
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                cls.update_from_dict(config)
    
    @classmethod
    def save_to_file(cls, config_file: str):
        """保存配置到文件"""
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(cls.to_dict(), f, indent=2, ensure_ascii=False)


class ExperimentConfig:
    """实验对照配置"""
    
    @staticmethod
    def get_rule_only_config() -> SimulationConfig:
        """获取纯规则模式配置"""
        SimulationConfig.EXPERIMENT_MODE = "rule_only"
        return SimulationConfig
    
    @staticmethod
    def get_hybrid_config() -> SimulationConfig:
        """获取混合模式配置（推荐）"""
        SimulationConfig.EXPERIMENT_MODE = "hybrid"
        return SimulationConfig
    
    @staticmethod
    def get_llm_only_config() -> SimulationConfig:
        """获取LLM模式配置（仅用于对比）"""
        SimulationConfig.EXPERIMENT_MODE = "llm_only"
        return SimulationConfig
    
    @staticmethod
    def create_ab_test_configs():
        """创建A/B测试配置"""
        config_a = SimulationConfig.to_dict()
        config_a["experiment_name"] = "rule_only"
        config_a["EXPERIMENT_MODE"] = "rule_only"
        
        config_b = SimulationConfig.to_dict()
        config_b["experiment_name"] = "hybrid"
        config_b["EXPERIMENT_MODE"] = "hybrid"
        
        return config_a, config_b
