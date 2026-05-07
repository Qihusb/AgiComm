"""
改进的指标计算
支持新的仿真指标：Message传播、情感演化、立场极化等
"""
import numpy as np
from collections import Counter
from typing import Dict, List, Optional


def calculate_metrics(
    history: List[int],
    agents: List,
    active_nodes: set,
    detailed_metrics: Optional[Dict] = None
) -> Dict:
    """
    计算仿真指标（升级版）
    """
    final_size = len(active_nodes)
    total_agents = len(agents)
    coverage_rate = final_size / total_agents if total_agents > 0 else 0

    steps_to_reach = len(history)
    if len(history) > 1:
        growth_rates = [
            (history[i] - history[i-1]) / history[i-1] if history[i-1] > 0 else 0
            for i in range(1, len(history))
        ]
        avg_growth_rate = np.mean(growth_rates)
        max_growth_rate = max(growth_rates) if growth_rates else 0
    else:
        avg_growth_rate = 0
        max_growth_rate = 0

    propagation_depth = len(history) if history else 0

    active_agents = [a for a in agents if a.id in active_nodes]
    inactive_agents = [a for a in agents if a.id not in active_nodes]

    if active_agents:
        active_emotions = [a.emotion for a in active_agents]
        active_emotion_mean = np.mean(active_emotions)
        active_emotion_std = np.std(active_emotions)
        active_emotion_max = max(active_emotions)
        active_emotion_min = min(active_emotions)
    else:
        active_emotion_mean = active_emotion_std = active_emotion_max = active_emotion_min = 0

    if inactive_agents:
        inactive_emotions = [a.emotion for a in inactive_agents]
        inactive_emotion_mean = np.mean(inactive_emotions)
        inactive_emotion_std = np.std(inactive_emotions)
    else:
        inactive_emotion_mean = inactive_emotion_std = 0

    if active_agents:
        active_stances = [a.stance for a in active_agents]
        active_stance_mean = np.mean(active_stances)
        active_stance_var = np.var(active_stances)
        active_stance_std = np.std(active_stances)
    else:
        active_stance_mean = active_stance_var = active_stance_std = 0

    if inactive_agents:
        inactive_stances = [a.stance for a in inactive_agents]
        inactive_stance_mean = np.mean(inactive_stances)
        inactive_stance_var = np.var(inactive_stances)
    else:
        inactive_stance_mean = inactive_stance_var = 0

    all_stances = [a.stance for a in agents]
    overall_stance_var = np.var(all_stances) if all_stances else 0
    polarization_index = active_stance_var - inactive_stance_var if (active_stance_var + inactive_stance_var) > 0 else 0
    if active_agents and all_stances:
        avg_stance = np.mean(all_stances)
        stance_divergence = np.mean([abs(a.stance - avg_stance) for a in active_agents])
    else:
        stance_divergence = 0

    if active_agents:
        avg_influence_active = np.mean([a.influence for a in active_agents])
        avg_activeness_active = np.mean([a.activeness for a in active_agents])
    else:
        avg_influence_active = avg_activeness_active = 0

    if active_agents:
        emotion_change = [
            abs(a.emotion - a.initial_emotion)
            for a in active_agents
            if hasattr(a, "initial_emotion")
        ]
        avg_emotion_change = np.mean(emotion_change) if emotion_change else 0

        stance_change = [
            abs(a.stance - a.initial_stance)
            for a in active_agents
            if hasattr(a, "initial_stance")
        ]
        avg_stance_change = np.mean(stance_change) if stance_change else 0
    else:
        avg_emotion_change = avg_stance_change = 0

    community_counts = Counter([a.community_id for a in active_agents])
    country_counts = Counter([a.country for a in active_agents])
    language_counts = Counter([a.language for a in active_agents])

    narrative_diversity = 0
    if detailed_metrics and "total_messages" in detailed_metrics:
        narrative_diversity = detailed_metrics.get("total_messages", 0)

    metrics = {
        "final_size": final_size,
        "coverage_rate": coverage_rate,
        "steps": steps_to_reach,
        "avg_growth_rate": avg_growth_rate,
        "max_growth_rate": max_growth_rate,
        "propagation_depth": propagation_depth,

        "active_emotion_mean": active_emotion_mean,
        "active_emotion_std": active_emotion_std,
        "active_emotion_max": active_emotion_max,
        "active_emotion_min": active_emotion_min,

        "inactive_emotion_mean": inactive_emotion_mean,
        "inactive_emotion_std": inactive_emotion_std,

        "active_stance_mean": active_stance_mean,
        "active_stance_var": active_stance_var,
        "active_stance_std": active_stance_std,

        "inactive_stance_mean": inactive_stance_mean,
        "inactive_stance_var": inactive_stance_var,

        "polarization_index": polarization_index,
        "overall_stance_var": overall_stance_var,
        "stance_divergence": stance_divergence,

        "avg_influence_active": avg_influence_active,
        "avg_activeness_active": avg_activeness_active,

        "avg_emotion_change": avg_emotion_change,
        "avg_stance_change": avg_stance_change,

        "active_community_diversity": len(community_counts),
        "active_country_diversity": len(country_counts),
        "active_language_diversity": len(language_counts),
        "narrative_diversity": narrative_diversity,
        **(detailed_metrics or {})
    }

    return metrics


def calculate_trajectory_metrics(
    agent_state_history: Dict,
    initial_states: Dict
) -> Dict:
    """
    计算Agent的轨迹指标（状态演化轨迹）
    """
    trajectory_metrics = {}

    for agent_id, states in agent_state_history.items():
        if not states:
            continue

        initial_emotion = initial_states.get(agent_id, {}).get("emotion", 0.5)
        initial_stance = initial_states.get(agent_id, {}).get("stance", 0.0)

        emotions = [s.get("emotion", initial_emotion) for s in states]
        stances = [s.get("stance", initial_stance) for s in states]

        trajectory_metrics[agent_id] = {
            "emotion_trajectory": emotions,
            "stance_trajectory": stances,
            "emotion_change": emotions[-1] - emotions[0] if emotions else 0,
            "stance_change": stances[-1] - stances[0] if stances else 0,
            "max_emotion": max(emotions) if emotions else initial_emotion,
            "min_emotion": min(emotions) if emotions else initial_emotion,
            "emotion_volatility": np.std(emotions) if len(emotions) > 1 else 0
        }

    return trajectory_metrics
