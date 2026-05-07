"""
社会传播仿真 - 后端API集成（稳定修复版）
"""

from typing import List, Optional, Dict, Tuple
from pydantic import BaseModel
import random

from src.modules.social_simulation import (
    ExperimentController,
    EventGenerator,
    load_agents_from_csv,
    build_network,
    Simulator,
    calculate_metrics
)

# ===================== 请求模型 =====================

class SimulationRequest(BaseModel):
    """社会传播仿真请求（统一版本）"""

    # 基础参数
    event_text: str
    event_emotion: Optional[float] = 0.6
    event_stance: Optional[float] = 0.5

    # 用户筛选
    emotion_threshold: Optional[float] = None
    stance_range: Optional[List[float]] = None   # JSON 兼容 list
    influence_threshold: Optional[float] = None

    # 种子配置
    num_seeds: int = 5
    seed_strategy: str = "influence"  # influence | emotion | random

    # 仿真参数
    max_steps: int = 10
    enable_llm: bool = False

    # 其他
    experiment_name: str = "social_propagation"


class SimulationResponse(BaseModel):
    """仿真响应"""
    status: str
    data: Optional[Dict] = None
    error: Optional[Dict] = None
    meta: Optional[Dict] = None


# ===================== 核心运行函数 =====================

def run_social_simulation(request: SimulationRequest, data_path: str) -> SimulationResponse:
    """
    社会传播仿真主函数（稳定增强版）
    """

    try:
        # 1. 加载数据
        agents = load_agents_from_csv(data_path)

        if not agents:
            return SimulationResponse(
                status="error",
                error={"message": "无可用用户数据", "code": "EMPTY_AGENTS"}
            )

        # 2. 筛选用户（安全版）
        filtered_agents = agents

        # 情感过滤
        if request.emotion_threshold is not None:
            filtered_agents = [
                a for a in filtered_agents
                if getattr(a, "emotion", 0) >= request.emotion_threshold
            ]

        # 立场过滤（list -> tuple 安全转换）
        if request.stance_range:
            try:
                min_s, max_s = request.stance_range
                filtered_agents = [
                    a for a in filtered_agents
                    if min_s <= getattr(a, "stance", 0) <= max_s
                ]
            except Exception:
                pass

        # 影响力过滤
        if request.influence_threshold is not None:
            filtered_agents = [
                a for a in filtered_agents
                if getattr(a, "influence", 0) >= request.influence_threshold
            ]

        if not filtered_agents:
            return SimulationResponse(
                status="error",
                error={"message": "筛选后无有效用户", "code": "NO_VALID_AGENTS"}
            )

        # 3. 构建网络
        G = build_network(filtered_agents)

        # 4. 初始化仿真器
        simulator = Simulator(enable_llm=request.enable_llm)

        # 5. 生成事件
        event_generator = EventGenerator()
        initial_event = event_generator.generate_custom_event(
            content=request.event_text,
            emotion=request.event_emotion,
            stance=request.event_stance,
            source_id="media_source"
        )

        # 6. 选择种子（安全版）
        import random

        k = min(request.num_seeds, len(filtered_agents))

        if request.seed_strategy == "influence":
            sorted_agents = sorted(
                filtered_agents,
                key=lambda x: getattr(x, "influence", 0),
                reverse=True
            )
            seeds = sorted_agents[:k]

        elif request.seed_strategy == "emotion":
            sorted_agents = sorted(
                filtered_agents,
                key=lambda x: getattr(x, "emotion", 0),
                reverse=True
            )
            seeds = sorted_agents[:k]

        else:
            seeds = random.sample(filtered_agents, k)

        seed_ids = [s.id for s in seeds]

        # 7. 运行仿真
        history, active_nodes, detailed_metrics = simulator.run_simulation(
            G,
            seed_ids,
            initial_message=initial_event,
            max_steps=request.max_steps
        )

        # 8. 提取决策轨迹
        decision_trace = detailed_metrics.pop("decision_trace", [])

        # 9. 指标计算
        metrics = calculate_metrics(
            history,
            filtered_agents,
            active_nodes,
            detailed_metrics
        )

        # 10. 返回结构
        result_data = {
            "simulation_id": request.experiment_name,
            "event": {
                "text": request.event_text,
                "emotion": request.event_emotion,
                "stance": request.event_stance
            },
            "parameters": {
                "total_agents": len(filtered_agents),
                "num_seeds": len(seeds),
                "max_steps": request.max_steps,
                "enable_llm": request.enable_llm
            },
            "results": {
                "history": history,
                "active_nodes_count": len(active_nodes),
                "metrics": metrics,
                "seeds": seed_ids,
                "decision_trace": decision_trace
            }
        }

        return SimulationResponse(
            status="success",
            data=result_data,
            meta={
                "total_agents": len(filtered_agents),
                "active_nodes": len(active_nodes),
                "coverage_rate": metrics.get("coverage_rate", 0)
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()

        return SimulationResponse(
            status="error",
            error={
                "code": "SIMULATION_ERROR",
                "message": f"仿真执行失败: {str(e)}",
                "reason": type(e).__name__
            }
        )


# ===================== 模板接口 =====================

def get_simulation_templates() -> Dict:
    """获取预设仿真模板"""
    event_generator = EventGenerator()

    templates = {}
    for event_type in event_generator.list_event_types():
        templates[event_type] = event_generator.get_event_template_info(event_type)

    return templates


# ===================== 对比实验 =====================

def run_comparison_experiments(configs: List[Dict], data_path: str) -> Dict:
    """
    多实验对比
    """

    try:
        results = []

        for config in configs:
            config["data_path"] = data_path

            controller = ExperimentController(config)
            controller.setup_experiment()
            result = controller.run_experiment()

            results.append(result)

        return {
            "status": "success",
            "experiments_count": len(results),
            "results": results
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "status": "error",
            "error": {
                "message": f"对比实验失败: {str(e)}",
                "reason": type(e).__name__
            }
        }