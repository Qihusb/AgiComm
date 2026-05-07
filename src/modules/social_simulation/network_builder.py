import random
from typing import Iterable
import networkx as nx


def _choose_country_communities(agents):
    countries = [getattr(agent, "country", None) for agent in agents if getattr(agent, "country", None)]
    unique = list(dict.fromkeys(countries))
    if unique:
        return unique
    return [f"community_{i}" for i in range(4)]


def build_network(agents, community_capacity: int = 4):
    """构建社区化社交网络。"""
    G = nx.DiGraph()
    communities = _choose_country_communities(agents)

    for index, agent in enumerate(agents):
        if not getattr(agent, "community_id", None):
            if getattr(agent, "country", None):
                agent.community_id = agent.country
            else:
                agent.community_id = communities[index % len(communities)]
        if not getattr(agent, "community_size", None):
            agent.community_size = 0
        if not getattr(agent, "relationship_strength", None):
            agent.relationship_strength = random.uniform(0.2, 0.7)
        G.add_node(agent.id, obj=agent)

    for agent in agents:
        same_community = [a for a in agents if a.community_id == agent.community_id and a.id != agent.id]
        cross_community = [a for a in agents if a.community_id != agent.community_id]

        same_count = min(len(same_community), max(1, int(agent.followers / 120)))
        cross_count = min(len(cross_community), max(0, int(agent.followers / 300)))

        for target in random.sample(same_community, same_count):
            strength = random.uniform(0.5, 1.0)
            G.add_edge(agent.id, target.id, weight=strength, relation="strong")

        for target in random.sample(cross_community, cross_count):
            if random.random() < 0.35:
                strength = random.uniform(0.1, 0.45)
                G.add_edge(agent.id, target.id, weight=strength, relation="weak")

    community_roots = {}
    for agent in sorted(agents, key=lambda a: getattr(a, "influence", 0), reverse=True):
        if agent.community_id not in community_roots:
            community_roots[agent.community_id] = agent

    for community_id, bridge_candidate in community_roots.items():
        other_communities = [c for c in communities if c != community_id]
        for target_community in other_communities:
            peer_candidates = [a for a in agents if a.community_id == target_community]
            if not peer_candidates:
                continue
            partner = random.choice(peer_candidates)
            if bridge_candidate.id != partner.id:
                G.add_edge(bridge_candidate.id, partner.id, weight=0.4, relation="bridge")
                G.add_edge(partner.id, bridge_candidate.id, weight=0.35, relation="bridge")

    for agent in agents:
        agent.community_size = len([a for a in agents if a.community_id == agent.community_id])

    return G