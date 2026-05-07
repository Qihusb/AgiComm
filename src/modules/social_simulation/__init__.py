"""
社会传播仿真模块
集成了规则驱动 + LLM语义增强的多智能体仿真系统

主要模块：
- message: Message类 - 文本传播对象
- agent: UserAgent类 - 扩展的智能体类
- event_generator: 初始事件生成
- semantic_engine: 规则决策 + LLM生成的统一语义引擎
- llm_generator: LLM语义生成层
- sentiment_analyzer: 情感分析和状态更新
- persona_builder: Agent特征描述
- propagation_model: 传播概率模型（纳入语义质量权重）
- network_builder: 社交网络构建
- simulator: 核心仿真器
- metrics: 指标计算
- experiment_controller: 实验控制器
- simulation_config: 仿真配置和实验管理
"""

from .message import Message
from .agent import UserAgent
from .event_generator import EventGenerator
from .semantic_engine import SemanticEngine, RuleDecisionLayer
from .llm_generator import LLMGenerator
from .sentiment_analyzer import SentimentAnalyzer
from .persona_builder import PersonaBuilder
from .propagation_model import sigmoid, stance_similarity, compute_propagation_prob, propagation_prob
from .network_builder import build_network
from .simulator import Simulator, run_simulation
from .metrics import calculate_metrics, calculate_trajectory_metrics
from .data_loader import load_agents_from_csv, clean_data
from .experiment_controller_v2 import ExperimentController, run_multiple_experiments
from .exposure_model import compute_exposure_prob
from .recommendation_engine import RecommendationEngine
from .simulation_config import SimulationConfig, ExperimentConfig

__all__ = [
    'Message',
    'UserAgent',
    'EventGenerator',
    'SemanticEngine',
    'RuleDecisionLayer',
    'LLMGenerator',
    'SentimentAnalyzer',
    'PersonaBuilder',
    'sigmoid',
    'stance_similarity',
    'compute_propagation_prob',
    'propagation_prob',
    'build_network',
    'Simulator',
    'run_simulation',
    'calculate_metrics',
    'calculate_trajectory_metrics',
    'load_agents_from_csv',
    'clean_data',
    'ExperimentController',
    'run_multiple_experiments',
    'compute_exposure_prob',
    'RecommendationEngine',
    'SimulationConfig',
    'ExperimentConfig',
]
