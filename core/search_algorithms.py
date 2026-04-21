import heapq
from collections import deque
from typing import List, Tuple, Dict, Any, Optional
import networkx as nx

class SearchAlgorithms:
    """Implementation of various search algorithms for pathfinding"""
    
    @staticmethod
    def breadth_first_search(G: nx.MultiDiGraph, start: int, goal: int,
                             cost_func=None, risk_data: Dict = None) -> Tuple[Optional[List], int]:
        """
        Breadth-First Search (BFS)
        
        Uninformed search that explores nodes level by level.
        Guarantees shortest path in terms of number of edges (unweighted).
        
        Args:
            G: NetworkX graph
            start: Start node ID
            goal: Goal node ID
            cost_func: Cost function (ignored for BFS)
            risk_data: Risk database (ignored for BFS)
            
        Returns:
            Tuple of (path, nodes_expanded)
        """
        visited = set([start])  # Mark start as visited immediately
        queue = deque([(start, [start])])
        nodes_expanded = 0
        
        while queue:
            current, path = queue.popleft()
            nodes_expanded += 1
            
            if current == goal:
                return path, nodes_expanded
            
            for neighbor in G.successors(current):
                if neighbor not in visited:
                    visited.add(neighbor)  # Mark visited when adding to queue
                    queue.append((neighbor, path + [neighbor]))
        
        return None, nodes_expanded
    
    @staticmethod
    def depth_first_search(G: nx.MultiDiGraph, start: int, goal: int,
                          cost_func=None, risk_data: Dict = None) -> Tuple[Optional[List], int]:
        """
        Depth-First Search (DFS)
        
        Uninformed search that explores nodes along a branch before backtracking.
        Does not guarantee shortest path but uses less memory.
        
        Args:
            G: NetworkX graph
            start: Start node ID
            goal: Goal node ID
            cost_func: Cost function (ignored for DFS)
            risk_data: Risk database (ignored for DFS)
            
        Returns:
            Tuple of (path, nodes_expanded)
        """
        visited = set([start])  # Mark start as visited immediately
        stack = [(start, [start])]
        nodes_expanded = 0
        
        while stack:
            current, path = stack.pop()
            nodes_expanded += 1
            
            if current == goal:
                return path, nodes_expanded
            
            for neighbor in G.successors(current):
                if neighbor not in visited:
                    visited.add(neighbor)  # Mark visited when adding to stack
                    stack.append((neighbor, path + [neighbor]))
        
        return None, nodes_expanded
    
    @staticmethod
    def uniform_cost_search(G: nx.MultiDiGraph, start: int, goal: int,
                           cost_func, risk_data: Dict) -> Tuple[Optional[List], int]:
        """
        Uniform Cost Search (UCS) — Dijkstra-style, optimal for non-negative costs.

        Heap entries: (cost, g_at_push, node).
        Stale-entry check: discard if g_at_push > best known g_score[node].
        Path reconstructed via came_from dict (same pattern as A*).
        """
        g_score   = {start: 0.0}
        came_from = {}
        pq = [(0.0, 0.0, start)]   # (f=g, g_at_push, node)
        nodes_expanded = 0

        while pq:
            _, g_pushed, current = heapq.heappop(pq)

            if g_pushed > g_score.get(current, float('inf')):
                continue

            nodes_expanded += 1

            if current == goal:
                path = []
                node = current
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start)
                path.reverse()
                return path, nodes_expanded

            for neighbor in G.successors(current):
                best_edge_cost = float('inf')
                best_key = None
                for key in G[current].get(neighbor, {}):
                    edge_attrs = risk_data.get(f"{current}_{neighbor}_{key}", {})
                    ec = cost_func.calculate_edge_cost(G, current, neighbor, key, edge_attrs)
                    if ec < best_edge_cost:
                        best_edge_cost = ec
                        best_key = key

                if best_key is None:
                    continue

                tentative_g = g_score[current] + best_edge_cost
                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor]   = tentative_g
                    came_from[neighbor] = current
                    heapq.heappush(pq, (tentative_g, tentative_g, neighbor))

        return None, nodes_expanded
    
    @staticmethod
    def iterative_deepening_search(G: nx.MultiDiGraph, start: int, goal: int,
                                   cost_func=None, risk_data: Dict = None,
                                   max_depth: int = 50) -> Tuple[Optional[List], int]:
        """
        Iterative Deepening Search (IDS)
        
        Combines depth-first space efficiency with breadth-first completeness.
        Re-explores nodes at different depths.
        
        Args:
            G: NetworkX graph
            start: Start node ID
            goal: Goal node ID
            cost_func: Cost function (ignored for IDS)
            risk_data: Risk database (ignored for IDS)
            max_depth: Maximum search depth
            
        Returns:
            Tuple of (path, nodes_expanded)
        """
        nodes_expanded = 0
        
        def depth_limited_search(current, goal, depth, visited_set, path):
            nonlocal nodes_expanded
            nodes_expanded += 1
            
            if current == goal:
                return path
            
            if depth == 0:
                return None
            
            if current in visited_set:
                return None
            
            visited_set.add(current)
            
            for neighbor in G.successors(current):
                result = depth_limited_search(neighbor, goal, depth - 1, 
                                            visited_set, path + [neighbor])
                if result:
                    return result
            
            # Remove from visited set when backtracking (memory efficiency)
            visited_set.remove(current)
            return None
        
        for depth in range(max_depth):
            result = depth_limited_search(start, goal, depth, set(), [start])
            if result:
                return result, nodes_expanded
        
        return None, nodes_expanded
    
    @staticmethod
    def greedy_best_first_search(G: nx.MultiDiGraph, start: int, goal: int,
                                heuristic_func, risk_data: Dict,
                                time_of_day: str = 'afternoon') -> Tuple[Optional[List], int]:
        """
        Greedy Best-First Search

        Expands the node with the lowest h(n). Not optimal, but fast.
        Heuristic values are cached per node to avoid recomputing
        coordinate math on every push.
        """
        h_cache = {}

        def h(node):
            if node not in h_cache:
                h_cache[node] = heuristic_func(G, node, goal, risk_data, time_of_day)
            return h_cache[node]

        visited = set()
        pq = [(h(start), start, [start])]
        nodes_expanded = 0

        while pq:
            _, current, path = heapq.heappop(pq)
            nodes_expanded += 1

            if current == goal:
                return path, nodes_expanded

            if current in visited:
                continue
            visited.add(current)

            for neighbor in G.successors(current):
                if neighbor not in visited:
                    heapq.heappush(pq, (h(neighbor), neighbor, path + [neighbor]))

        return None, nodes_expanded
    
    @staticmethod
    def a_star_search(G: nx.MultiDiGraph, start: int, goal: int,
                     cost_func, heuristic_func, risk_data: Dict,
                     time_of_day: str = 'afternoon') -> Tuple[Optional[List], int]:
        """
        A* Search — correct for admissible (not necessarily consistent) heuristics.

        Heap entries store (f, g_at_push, node).  The stale-entry check
        compares g_at_push against the current best g_score[node]: if a
        better path was found after this entry was pushed, g_at_push will be
        larger than g_score[node] and the entry is discarded.  This avoids
        an extra heuristic call on every pop and is the standard lazy-deletion
        pattern for A* without a decrease-key heap.

        f(n) = g(n) + h(n)
          g(n) — actual accumulated cost from start to n
          h(n) — admissible lower-bound estimate from n to goal
        """
        g_score   = {start: 0.0}
        came_from = {}

        h_start = heuristic_func(G, start, goal, risk_data, time_of_day)
        # heap: (f, g_at_push, node)
        pq = [(0.0 + h_start, 0.0, start)]
        nodes_expanded = 0

        while pq:
            f_pushed, g_pushed, current = heapq.heappop(pq)

            # Stale entry: a better path to `current` was found after this push
            if g_pushed > g_score.get(current, float('inf')):
                continue

            nodes_expanded += 1

            if current == goal:
                path = []
                node = current
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start)
                path.reverse()
                return path, nodes_expanded

            for neighbor in G.successors(current):
                # Best edge among parallel edges
                best_edge_cost = float('inf')
                best_key = None
                if G.has_edge(current, neighbor):
                    for key in G[current][neighbor]:
                        edge_attrs = risk_data.get(f"{current}_{neighbor}_{key}", {})
                        ec = cost_func.calculate_edge_cost(
                            G, current, neighbor, key, edge_attrs)
                        if ec < best_edge_cost:
                            best_edge_cost = ec
                            best_key = key

                if best_key is None:
                    continue

                tentative_g = g_score[current] + best_edge_cost

                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor]   = tentative_g
                    came_from[neighbor] = current
                    h_n = heuristic_func(G, neighbor, goal, risk_data, time_of_day)
                    heapq.heappush(pq, (tentative_g + h_n, tentative_g, neighbor))

        return None, nodes_expanded
    
    @staticmethod
    def depth_limited_search(G: nx.MultiDiGraph, start: int, goal: int,
                            cost_func=None, risk_data: Dict = None,
                            depth_limit: int = 20) -> Tuple[Optional[List], int]:
        """
        Depth Limited Search (DLS)
        
        DFS variant with a maximum depth constraint.
        Prevents infinite searches in cyclic graphs.
        
        Args:
            G: NetworkX graph
            start: Start node ID
            goal: Goal node ID
            cost_func: Cost function (ignored for DLS)
            risk_data: Risk database (ignored for DLS)
            depth_limit: Maximum depth to explore
            
        Returns:
            Tuple of (path, nodes_expanded)
        """
        nodes_expanded = 0
        
        def dls_helper(current, goal, depth, visited_set, path):
            nonlocal nodes_expanded
            nodes_expanded += 1
            
            if current == goal:
                return path
            
            if depth == 0:
                return None
            
            if current in visited_set:
                return None
            
            visited_set.add(current)
            
            for neighbor in G.successors(current):
                result = dls_helper(neighbor, goal, depth - 1, 
                                   visited_set, path + [neighbor])
                if result:
                    return result
            
            # Remove from visited set when backtracking (memory efficiency)
            visited_set.remove(current)
            return None
        
        result = dls_helper(start, goal, depth_limit, set(), [start])
        return result, nodes_expanded
    
    @staticmethod
    def iterative_deepening_depth_limited_search(G: nx.MultiDiGraph, start: int, goal: int,
                                                cost_func=None, risk_data: Dict = None,
                                                max_depth: int = 50) -> Tuple[Optional[List], int]:
        """
        Iterative Deepening Depth Limited Search (IDLS)

        Same as IDS but with an explicit upper bound on depth.
        Uses backtracking visited set (add on descent, remove on ascent)
        instead of copying — O(depth) memory per path, not O(V).
        """
        nodes_expanded = 0

        def dls_helper(current, goal, depth, path_set, path):
            nonlocal nodes_expanded
            nodes_expanded += 1

            if current == goal:
                return path

            if depth == 0:
                return None

            for neighbor in G.successors(current):
                if neighbor in path_set:   # cycle on current path only
                    continue
                path_set.add(neighbor)
                result = dls_helper(neighbor, goal, depth - 1,
                                    path_set, path + [neighbor])
                path_set.discard(neighbor)  # backtrack
                if result:
                    return result

            return None

        for depth in range(1, max_depth + 1):
            path_set = {start}
            result = dls_helper(start, goal, depth, path_set, [start])
            if result:
                return result, nodes_expanded

        return None, nodes_expanded
    
    @staticmethod
    def weighted_a_star_search(G: nx.MultiDiGraph, start: int, goal: int,
                              cost_func, heuristic_func, risk_data: Dict,
                              time_of_day: str = 'afternoon',
                              weight: float = 1.5) -> Tuple[Optional[List], int]:
        """
        Weighted A* — f(n) = g(n) + weight × h(n).

        weight = 1.0  →  standard A* (optimal)
        weight > 1.0  →  ε-suboptimal: found cost ≤ weight × optimal cost
        weight < 1.0  →  still optimal, slower than standard A*

        Same lazy-deletion stale-entry pattern as a_star_search.
        Heap entries: (f, g_at_push, node).
        """
        g_score   = {start: 0.0}
        came_from = {}

        h_start = heuristic_func(G, start, goal, risk_data, time_of_day)
        pq = [(0.0 + weight * h_start, 0.0, start)]
        nodes_expanded = 0

        while pq:
            f_pushed, g_pushed, current = heapq.heappop(pq)

            if g_pushed > g_score.get(current, float('inf')):
                continue

            nodes_expanded += 1

            if current == goal:
                path = []
                node = current
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start)
                path.reverse()
                return path, nodes_expanded

            for neighbor in G.successors(current):
                best_edge_cost = float('inf')
                best_key = None
                if G.has_edge(current, neighbor):
                    for key in G[current][neighbor]:
                        edge_attrs = risk_data.get(f"{current}_{neighbor}_{key}", {})
                        ec = cost_func.calculate_edge_cost(
                            G, current, neighbor, key, edge_attrs)
                        if ec < best_edge_cost:
                            best_edge_cost = ec
                            best_key = key

                if best_key is None:
                    continue

                tentative_g = g_score[current] + best_edge_cost

                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor]   = tentative_g
                    came_from[neighbor] = current
                    h_n = heuristic_func(G, neighbor, goal, risk_data, time_of_day)
                    heapq.heappush(pq, (tentative_g + weight * h_n, tentative_g, neighbor))

        return None, nodes_expanded


def get_algorithm(algorithm_name: str):
    """Get algorithm function by name"""
    algorithms = {
        'BFS': SearchAlgorithms.breadth_first_search,
        'DFS': SearchAlgorithms.depth_first_search,
        'UCS': SearchAlgorithms.uniform_cost_search,
        'DLS': SearchAlgorithms.depth_limited_search,
        'IDLS': SearchAlgorithms.iterative_deepening_depth_limited_search,
        'IDS': SearchAlgorithms.iterative_deepening_search,
        'Greedy': SearchAlgorithms.greedy_best_first_search,
        'A*': SearchAlgorithms.a_star_search,
        'Weighted A*': SearchAlgorithms.weighted_a_star_search,
    }
    return algorithms.get(algorithm_name)
