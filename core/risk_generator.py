import pickle
import os
import random
import networkx as nx
from typing import Dict, Any
import numpy as np


class RiskDatabase:
    """Generate and manage risk attributes for road edges"""

    TRAFFIC_LEVELS = ['low', 'medium', 'high']
    GENDERS = ['male', 'female', 'mixed']
    AGE_GROUPS = ['child', 'adult', 'elderly']
    VEHICLE_TYPES = ['rickshaw', 'bus', 'car', 'mixed', 'bicycle', 'motorcycle', 'truck']
    WEATHER_CONDITIONS = ['clear', 'rain', 'fog', 'storm']
    STREET_LIGHTING = ['none', 'partial', 'full']
    ROAD_SURFACE = ['poor', 'fair', 'good']
    PEAK_TIMES = ['morning', 'afternoon', 'evening', 'night']

    def __init__(self, db_path: str = 'data/risk_database.pkl'):
        self.db_path = db_path
        self.risk_data = {}
        self.load_or_create()

    def load_or_create(self):
        if os.path.exists(self.db_path):
            print(f"Loading risk database from {self.db_path}...")
            with open(self.db_path, 'rb') as f:
                self.risk_data = pickle.load(f)
            print(f"Loaded risk data for {len(self.risk_data)} edges")
        else:
            print("Risk database not found. Will generate on first use.")

    def generate_risk_data_for_graph(self, G: nx.MultiDiGraph):
        print("Generating risk data for all edges...")

        total_edges = G.number_of_edges()
        count = 0

        for u, v, key, data in G.edges(keys=True, data=True):
            edge_id = f"{u}_{v}_{key}"

            if edge_id not in self.risk_data:
                self.risk_data[edge_id] = self._generate_edge_attributes(data)
                count += 1

            if count % 1000 == 0:
                print(f"  Generated {count}/{total_edges} edges...")

        print(f"Completed! Generated {count} new edge records")
        self.save()

    def _generate_edge_attributes(self, osm_data: Dict[str, Any]) -> Dict[str, Any]:
        street_width = self._extract_street_width(osm_data)
        road_surface = self._get_road_surface(osm_data)

        attributes = {
            'traffic_factor': random.choice(self.TRAFFIC_LEVELS),
            'is_holiday': random.choice([True, False]),
            'gender_predominant': random.choice(self.GENDERS),
            'age_group': random.choice(self.AGE_GROUPS),
            'vehicle_types': random.choice(self.VEHICLE_TYPES),
            'construction_work': random.choice([True, False]),
            'weather_condition': random.choice(self.WEATHER_CONDITIONS),
            'tolled_street': random.choice([True, False]),
            'num_vehicles': random.randint(1, 50),
            'street_width': street_width,
            'num_accidents_per_year': random.randint(0, 20),
            'num_police_boxes_500m': random.randint(0, 5),
            'street_lighting': random.choice(self.STREET_LIGHTING),
            'road_surface_condition': road_surface,
            'peak_usage_time': random.choice(self.PEAK_TIMES),
        }

        attributes['risk_factor'] = self._calculate_risk_factor(attributes)
        return attributes

    def _extract_street_width(self, osm_data: Dict[str, Any]) -> float:
        if 'width' in osm_data:
            try:
                return float(osm_data['width'])
            except:
                pass

        highway_type = osm_data.get('highway', 'residential')
        width_map = {
            'motorway': 12,
            'trunk': 11,
            'primary': 10,
            'secondary': 9,
            'tertiary': 8,
            'residential': 6,
            'living_street': 5,
            'pedestrian': 3,
            'service': 5,
        }

        return float(width_map.get(highway_type, 7))

    def _get_road_surface(self, osm_data: Dict[str, Any]) -> str:
        highway_type = osm_data.get('highway', 'residential')

        if highway_type in ['motorway', 'trunk', 'primary']:
            return random.choice(['fair', 'good'])
        elif highway_type in ['secondary', 'tertiary']:
            return random.choice(['fair', 'good'])
        else:
            return random.choice(['poor', 'fair', 'good'])

    def _calculate_risk_factor(self, a: Dict[str, Any]) -> float:
        risk = 0.0

        # ---------------------------
        # BASE FACTORS (existing)
        # ---------------------------

        traffic_map = {'low': 0.05, 'medium': 0.15, 'high': 0.30}
        risk += traffic_map.get(a['traffic_factor'], 0.15)

        weather_map = {'clear': 0.0, 'rain': 0.08, 'fog': 0.12, 'storm': 0.20}
        risk += weather_map.get(a['weather_condition'], 0.08)

        if a['construction_work']:
            risk += 0.15

        surface_map = {'poor': 0.15, 'fair': 0.08, 'good': 0.02}
        risk += surface_map.get(a['road_surface_condition'], 0.08)

        accident_risk = min(a['num_accidents_per_year'] / 20.0, 1.0) * 0.1
        risk += accident_risk

        lighting_map = {'none': 0.10, 'partial': 0.05, 'full': 0.0}
        risk += lighting_map.get(a['street_lighting'], 0.05)

        if a['tolled_street']:
            risk += 0.05


        # Vehicle density
        risk += min(a['num_vehicles'] / 50.0, 1.0) * 0.1

        # Narrow roads = risky
        if a['street_width'] < 5:
            risk += 0.10
        elif a['street_width'] < 8:
            risk += 0.05

        # Police presence reduces risk
        risk -= min(a['num_police_boxes_500m'] * 0.02, 0.1)

        # Night + poor lighting = dangerous
        if a['peak_usage_time'] == 'night' and a['street_lighting'] == 'none':
            risk += 0.10

        # Holiday effect (less traffic but more unpredictability)
        if a['is_holiday']:
            risk += 0.03

        # Vehicle type risk
        if a['vehicle_types'] in ['truck', 'bus']:
            risk += 0.05
        elif a['vehicle_types'] in ['motorcycle']:
            risk += 0.04

        # Vulnerable population
        if a['age_group'] in ['child', 'elderly']:
            risk += 0.03

        # Gender-based safety proxy (optional heuristic)
        if a['gender_predominant'] == 'female' and a['peak_usage_time'] == 'night':
            risk += 0.05

        # ---------------------------
        # FINAL NORMALIZATION
        # ---------------------------

        risk = max(0.0, min(risk, 1.0))
        return risk

    def get_edge_risk(self, u: int, v: int, key: int = 0) -> Dict[str, Any]:
        edge_id = f"{u}_{v}_{key}"
        return self.risk_data.get(edge_id, {})

    def get_time_adjusted_attributes(self, attributes: Dict[str, Any],
                                     day_of_week: str, hour: int) -> Dict[str, Any]:

        adjusted = attributes.copy()

        if 7 <= hour < 10:
            adjusted['peak_usage_time'] = 'morning'
        elif 10 <= hour < 16:
            adjusted['peak_usage_time'] = 'afternoon'
        elif 16 <= hour < 20:
            adjusted['peak_usage_time'] = 'evening'
        else:
            adjusted['peak_usage_time'] = 'night'

        if adjusted['peak_usage_time'] in ['morning', 'evening']:
            if adjusted['traffic_factor'] == 'low':
                adjusted['traffic_factor'] = 'medium'
            elif adjusted['traffic_factor'] == 'medium':
                adjusted['traffic_factor'] = 'high'

        holidays = ['Saturday', 'Sunday']
        adjusted['is_holiday'] = day_of_week in holidays

        adjusted['risk_factor'] = self._calculate_risk_factor(adjusted)
        return adjusted

    def save(self):
        os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True)
        with open(self.db_path, 'wb') as f:
            pickle.dump(self.risk_data, f)
        print(f"Risk database saved to {self.db_path}")

    def get_statistics(self) -> Dict[str, Any]:
        if not self.risk_data:
            return {"total_edges": 0}

        risk_factors = [v['risk_factor'] for v in self.risk_data.values()]

        return {
            "total_edges": len(self.risk_data),
            "avg_risk_factor": np.mean(risk_factors),
            "min_risk_factor": np.min(risk_factors),
            "max_risk_factor": np.max(risk_factors),
            "std_risk_factor": np.std(risk_factors),
        }