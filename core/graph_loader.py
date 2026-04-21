import networkx as nx
import os
from typing import Tuple

class GraphLoader:
    """Load and prepare the Dhaka road network graph"""
    
    @staticmethod
    def load_graph(graphml_path: str) -> nx.MultiDiGraph:
        """
        Load the road network graph from GraphML file
        
        Args:
            graphml_path: Path to the GraphML file
            
        Returns:
            NetworkX MultiDiGraph object
        """
        if not os.path.exists(graphml_path):
            raise FileNotFoundError(f"GraphML file not found: {graphml_path}")
        
        print(f"Loading graph from {graphml_path}...")
        G = nx.read_graphml(graphml_path)
        
        print(f"Graph loaded successfully!")
        print(f"  - Nodes: {G.number_of_nodes()}")
        print(f"  - Edges: {G.number_of_edges()}")
        
        return G
    
    @staticmethod
    def get_node_coordinates(G: nx.MultiDiGraph, node_id) -> Tuple[float, float]:
        """
        Get latitude and longitude of a node
        
        Args:
            G: NetworkX graph
            node_id: Node identifier
            
        Returns:
            Tuple of (latitude, longitude)
        """
        node_data = G.nodes[node_id]
        lat = float(node_data.get('y', 0))
        lon = float(node_data.get('x', 0))
        return lat, lon
    
    @staticmethod
    def get_all_nodes(G: nx.MultiDiGraph) -> list:
        """
        Get list of all node IDs
        
        Args:
            G: NetworkX graph
            
        Returns:
            List of node IDs
        """
        return list(G.nodes())
    
    @staticmethod
    def validate_node(G: nx.MultiDiGraph, node_id) -> bool:
        """
        Check if a node exists in the graph
        
        Args:
            G: NetworkX graph
            node_id: Node identifier
            
        Returns:
            True if node exists, False otherwise
        """
        return node_id in G.nodes()
