"""
改进的实验控制器
支持新的语义+概率仿真，可复现的参数化实验
"""
import random
from typing import Dict, List, Optional
from .data_loader import load_agents_from_csv
from .network_builder import build_network
from .simulator import Simulator
from .metrics import calculate_metrics
from .visualization import plot_results
from .event_generator import EventGenerator
from .message import Message


class ExperimentController:
    """
    实验控制器 - 参数驱动的仿真实验
    
    配置参数示例：
    {
        "data_path": "...",
        "max_steps": 10,
        "num_seeds": 5,
        "seed_strategy": "influence",
        "enable_semantic": True,
        "enable_llm": False,
        "user_filter": {
            "emotion_threshold": 0.5,
            "stance_range": [0.2, 0.8],
            "influence_threshold": 100
        },
        "initial_event": {
            "type": "social_hotspot",
            "custom_content": "...",
            "custom_emotion": 0.7,
            "custom_stance": 0.5
        }
    }
    """
    
    def __init__(self, config: Dict):
        """
        初始化实验控制器
        
        Args:
            config: 实验配置字典
        """
        self.config = config
        self.agents = None
        self.G = None
        self.simulator = None
        self.event_generator = EventGenerator()
    
    def setup_experiment(self):
        """设置实验：加载数据，构建网络，初始化仿真器"""
        
        # 1. 加载数据
        print(f"[ExperimentController] 加载数据: {self.config['data_path']}")
        self.agents = load_agents_from_csv(self.config['data_path'])
        print(f"[ExperimentController] 加载了 {len(self.agents)} 个Agent")
        
        # 2. 用户筛选
        if self.config.get('user_filter'):
            original_count = len(self.agents)
            self.agents = self._filter_agents(self.agents, self.config['user_filter'])
            print(f"[ExperimentController] 筛选后: {len(self.agents)} 个Agent（从 {original_count}）")
        
        # 3. 构建网络
        print("[ExperimentController] 构建社交网络...")
        self.G = build_network(self.agents)
        print(f"[ExperimentController] 网络节点: {self.G.number_of_nodes()}, 边: {self.G.number_of_edges()}")
        
        # 4. 初始化仿真器
        enable_llm = self.config.get('enable_llm', False)
        self.simulator = Simulator(enable_llm=enable_llm)
        print(f"[ExperimentController] 仿真器已初始化 (LLM: {enable_llm})")
    
    def _filter_agents(self, agents: List, filter_config: Dict) -> List:
        """
        根据配置筛选用户
        
        Args:
            agents: 原始Agent列表
            filter_config: 筛选配置
            
        Returns:
            筛选后的Agent列表
        """
        filtered = agents
        
        if 'emotion_threshold' in filter_config:
            threshold = filter_config['emotion_threshold']
            filtered = [a for a in filtered if a.emotion >= threshold]
        
        if 'stance_range' in filter_config:
            min_s, max_s = filter_config['stance_range']
            filtered = [a for a in filtered if min_s <= a.stance <= max_s]
        
        if 'influence_threshold' in filter_config:
            threshold = filter_config['influence_threshold']
            filtered = [a for a in filtered if a.influence >= threshold]
        
        if 'activeness_threshold' in filter_config:
            threshold = filter_config['activeness_threshold']
            filtered = [a for a in filtered if a.activeness >= threshold]
        
        return filtered
    
    def select_seeds(self, seed_ids: Optional[List[str]] = None) -> List[str]:
        """
        选择种子节点
        
        Args:
            seed_ids: 指定的种子节点ID（如果为None则使用config中的策略）
            
        Returns:
            种子节点ID列表
        """
        if seed_ids:
            # 使用指定的种子
            return seed_ids
        
        strategy = self.config.get('seed_strategy', 'influence')
        num_seeds = self.config.get('num_seeds', 5)
        
        print(f"[ExperimentController] 使用种子策略: {strategy}, 数量: {num_seeds}")
        
        if strategy == 'random':
            seeds = random.sample(self.agents, min(num_seeds, len(self.agents)))
        
        elif strategy == 'influence':
            sorted_agents = sorted(self.agents, key=lambda x: x.influence, reverse=True)
            seeds = sorted_agents[:min(num_seeds, len(sorted_agents))]
        
        elif strategy == 'emotion':
            sorted_agents = sorted(self.agents, key=lambda x: x.emotion, reverse=True)
            seeds = sorted_agents[:min(num_seeds, len(sorted_agents))]
        
        elif strategy == 'activeness':
            sorted_agents = sorted(self.agents, key=lambda x: x.activeness, reverse=True)
            seeds = sorted_agents[:min(num_seeds, len(sorted_agents))]
        
        else:
            seeds = random.sample(self.agents, min(num_seeds, len(self.agents)))
        
        seed_ids = [s.id for s in seeds]
        print(f"[ExperimentController] 选定种子: {seed_ids}")
        
        return seed_ids
    
    def _generate_initial_event(self) -> Message:
        """
        生成初始事件
        
        Returns:
            Message对象
        """
        event_config = self.config.get('initial_event', {})
        
        event_type = event_config.get('type', 'social_hotspot')
        custom_content = event_config.get('custom_content')
        custom_emotion = event_config.get('custom_emotion')
        custom_stance = event_config.get('custom_stance')
        
        return self.event_generator.generate_event(
            event_type=event_type,
            custom_content=custom_content,
            custom_emotion=custom_emotion,
            custom_stance=custom_stance,
            source_id='event_source'
        )
    
    def run_experiment(self, seed_ids: Optional[List[str]] = None) -> Dict:
        """
        运行一次实验
        
        Args:
            seed_ids: 指定的种子节点（可选）
            
        Returns:
            实验结果字典
        """
        print("\n" + "="*80)
        print("🧪 开始运行实验")
        print("="*80)
        
        # 选择种子
        seed_ids = self.select_seeds(seed_ids)
        
        # 生成初始事件
        initial_event = self._generate_initial_event()
        print(f"[ExperimentController] 初始事件: {initial_event.content[:50]}...")
        print(f"[ExperimentController] 事件情感: {initial_event.emotion:.2f}, 立场: {initial_event.stance:.2f}")
        
        # 运行仿真
        print(f"[ExperimentController] 开始仿真 (最多 {self.config.get('max_steps', 10)} 步)...")
        
        history, active_nodes, detailed_metrics = self.simulator.run_simulation(
            self.G,
            seed_ids,
            initial_message=initial_event,
            max_steps=self.config.get('max_steps', 10)
        )
        
        print(f"[ExperimentController] 仿真完成: {len(active_nodes)} 个节点被激活 (共 {len(self.agents)} 个)")
        
        # 计算指标
        metrics = calculate_metrics(history, self.agents, active_nodes, detailed_metrics)
        
        # 可视化（可选）
        if self.config.get('visualize', False):
            experiment_name = self.config.get('experiment_name', 'experiment')
            plot_results(history, metrics, experiment_name)
        
        print("="*80)
        print("✅ 实验完成\n")
        
        return {
            'history': history,
            'active_nodes': active_nodes,
            'metrics': metrics,
            'seeds': seed_ids,
            'initial_event': initial_event.to_dict(),
            'config': self.config
        }


def run_multiple_experiments(configs: List[Dict]) -> List[Dict]:
    """
    运行多个对比实验
    
    Args:
        configs: 实验配置列表
        
    Returns:
        结果列表
    """
    results = []
    
    for i, config in enumerate(configs, 1):
        print(f"\n{'#'*80}")
        print(f"# 实验 {i}/{len(configs)}: {config.get('name', 'Unnamed')}")
        print(f"{'#'*80}\n")
        
        controller = ExperimentController(config)
        controller.setup_experiment()
        result = controller.run_experiment()
        results.append(result)
    
    return results
