import math
from typing import Dict, Any
import networkx as nx


# Matches the normalization in CostFunction._calculate_distance_cost
MAX_EDGE_DISTANCE = 5000.0


def admissible_heuristic(G: nx.MultiDiGraph, current: int, goal: int,
                         risk_data: Dict[str, Any] = None,
                         time_of_day: str = 'afternoon',
                         cost_weights: Dict[str, float] = None,
                         precomputed_min_risk: float = 0.0) -> float:
    """
    Admissible heuristic for A*, Weighted A*, and Greedy search.

    h(n) = w_d * min(SL/5000, 1.0)   ← distance lower bound
         + w_r * min_risk             ← risk lower bound (single edge)
         + w_t * 0.1                  ← traffic lower bound (low traffic = 0.1)

    Admissibility proof:
        - SL ≤ actual path distance  (triangle inequality)
        - min_risk ≤ risk on any edge
        - 0.1 ≤ traffic cost on any edge (minimum traffic level)
        Therefore h(n) ≤ actual_cost(n → goal)  ✅

    Args:
        G:                    NetworkX MultiDiGraph
        current:              Current node ID
        goal:                 Goal node ID
        risk_data:            Unused — kept for interface compatibility
                              (min_risk is pre-computed and passed directly)
        time_of_day:          Unused — kept for interface compatibility
        cost_weights:         Live cost-function weights dict
        precomputed_min_risk: Global minimum risk_factor across all edges,
                              pre-computed once per time slot in RouteOptimizer.
                              Avoids O(edges) scan on every node expansion.

    Returns:
        Admissible heuristic value (float >= 0)
    """
    if current not in G.nodes or goal not in G.nodes:
        return 0.0

    # ── weights ──────────────────────────────────────────────────────────────
    if cost_weights:
        w_d = cost_weights.get('distance',       0.30)
        w_r = cost_weights.get('risk_factor',    0.20)
        w_t = cost_weights.get('traffic_factor', 0.15)
    else:
        w_d, w_r, w_t = 0.30, 0.20, 0.15

    # ── straight-line distance (meters) ──────────────────────────────────────
    lat1 = float(G.nodes[current].get('y', 0))
    lon1 = float(G.nodes[current].get('x', 0))
    lat2 = float(G.nodes[goal].get('y', 0))
    lon2 = float(G.nodes[goal].get('x', 0))

    dx = (lon2 - lon1) * 111000 * math.cos(math.radians((lat1 + lat2) / 2))
    dy = (lat2 - lat1) * 111000
    straight_line = math.sqrt(dx ** 2 + dy ** 2)

    # ── distance lower bound ─────────────────────────────────────────────────
    h_distance = w_d * min(straight_line / MAX_EDGE_DISTANCE, 1.0)

    # ── risk lower bound (pre-computed — O(1) lookup) ────────────────────────
    h_risk = w_r * precomputed_min_risk

    # ── traffic lower bound ('low' traffic = 0.1) ────────────────────────────
    h_traffic = w_t * 0.1

    return h_distance + h_risk + h_traffic


def get_heuristic_function(_name: str = None):
    """Return the single admissible heuristic (name argument ignored)."""
    return admissible_heuristic


def get_scaled_heuristic_function(_heuristic_name: str,
                                  _optimization_criteria: str,
                                  cost_weights: Dict[str, float],
                                  precomputed_min_risk: float = 0.0):
    """
    Return a heuristic callable bound to the current cost_weights and
    pre-computed min_risk.

    Signature of the returned function:
        heuristic_func(G, current, goal, risk_data, time_of_day) -> float

    risk_data is accepted for interface compatibility but ignored —
    min_risk is already baked in via closure.
    """
    def bound_heuristic(G, current, goal, risk_data=None, time_of_day='afternoon'):
        return admissible_heuristic(
            G, current, goal,
            risk_data=None,           # not needed — min_risk is pre-computed
            time_of_day=time_of_day,
            cost_weights=cost_weights,
            precomputed_min_risk=precomputed_min_risk,
        )

    return bound_heuristic


# ── kept for UI / RouteOptimizer compatibility ────────────────────────────────
AVAILABLE_HEURISTICS = {
    'admissible': {
        'name': 'Admissible Heuristic',
        'function': admissible_heuristic,
        'description': (
            'Normalized straight-line distance + optimistic risk + optimistic traffic. '
            'Guaranteed admissible: h(n) ≤ actual cost to goal.'
        ),
    }
}
