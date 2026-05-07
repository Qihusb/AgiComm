import random
from .data_loader import load_agents_from_csv
from .network_builder import build_network
from .simulator import run_simulation
from .metrics import calculate_metrics
from .visualization import plot_results

class ExperimentController:
    """
    实验控制（Experiment Controller）
    核心逻辑：
    用“配置参数”驱动仿真，而不是写死流程
    例如：
    seed选择策略（随机 / 高影响力）
    用户筛选（高情绪 / 特定立场）
    仿真轮数
    本质：把一次仿真 → 变成可重复对比的实验
    """

    def __init__(self, config):
        self.config = config
        self.agents = None
        self.G = None

    def setup_experiment(self):
        """设置实验：加载数据，构建网络"""
        # 加载数据
        self.agents = load_agents_from_csv(self.config['data_path'])

        # 用户筛选
        if self.config.get('user_filter'):
            self.agents = self._filter_agents(self.agents, self.config['user_filter'])

        # 构建网络
        self.G = build_network(self.agents)

    def _filter_agents(self, agents, filter_config):
        """根据配置筛选用户"""
        filtered = agents

        if 'emotion_threshold' in filter_config:
            filtered = [a for a in filtered if a.emotion >= filter_config['emotion_threshold']]

        if 'stance_range' in filter_config:
            min_s, max_s = filter_config['stance_range']
            filtered = [a for a in filtered if min_s <= a.stance <= max_s]

        if 'influence_threshold' in filter_config:
            filtered = [a for a in filtered if a.influence >= filter_config['influence_threshold']]

        return filtered

    def select_seeds(self):
        """根据策略选择种子节点"""
        strategy = self.config.get('seed_strategy', 'influence')

        if strategy == 'random':
            seeds = random.sample(self.agents, self.config.get('num_seeds', 5))
        elif strategy == 'influence':
            sorted_agents = sorted(self.agents, key=lambda x: x.influence, reverse=True)
            seeds = sorted_agents[:self.config.get('num_seeds', 5)]
        elif strategy == 'emotion':
            sorted_agents = sorted(self.agents, key=lambda x: x.emotion, reverse=True)
            seeds = sorted_agents[:self.config.get('num_seeds', 5)]
        else:
            seeds = random.sample(self.agents, self.config.get('num_seeds', 5))

        return [s.id for s in seeds]

    def run_experiment(self):
        """运行实验"""
        seed_ids = self.select_seeds()

        # 运行仿真
        history, active_nodes = run_simulation(
            self.G,
            seed_ids,
            max_steps=self.config.get('max_steps', 10)
        )

        # 计算指标
        metrics = calculate_metrics(history, self.agents, active_nodes)

        # 可视化
        if self.config.get('visualize', False):
            plot_results(history, metrics, self.config.get('experiment_name', 'experiment'))

        return {
            'history': history,
            'active_nodes': active_nodes,
            'metrics': metrics,
            'seeds': seed_ids
        }

def run_multiple_experiments(configs):
    """运行多个实验进行对比"""
    results = []

    for config in configs:
        controller = ExperimentController(config)
        controller.setup_experiment()
        result = controller.run_experiment()
        results.append(result)

    return results