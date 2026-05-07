"""
改进的仿真器
从原来的"节点激活"升级为"Message传播 + Agent状态动态演化"

集成语义增强：
- 规则驱动传播机制
- LLM语义增强生成
- 语义质量与争议性权重
"""
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from .message import Message
from .semantic_engine import SemanticEngine
from .sentiment_analyzer import SentimentAnalyzer
from .propagation_model import compute_propagation_prob
from .exposure_model import compute_exposure_prob
from .recommendation_engine import RecommendationEngine


class Simulator:
    """
    改进的传播仿真器
    支持Message传播和Agent动态状态变化
    """

    def __init__(self, enable_llm: bool = False):
        """
        初始化仿真器

        Args:
            enable_llm: 是否启用LLM（用于语义引擎和生成层）
        """
        self.semantic_engine = SemanticEngine(enable_llm=enable_llm)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.recommendation_engine = RecommendationEngine()
        self.enable_llm = enable_llm
        
        # 初始化LLM生成器
        self.llm_generator = None
        if enable_llm:
            try:
                from .llm_generator import LLMGenerator
                self.llm_generator = LLMGenerator(enable_llm=enable_llm)
            except ImportError:
                print("[Simulator] LLMGenerator not available, using rule templates only")

    def run_simulation(
        self,
        G,
        seed_ids: List[str],
        initial_message: Optional[Message] = None,
        max_steps: int = 10
    ) -> Tuple[List[int], set, Dict]:
        """
        运行改进的传播仿真

        Args:
            G: 网络图（networkx DiGraph）
            seed_ids: 种子节点ID列表
            initial_message: 初始Message对象
            max_steps: 最大步数

        Returns:
            (history, active_nodes, detailed_metrics)
        """
        active_nodes = set(seed_ids)
        history = [len(active_nodes)]

        if initial_message is None:
            from .event_generator import EventGenerator
            gen = EventGenerator()
            initial_message = gen.generate_event(
                event_type="social_hotspot",
                source_id="seed_0"
            )

        message_pool = {}
        message_queue = []

        # 如果初始消息源不在社交网络中，则用种子节点创建起始传播消息
        if initial_message.source_id not in G and seed_ids:
            for seed_id in seed_ids:
                if seed_id not in G.nodes:
                    continue
                seed_message = Message(
                    content=initial_message.content,
                    emotion=initial_message.emotion,
                    stance=initial_message.stance,
                    source_id=seed_id,
                    narrative_id=initial_message.narrative_id,
                    narrative_type=initial_message.narrative_type,
                    origin_country=initial_message.origin_country,
                    language=initial_message.language,
                    hotness=initial_message.hotness,
                    propagation_depth=0,
                    semantic_quality=initial_message.semantic_quality,
                    controversy_score=initial_message.controversy_score,
                    emotional_intensity=initial_message.emotional_intensity
                )
                message_pool[seed_message.id] = seed_message
                message_queue.append(seed_message)
        else:
            message_pool[initial_message.id] = initial_message
            message_queue = [initial_message]

        propagation_tree = {}
        agent_state_history = {}
        recommendation_exposures = 0
        decision_trace = []

        for step in range(max_steps):
            new_message_queue = []
            nodes_activated_this_step = set()
            step_state_updates = {}

            for current_message in message_queue:
                source_id = current_message.source_id
                neighbors = list(G.successors(source_id)) if source_id in G else []

                for neighbor_id in neighbors:
                    if neighbor_id not in G.nodes:
                        continue
                    neighbor = G.nodes[neighbor_id]["obj"]
                    if not neighbor.can_process_message():
                        neighbor.apply_overload()
                        continue

                    exposure_prob = compute_exposure_prob(
                        neighbor,
                        current_message,
                        context={
                            "relationship_strength": 0.6,
                            "hotness": current_message.hotness,
                            "platform_weight": 0.8,
                            "timezone_factor": 1.0
                        }
                    )
                    neighbor.record_exposure(current_message, exposure_prob, datetime.now())

                    if random.random() > exposure_prob:
                        continue

                    semantic_result = self.semantic_engine.process(neighbor, current_message, use_llm=self.enable_llm)
                    propagation_prob = compute_propagation_prob(neighbor, current_message, semantic_result)

                    # 调整传播决策：对于comment，降低随机阈值使其更容易传播
                    threshold = 0.5 if semantic_result["action"] == "comment" else 1.0
                    should_propagate = random.random() < (propagation_prob * threshold)

                    if semantic_result["action"] == "ignore" or not should_propagate:
                        neighbor.record_interaction(semantic_result["action"], current_message, propagation_prob)
                        decision_trace.append({
                            "step": step,
                            "agent_id": neighbor_id,
                            "source_agent_id": source_id,
                            "source_message_id": current_message.id,
                            "action": semantic_result["action"],
                            "generated_text": semantic_result["generated_text"],
                            "emotion_shift": semantic_result["emotion_shift"],
                            "stance_shift": semantic_result["stance_shift"],
                            "semantic_score": semantic_result["semantic_score"],
                            "exposure_prob": exposure_prob,
                            "propagation_prob": propagation_prob,
                            "use_llm": semantic_result.get("use_llm", False),
                            "llm_error": semantic_result.get("llm_error"),
                            "recommendation": False,
                            "message_depth": current_message.propagation_depth,
                            "hotness": current_message.hotness,
                            "outcome": "ignored"
                        })
                        continue

                    new_message = current_message.clone_with_modifications(
                        new_content=semantic_result["generated_text"],
                        new_emotion=max(0.0, min(1.0, current_message.emotion + semantic_result["emotion_shift"])),
                        new_stance=max(-1.0, min(1.0, current_message.stance + semantic_result["stance_shift"])),
                        source_agent_id=neighbor_id,
                        hotness=min(1.0, current_message.hotness + 0.05)
                    )
                    new_message.propagation_count = current_message.propagation_count + 1
                    
                    # 计算语义质量和争议性（用于后续传播）
                    if self.llm_generator:
                        new_message.semantic_quality = self.llm_generator.compute_semantic_quality(
                            semantic_result["generated_text"], neighbor, new_message
                        )
                        new_message.controversy_score = self.llm_generator.compute_controversy_score(
                            semantic_result["generated_text"], new_message
                        )
                    self.sentiment_analyzer.update_agent_state(
                        neighbor,
                        semantic_result["generated_text"],
                        semantic_result["emotion_shift"],
                        semantic_result["stance_shift"],
                        semantic_result["action"]
                    )
                    neighbor.update_state(influencer=G.nodes[source_id]["obj"] if source_id in G else None)
                    neighbor.record_interaction(semantic_result["action"], current_message, propagation_prob)
                    neighbor.add_memory({
                        "message_id": current_message.id,
                        "narrative_id": current_message.narrative_id,
                        "narrative_type": current_message.narrative_type,
                        "action": semantic_result["action"],
                        "timestamp": datetime.now().isoformat()
                    })

                    if neighbor_id not in active_nodes:
                        nodes_activated_this_step.add(neighbor_id)
                    propagation_tree.setdefault(new_message.id, []).append(neighbor_id)

                    if new_message.id not in message_pool:
                        message_pool[new_message.id] = new_message
                        new_message_queue.append(new_message)

                    decision_trace.append({
                        "step": step,
                        "agent_id": neighbor_id,
                        "source_agent_id": source_id,
                        "source_message_id": current_message.id,
                        "action": semantic_result["action"],
                        "generated_text": semantic_result["generated_text"],
                        "emotion_shift": semantic_result["emotion_shift"],
                        "stance_shift": semantic_result["stance_shift"],
                        "semantic_score": semantic_result["semantic_score"],
                        "exposure_prob": exposure_prob,
                        "propagation_prob": propagation_prob,
                        "use_llm": semantic_result.get("use_llm", False),
                        "llm_error": semantic_result.get("llm_error"),
                        "recommendation": False,
                        "message_depth": current_message.propagation_depth,
                        "hotness": current_message.hotness,
                        "outcome": "propagated"
                    })
                    step_state_updates.setdefault(neighbor_id, []).append({
                        "step": step,
                        "emotion": neighbor.emotion,
                        "stance": neighbor.stance,
                        "action": semantic_result["action"]
                    })

                recommended = self.recommendation_engine.recommend(
                    G,
                    current_message,
                    exclude_ids=neighbors + [source_id],
                    source="social",
                    top_k=4
                )

                for recommended_id, score in recommended:
                    if recommended_id not in G.nodes:
                        continue
                    recommended_agent = G.nodes[recommended_id]["obj"]
                    if not recommended_agent.can_process_message():
                        recommended_agent.apply_overload()
                        continue

                    exposure_prob = compute_exposure_prob(
                        recommended_agent,
                        current_message,
                        context={
                            "relationship_strength": 0.3,
                            "hotness": current_message.hotness,
                            "platform_weight": 0.6,
                            "timezone_factor": 0.9
                        }
                    )
                    recommended_agent.record_exposure(current_message, exposure_prob, datetime.now())
                    recommendation_exposures += 1

                    if random.random() > exposure_prob:
                        continue

                    semantic_result = self.semantic_engine.process(recommended_agent, current_message, use_llm=self.enable_llm)
                    propagation_prob = compute_propagation_prob(recommended_agent, current_message, semantic_result)

                    # 调整传播决策：对于comment，降低随机阈值使其更容易传播
                    threshold = 0.5 if semantic_result["action"] == "comment" else 1.0
                    should_propagate = random.random() < (propagation_prob * threshold)

                    if semantic_result["action"] == "ignore" or not should_propagate:
                        recommended_agent.record_interaction(semantic_result["action"], current_message, propagation_prob)
                        decision_trace.append({
                            "step": step,
                            "agent_id": recommended_id,
                            "source_agent_id": source_id,
                            "source_message_id": current_message.id,
                            "action": semantic_result["action"],
                            "generated_text": semantic_result["generated_text"],
                            "emotion_shift": semantic_result["emotion_shift"],
                            "stance_shift": semantic_result["stance_shift"],
                            "semantic_score": semantic_result["semantic_score"],
                            "exposure_prob": exposure_prob,
                            "propagation_prob": propagation_prob,
                            "use_llm": semantic_result.get("use_llm", False),
                            "llm_error": semantic_result.get("llm_error"),
                            "recommendation": True,
                            "message_depth": current_message.propagation_depth,
                            "hotness": current_message.hotness,
                            "outcome": "ignored"
                        })
                        continue

                    new_message = current_message.clone_with_modifications(
                        new_content=semantic_result["generated_text"],
                        new_emotion=max(0.0, min(1.0, current_message.emotion + semantic_result["emotion_shift"])),
                        new_stance=max(-1.0, min(1.0, current_message.stance + semantic_result["stance_shift"])),
                        source_agent_id=recommended_id,
                        hotness=min(1.0, current_message.hotness + 0.03)
                    )
                    new_message.propagation_count = current_message.propagation_count + 1
                    
                    # 计算语义质量和争议性（用于后续传播）
                    if self.llm_generator:
                        new_message.semantic_quality = self.llm_generator.compute_semantic_quality(
                            semantic_result["generated_text"], recommended_agent, new_message
                        )
                        new_message.controversy_score = self.llm_generator.compute_controversy_score(
                            semantic_result["generated_text"], new_message
                        )
                    self.sentiment_analyzer.update_agent_state(
                        recommended_agent,
                        semantic_result["generated_text"],
                        semantic_result["emotion_shift"],
                        semantic_result["stance_shift"],
                        semantic_result["action"]
                    )
                    recommended_agent.update_state(influencer=G.nodes[source_id]["obj"] if source_id in G else None)
                    recommended_agent.record_interaction(semantic_result["action"], current_message, propagation_prob)
                    recommended_agent.add_memory({
                        "message_id": current_message.id,
                        "narrative_id": current_message.narrative_id,
                        "narrative_type": current_message.narrative_type,
                        "action": semantic_result["action"],
                        "timestamp": datetime.now().isoformat()
                    })

                    if recommended_id not in active_nodes:
                        nodes_activated_this_step.add(recommended_id)
                    propagation_tree.setdefault(new_message.id, []).append(recommended_id)

                    if new_message.id not in message_pool:
                        message_pool[new_message.id] = new_message
                        new_message_queue.append(new_message)

                    decision_trace.append({
                        "step": step,
                        "agent_id": recommended_id,
                        "source_agent_id": source_id,
                        "source_message_id": current_message.id,
                        "action": semantic_result["action"],
                        "generated_text": semantic_result["generated_text"],
                        "emotion_shift": semantic_result["emotion_shift"],
                        "stance_shift": semantic_result["stance_shift"],
                        "semantic_score": semantic_result["semantic_score"],
                        "exposure_prob": exposure_prob,
                        "propagation_prob": propagation_prob,
                        "use_llm": semantic_result.get("use_llm", False),
                        "llm_error": semantic_result.get("llm_error"),
                        "recommendation": True,
                        "message_depth": current_message.propagation_depth,
                        "hotness": current_message.hotness,
                        "outcome": "propagated"
                    })
                    step_state_updates.setdefault(recommended_id, []).append({
                        "step": step,
                        "emotion": recommended_agent.emotion,
                        "stance": recommended_agent.stance,
                        "action": semantic_result["action"]
                    })

            for aid, updates in step_state_updates.items():
                agent_state_history.setdefault(aid, []).extend(updates)

            active_nodes.update(nodes_activated_this_step)
            history.append(len(active_nodes))
            message_queue = new_message_queue

            if not nodes_activated_this_step and not message_queue:
                break

        detailed_metrics = self._compute_detailed_metrics(
            G,
            active_nodes,
            agent_state_history,
            message_pool,
            recommendation_exposures
        )
        detailed_metrics["decision_trace"] = decision_trace

        return history, active_nodes, detailed_metrics

    def _compute_detailed_metrics(
        self,
        G,
        active_nodes: set,
        agent_state_history: Dict,
        message_pool: Dict,
        recommendation_exposures: int = 0
    ) -> Dict:
        active_agents = [G.nodes[nid]["obj"] for nid in active_nodes if nid in G.nodes]
        all_agents = [G.nodes[nid]["obj"] for nid in G.nodes()]

        import numpy as np

        metrics = {
            "total_messages": len(message_pool),
            "active_nodes_count": len(active_nodes),
            "coverage_rate": len(active_nodes) / len(all_agents) if all_agents else 0,
            "agents_with_state_changes": len(agent_state_history),
            "recommendation_exposures": recommendation_exposures
        }

        if active_agents:
            emotions = [a.emotion for a in active_agents]
            stances = [a.stance for a in active_agents]
            fatigue = [a.fatigue for a in active_agents]
            communities = [a.community_id for a in active_agents]

            metrics.update({
                "avg_emotion_active": np.mean(emotions),
                "std_emotion_active": np.std(emotions),
                "avg_stance_active": np.mean(stances),
                "std_stance_active": np.std(stances),
                "max_stance_active": max(stances),
                "min_stance_active": min(stances),
                "avg_fatigue_active": np.mean(fatigue),
                "community_diversity_active": len(set(communities))
            })

        if all_agents:
            all_emotions = [a.emotion for a in all_agents]
            all_stances = [a.stance for a in all_agents]
            all_communities = [a.community_id for a in all_agents]

            metrics.update({
                "avg_emotion_overall": np.mean(all_emotions),
                "std_emotion_overall": np.std(all_emotions),
                "avg_stance_overall": np.mean(all_stances),
                "std_stance_overall": np.std(all_stances),
                "community_diversity_overall": len(set(all_communities))
            })

        return metrics


def run_simulation(
    G,
    seed_ids: List[str],
    initial_message: Optional[Message] = None,
    max_steps: int = 10
) -> Tuple[List[int], set]:
    simulator = Simulator()
    history, active_nodes, _ = simulator.run_simulation(
        G, seed_ids, initial_message, max_steps
    )
    return history, active_nodes

