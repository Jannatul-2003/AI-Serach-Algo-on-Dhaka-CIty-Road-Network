import math
from typing import Dict, Any, Tuple
import networkx as nx

class CostFunction:
    """Calculate traversal costs for edges based on multiple factors"""
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize cost function with weights
        
        Args:
            weights: Dictionary of weight factors for each criterion
                    Default weights are balanced for most scenarios
        """
        # Default weights - user can adjust these via UI sliders
        self.default_weights = {
            'distance': 0.30,        # Base distance cost (30%)
            'risk_factor': 0.20,     # Safety risk (20%)
            'traffic_factor': 0.15,  # Traffic congestion (15%)
            'road_surface': 0.10,    # Road condition (10%)
            'weather': 0.10,         # Weather impact (10%)
            'construction': 0.05,    # Construction penalty (5%)
            'toll': 0.05,            # Toll roads (5%)
            'street_width': 0.03,    # Width penalty (3%)
            'travel_time': 0.02,     # Additional time factors (2%)
        }
        
        self.weights = weights if weights else self.default_weights.copy()
        self.custom_weights_applied = False  # Track if user has manually adjusted weights
    
    def normalize_weights(self):
        """Ensure weights sum to 1.0"""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}
    
    def calculate_edge_cost(self, G: nx.MultiDiGraph, u: int, v: int, key: int,
                            edge_attributes: Dict[str, Any],
                            distance: float = None) -> float:
        """
        Calculate total cost for traversing an edge
        
        Args:
            G: NetworkX graph
            u: Source node
            v: Target node
            key: Edge key
            edge_attributes: Risk attributes for the edge
            distance: Distance in meters (calculated if not provided)
            
        Returns:
            Total normalized cost (0.0-1.0+)
        """
        if distance is None:
            distance = self._get_edge_distance(G, u, v, key)
        
        cost = 0.0
        
        # 1. Base distance cost (fundamental component)
        distance_cost = self._calculate_distance_cost(distance)
        cost += self.weights['distance'] * distance_cost
        
        # 2. Risk factor (0-1 already normalized)
        cost += self.weights['risk_factor'] * edge_attributes.get('risk_factor', 0.5)
        
        # 3. Traffic factor
        traffic_cost = self._calculate_traffic_cost(edge_attributes)
        cost += self.weights['traffic_factor'] * traffic_cost
        
        # 4. Road surface condition
        surface_cost = self._calculate_surface_cost(edge_attributes)
        cost += self.weights['road_surface'] * surface_cost
        
        # 5. Weather condition
        weather_cost = self._calculate_weather_cost(edge_attributes)
        cost += self.weights['weather'] * weather_cost
        
        # 6. Construction work penalty
        construction_cost = 0.5 if edge_attributes.get('construction_work', False) else 0.0
        cost += self.weights['construction'] * construction_cost
        
        # 7. Toll penalty
        toll_cost = 0.3 if edge_attributes.get('tolled_street', False) else 0.0
        cost += self.weights['toll'] * toll_cost
        
        # 8. Street width benefit (wider = safer, lower cost)
        street_width = edge_attributes.get('street_width', 7)
        width_cost = max(0.0, 1.0 - (street_width / 15.0))  # Normalize 0-15m to 1-0
        cost += self.weights['street_width'] * width_cost
        
        # 9. Travel time (based on distance and congestion)
        travel_time_cost = self._calculate_travel_time_cost(distance, edge_attributes)
        cost += self.weights['travel_time'] * travel_time_cost
        
        return cost
    
    def _get_edge_distance(self, G: nx.MultiDiGraph, u: int, v: int, key: int) -> float:
        """
        Get distance for an edge from OSM data
        
        Args:
            G: NetworkX graph
            u: Source node
            v: Target node
            key: Edge key
            
        Returns:
            Distance in meters
        """
        try:
            edge_data = G.edges[u, v, key]
            # Try different possible length attributes from OSM data
            length = edge_data.get('length')
            if length is not None:
                return float(length)
            
            # Try other common distance attributes
            for attr in ['distance', 'dist', 'len']:
                if attr in edge_data:
                    return float(edge_data[attr])
            
            # If no length attribute, calculate from coordinates
            return self._haversine_distance(G, u, v)
            
        except Exception as e:
            # Fallback: calculate Haversine distance
            return self._haversine_distance(G, u, v)
    
    def _haversine_distance(self, G: nx.MultiDiGraph, u: int, v: int) -> float:
        """Calculate great-circle distance between two nodes"""
        lat1 = float(G.nodes[u].get('y', 0))
        lon1 = float(G.nodes[u].get('x', 0))
        lat2 = float(G.nodes[v].get('y', 0))
        lon2 = float(G.nodes[v].get('x', 0))
        
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _calculate_distance_cost(self, distance: float) -> float:
        """
        Calculate normalized distance cost (0-1).

        Normalized to a 5 km reference (typical max city-road segment).
        All other cost terms are also in [0,1], so this keeps the weighted
        sum dimensionally consistent and makes the heuristic risk/traffic
        terms meaningful relative to the distance term.

        Args:
            distance: Distance in meters

        Returns:
            Normalized distance cost in [0, 1]
        """
        MAX_EDGE_DISTANCE = 5000.0   # 5 km — reasonable upper bound for city edges
        return min(distance / MAX_EDGE_DISTANCE, 1.0)
    
    def _calculate_traffic_cost(self, edge_attributes: Dict[str, Any]) -> float:
        """Calculate normalized traffic cost (0-1)"""
        traffic_map = {
            'low': 0.1,
            'medium': 0.5,
            'high': 0.9,
        }
        
        base_cost = traffic_map.get(edge_attributes.get('traffic_factor', 'medium'), 0.5)
        
        # Adjust by number of vehicles
        num_vehicles = edge_attributes.get('num_vehicles', 25)
        vehicle_factor = min(num_vehicles / 50.0, 1.0)
        
        return min(base_cost + vehicle_factor * 0.1, 1.0)
    
    def _calculate_surface_cost(self, edge_attributes: Dict[str, Any]) -> float:
        """Calculate normalized road surface cost (0-1)"""
        surface_map = {
            'poor': 0.8,
            'fair': 0.4,
            'good': 0.1,
        }
        
        return surface_map.get(edge_attributes.get('road_surface_condition', 'fair'), 0.4)
    
    def _calculate_weather_cost(self, edge_attributes: Dict[str, Any]) -> float:
        """Calculate normalized weather cost (0-1)"""
        weather_map = {
            'clear': 0.0,
            'rain': 0.3,
            'fog': 0.5,
            'storm': 0.9,
        }
        
        return weather_map.get(edge_attributes.get('weather_condition', 'clear'), 0.0)
    
    def _calculate_travel_time_cost(self, distance: float, 
                                    edge_attributes: Dict[str, Any]) -> float:
        """
        Calculate travel time cost based on distance and congestion
        
        Args:
            distance: Distance in meters
            edge_attributes: Edge risk attributes
            
        Returns:
            Normalized travel time cost (0-1)
        """
        # Estimate travel time (in seconds)
        # Base speed depends on traffic
        traffic_level = edge_attributes.get('traffic_factor', 'medium')
        speed_map = {
            'low': 15,  # m/s (~54 km/h)
            'medium': 10,  # m/s (~36 km/h)
            'high': 5,  # m/s (~18 km/h)
        }
        
        base_speed = speed_map.get(traffic_level, 10)
        
        # Adjust for surface condition
        surface = edge_attributes.get('road_surface_condition', 'fair')
        surface_multiplier = {
            'poor': 0.6,
            'fair': 0.8,
            'good': 1.0,
        }
        
        speed = base_speed * surface_multiplier.get(surface, 0.8)
        
        # Calculate time in seconds
        travel_time = distance / speed if speed > 0 else distance / 10
        
        # Normalize to 0-1 (assuming max 5 minutes = 300 seconds is reasonable)
        normalized_time = min(travel_time / 300.0, 1.0)
        
        return normalized_time
    
    def calculate_path_cost(self, G: nx.MultiDiGraph, path: list,
                           risk_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate total cost for a complete path
        
        Args:
            G: NetworkX graph
            path: List of node IDs representing the path
            risk_data: Risk database
            
        Returns:
            Tuple of (total_cost, statistics_dict)
        """
        total_cost = 0.0
        total_distance = 0.0
        total_travel_time = 0.0
        avg_risk = 0.0
        edge_count = 0
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            
            # Handle MultiDiGraph - find the best edge
            if G.has_edge(u, v):
                best_edge_cost = float('inf')
                best_distance = 0
                best_risk = 0
                best_travel_time = 0
                
                # Check all edges between u and v
                for key in G[u][v]:
                    edge_data = G.edges[u, v, key]
                    distance = self._get_edge_distance(G, u, v, key)
                    
                    # Get risk attributes
                    edge_id = f"{u}_{v}_{key}"
                    edge_attributes = risk_data.get(edge_id, {})
                    
                    # Calculate edge cost
                    edge_cost = self.calculate_edge_cost(G, u, v, key, edge_attributes, distance)
                    
                    # Use the best (lowest cost) edge
                    if edge_cost < best_edge_cost:
                        best_edge_cost = edge_cost
                        best_distance = distance
                        best_risk = edge_attributes.get('risk_factor', 0.5)
                        
                        # Estimate travel time
                        traffic_level = edge_attributes.get('traffic_factor', 'medium')
                        speed_map = {'low': 15, 'medium': 10, 'high': 5}
                        speed = speed_map.get(traffic_level, 10)
                        best_travel_time = distance / speed if speed > 0 else distance / 10
                
                total_cost += best_edge_cost
                total_distance += best_distance
                total_travel_time += best_travel_time
                avg_risk += best_risk
                edge_count += 1
        
        avg_risk = avg_risk / edge_count if edge_count > 0 else 0
        
        stats = {
            'total_cost': total_cost,
            'total_distance': total_distance,
            'total_travel_time_seconds': total_travel_time,
            'total_travel_time_minutes': total_travel_time / 60.0,
            'avg_risk_factor': avg_risk,
            'num_edges': edge_count,
        }
        
        return total_cost, stats
    
    def set_optimization_criteria(self, criteria: str):
        """
        Adjust weights for different optimization criteria
        
        IMPORTANT: This is skipped if user has manually adjusted weights!
        Custom weights always take precedence over optimization presets.
        
        Args:
            criteria: One of 'fastest', 'safest', 'cheapest'
        """
        # Skip if user has manually adjusted weights
        if self.custom_weights_applied:
            return
        if criteria == 'fastest':
            # Prioritize travel time and traffic, minimize distance impact
            self.weights = {
                'distance': 0.10,        # Low distance priority (10%)
                'risk_factor': 0.05,     # Very low risk priority (5%)
                'traffic_factor': 0.35,  # High traffic priority (35%)
                'road_surface': 0.05,    # Low surface priority (5%)
                'weather': 0.05,         # Low weather priority (5%)
                'construction': 0.05,    # Low construction priority (5%)
                'toll': 0.00,            # Ignore tolls (0%)
                'street_width': 0.05,    # Low width priority (5%)
                'travel_time': 0.30,     # High time priority (30%)
            }
        elif criteria == 'safest':
            # Prioritize risk and infrastructure, moderate distance consideration
            self.weights = {
                'distance': 0.15,        # Moderate distance priority (15%)
                'risk_factor': 0.30,     # Highest risk priority (30%)
                'traffic_factor': 0.15,  # Medium traffic priority (15%)
                'road_surface': 0.15,    # Medium surface priority (15%)
                'weather': 0.10,         # Medium weather priority (10%)
                'construction': 0.10,    # Medium construction priority (10%)
                'toll': 0.00,            # Ignore tolls (0%)
                'street_width': 0.05,    # Low width priority (5%)
                'travel_time': 0.00,     # Ignore time (0%)
            }
        elif criteria == 'cheapest':
            # Prioritize distance (fuel cost) and avoid tolls
            self.weights = {
                'distance': 0.35,        # High distance priority (35%) - fuel cost
                'risk_factor': 0.05,     # Low risk priority (5%)
                'traffic_factor': 0.10,  # Low traffic priority (10%)
                'road_surface': 0.05,    # Low surface priority (5%)
                'weather': 0.05,         # Low weather priority (5%)
                'construction': 0.05,    # Low construction priority (5%)
                'toll': 0.30,            # High toll penalty (30%)
                'street_width': 0.03,    # Very low width priority (3%)
                'travel_time': 0.02,     # Very low time priority (2%)
            }
        
        self.normalize_weights()
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update weights from user input (UI sliders)
        This marks weights as customized so optimization_criteria won't override them
        
        Args:
            new_weights: Dictionary of new weights
        """
        self.weights.update(new_weights)
        self.normalize_weights()
        self.custom_weights_applied = True  # Mark as custom so optimization_criteria is skipped
    
    def reset_custom_weights(self):
        """Reset custom weights flag so optimization_criteria presets work again"""
        self.custom_weights_applied = False
