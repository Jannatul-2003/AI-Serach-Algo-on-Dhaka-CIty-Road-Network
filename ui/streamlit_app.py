import streamlit as st
import folium
from streamlit_folium import st_folium
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.route_optimizer import RouteOptimizer

# Page configuration
st.set_page_config(
    page_title="Dhaka Route Optimizer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'optimizer' not in st.session_state:
    graphml_path = 'data/dhaka_road_graph.graphml'
    if os.path.exists(graphml_path):
        st.session_state.optimizer = RouteOptimizer(graphml_path)
    else:
        st.error(f"GraphML file not found at {graphml_path}")
        st.stop()

if 'last_results' not in st.session_state:
    st.session_state.last_results = None

if 'last_routes_data' not in st.session_state:
    st.session_state.last_routes_data = None

if 'current_optimization_criteria' not in st.session_state:
    st.session_state.current_optimization_criteria = 'fastest'

if 'last_weights_applied' not in st.session_state:
    st.session_state.last_weights_applied = None

optimizer = st.session_state.optimizer

# Title and description
st.title("🗺️ Dhaka Road Network Route Optimizer")
st.markdown("""
Intelligent pathfinding system using multiple search algorithms with realistic edge factors.
Find the **fastest**, **safest**, or **cheapest** routes through Dhaka city.
""")

# Get network info
graph_info = optimizer.get_graph_info()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Network Nodes", graph_info['total_nodes'])
col2.metric("Network Edges", graph_info['total_edges'])
col3.metric("Risk Database", graph_info['risk_database_edges'])
col4.metric("Avg Risk Factor", f"{graph_info['risk_stats']['avg_risk_factor']:.3f}")

st.divider()

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Get available nodes
    all_nodes = optimizer.get_available_nodes()
    
    # Source and destination
    st.subheader("📍 Route Selection")
    source = st.selectbox(
        "Source Node ID",
        all_nodes,
        key="source_node",
        help="Select starting location"
    )
    
    destination = st.selectbox(
        "Destination Node ID",
        all_nodes,
        key="dest_node",
        help="Select ending location"
    )
    
    # Time settings
    st.subheader("⏰ Time Settings")
    col_day, col_hour = st.columns(2)
    with col_day:
        day_of_week = st.selectbox(
            "Day of Week",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            index=0
        )
    with col_hour:
        hour_of_day = st.slider("Hour of Day", 0, 23, 14)
    
    # Traveler information
    st.subheader("👤 Traveler Info")
    vehicle_type = st.selectbox(
        "Vehicle Type",
        ["car", "motorcycle", "bus", "bicycle", "rickshaw", "truck", "mixed"]
    )
    
    col_gender, col_age = st.columns(2)
    with col_gender:
        gender = st.selectbox("Gender", ["male", "female", "mixed"])
    with col_age:
        age_group = st.selectbox("Age Group", ["child", "adult", "elderly"])
    
    # Algorithm selection
    st.subheader("🔍 Search Algorithms")
    algorithms = st.multiselect(
        "Select Algorithms",
        ["BFS", "DFS", "UCS", "DLS", "IDLS", "IDS", "Greedy", "A*", "Weighted A*"],
        default=["A*", "Weighted A*"],
        help="Select one or more algorithms to compare"
    )

    if not algorithms:
        st.warning("Please select at least one algorithm")
    
    # Optimization criteria
    st.subheader("🎯 Optimization Criteria")
    selected_criteria = st.radio(
        "Optimize Route For",
        ["fastest", "safest", "cheapest"],
        captions=[
            "Minimize travel time and traffic",
            "Minimize risk and maximize safety",
            "Minimize tolls and overall cost"
        ]
    )
    
    # Reset custom weights when optimization criteria changes
    if selected_criteria != st.session_state.current_optimization_criteria:
        st.session_state.current_optimization_criteria = selected_criteria
        optimizer.reset_custom_weights()
        st.info(f"✅ Switched to **{selected_criteria.upper()}** optimization")
    
    # Cost function weight adjustment
    st.subheader("⚖️ Cost Function Weights")
    with st.expander("Adjust Weights"):
        # Get current criteria weights to show as defaults
        if st.session_state.current_optimization_criteria == 'fastest':
            default_weights = {
                'risk_factor': 0.05, 'traffic_factor': 0.35, 'road_surface': 0.05,
                'weather': 0.05, 'construction': 0.05, 'toll': 0.00,
                'street_width': 0.05, 'travel_time': 0.40,
            }
        elif st.session_state.current_optimization_criteria == 'safest':
            default_weights = {
                'risk_factor': 0.35, 'traffic_factor': 0.15, 'road_surface': 0.15,
                'weather': 0.10, 'construction': 0.10, 'toll': 0.00,
                'street_width': 0.10, 'travel_time': 0.05,
            }
        else:  # cheapest
            default_weights = {
                'risk_factor': 0.10, 'traffic_factor': 0.10, 'road_surface': 0.05,
                'weather': 0.05, 'construction': 0.05, 'toll': 0.50,
                'street_width': 0.05, 'travel_time': 0.10,
            }
        
        col1, col2 = st.columns(2)
        with col1:
            w_risk = st.slider("Risk Factor", 0.0, 1.0, 
                             default_weights['risk_factor'], 0.05,
                             help="Weight for overall risk")
            w_traffic = st.slider("Traffic Factor", 0.0, 1.0,
                                default_weights['traffic_factor'], 0.05)
            w_surface = st.slider("Road Surface", 0.0, 1.0,
                                default_weights['road_surface'], 0.05)
            w_weather = st.slider("Weather Condition", 0.0, 1.0,
                                default_weights['weather'], 0.05)
        
        with col2:
            w_construction = st.slider("Construction Work", 0.0, 1.0,
                                     default_weights['construction'], 0.05)
            w_toll = st.slider("Toll Factor", 0.0, 1.0,
                             default_weights['toll'], 0.05)
            w_width = st.slider("Street Width", 0.0, 1.0,
                              default_weights['street_width'], 0.05)
            w_time = st.slider("Travel Time", 0.0, 1.0,
                             default_weights['travel_time'], 0.05)
        
        # Only update weights if they differ from the current optimization criteria defaults
        new_weights = {
            'risk_factor': w_risk,
            'traffic_factor': w_traffic,
            'road_surface': w_surface,
            'weather': w_weather,
            'construction': w_construction,
            'toll': w_toll,
            'street_width': w_width,
            'travel_time': w_time,
        }
        
        # Check if weights differ from the criteria defaults
        weights_changed = any(new_weights[k] != default_weights.get(k, 0) for k in new_weights)
        
        if weights_changed:
            st.warning("⚠️ You've customized weights (will override optimization criteria)")
            optimizer.update_cost_weights(new_weights)
        else:
            st.info("Using optimization criteria weights")
    
    st.divider()
    
    # Find routes button
    if st.button("🚀 Find Routes", width='stretch'):
        if not algorithms:
            st.error("Please select at least one algorithm")
        elif source == destination:
            st.error("Source and destination must be different")
        else:
            with st.spinner("Finding routes..."):
                results = optimizer.find_routes(
                    source=source,
                    destination=destination,
                    algorithms=algorithms,
                    vehicle_type=vehicle_type,
                    gender=gender,
                    age_group=age_group,
                    day_of_week=day_of_week,
                    hour_of_day=hour_of_day,
                    optimization_criteria=selected_criteria
                )
                st.session_state.last_results = results
                st.session_state.last_routes_data = (source, destination)
                st.success("Routes found!")

# Main content area
if st.session_state.last_results:
    results = st.session_state.last_results
    
    if 'error' not in results:
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📍 Map View", "📊 Route Comparison", "📈 Statistics", "📚 Algorithm Info"])
        
        with tab1:
            st.subheader("Route Visualization on Map")
            
            # Rank routes by cost
            rankings = optimizer.rank_routes(results)
            
            if rankings:
                # Initialize visibility state for algorithms
                if 'algo_visibility' not in st.session_state:
                    st.session_state.algo_visibility = {algo: True for algo, _ in rankings}
                
                # Show visibility toggles
                st.subheader("🔍 Path Visibility")
                cols = st.columns(min(4, len(rankings)))
                for idx, (algo_name, _) in enumerate(rankings):
                    with cols[idx % len(cols)]:
                        st.session_state.algo_visibility[algo_name] = st.checkbox(
                            f"{algo_name} (#{idx+1})",
                            value=st.session_state.algo_visibility.get(algo_name, True)
                        )
                
                # Filter rankings based on visibility
                visible_rankings = [(algo, cost) for algo, cost in rankings if st.session_state.algo_visibility.get(algo, True)]
                
                if visible_rankings:
                    # Create map centered on first visible path's first node
                    first_algo = visible_rankings[0][0]
                    if results['algorithms'][first_algo].get('path'):
                        start_coords = optimizer.get_node_coordinates(results['algorithms'][first_algo]['path'][0])
                    m = folium.Map(
                        location=[start_coords[0], start_coords[1]],
                        zoom_start=13,
                        tiles="OpenStreetMap"
                    )
                    
                    # Plot visible routes
                    for display_idx, (algo_name, cost) in enumerate(visible_rankings):
                        path = results['algorithms'][algo_name]['path']
                        if path:
                            coords = optimizer.get_path_coordinates(path)
                            
                            # Convert to folium format (lat, lon)
                            path_coords = [[lat, lon] for lat, lon in coords]
                            
                            # Create popup text
                            stats = results['algorithms'][algo_name]['statistics']
                            popup_text = f"""
                            <b>Algorithm: {algo_name}</b><br>
                            Cost: {cost:.4f}<br>
                            Distance: {stats['total_distance']:.0f}m<br>
                            Time: {stats['total_travel_time_minutes']:.1f} min<br>
                            Risk: {stats['avg_risk_factor']:.3f}
                            """
                            
                            # Draw path
                            folium.PolyLine(
                                path_coords,
                                color='#00AA00',
                                weight=4,
                                opacity=1.0,
                                popup=folium.Popup(popup_text, max_width=300)
                            ).add_to(m)
                    
                    # Add start and end markers
                    start_coords = optimizer.get_node_coordinates(results['source'])
                    end_coords = optimizer.get_node_coordinates(results['destination'])
                    
                    folium.Marker(
                        [start_coords[0], start_coords[1]],
                        popup=f"Start: Node {results['source']}",
                        icon=folium.Icon(color='green', icon='play')
                    ).add_to(m)
                    
                    folium.Marker(
                        [end_coords[0], end_coords[1]],
                        popup=f"End: Node {results['destination']}",
                        icon=folium.Icon(color='red', icon='stop')
                    ).add_to(m)
                    
                    # Add legend
                    legend_html = '''
                    <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 280px; height: auto; 
                        background-color: #f8f9fa; border:3px solid #333; z-index:9999; 
                        font-size:12px; padding: 12px; border-radius: 5px; color: #000;">
                    <b style="color: #000; font-size: 14px;">Route Rankings</b><br>
                    <hr style="margin: 5px 0; border: 1px solid #ccc;">
                    '''
                    for display_idx, (algo_name, cost) in enumerate(visible_rankings):
                        legend_html += f'<div style="margin: 4px 0;"><span style="color: #00AA00; font-size: 12px;">▬</span> <b style="color: #000;">{algo_name}</b> (#{display_idx+1})</div>'
                    
                    legend_html += '<hr style="margin: 5px 0; border: 1px solid #ccc;">'
                    legend_html += '<div style="margin: 4px 0;"><span style="color: #00AA00; font-size: 18px;">●</span> <b style="color: #000;">Start</b></div>'
                    legend_html += '<div style="margin: 4px 0;"><span style="color: #FF0000; font-size: 18px;">●</span> <b style="color: #000;">End</b></div>'
                    legend_html += '</div>'
                    
                    m.get_root().html.add_child(folium.Element(legend_html))
                    
                    st_folium(m, width=1000, height=600)
                else:
                    st.warning("Please select at least one path to display")
            else:
                st.warning("No routes found to display")
        
        with tab2:
            st.subheader("Route Comparison")
            
            # Create comparison table
            rankings = optimizer.rank_routes(results)
            
            comparison_data = []
            for rank, (algo_name, cost) in enumerate(rankings, 1):
                route_info = results['algorithms'][algo_name]
                stats = route_info['statistics']
                
                comparison_data.append({
                    'Rank': rank,
                    'Algorithm': algo_name,
                    'Cost': f"{cost:.4f}",
                    'Distance (m)': f"{stats['total_distance']:.0f}",
                    'Time (min)': f"{stats['total_travel_time_minutes']:.1f}",
                    'Avg Risk': f"{stats['avg_risk_factor']:.3f}",
                    'Edges': stats['num_edges'],
                    'Nodes Expanded': route_info['nodes_expanded'],
                })
            
            st.dataframe(comparison_data, width='stretch')
            
            # Filter and sort options
            st.subheader("Filter and Sort Paths")
            
            filter_by = st.selectbox(
                "Sort by",
                ["Cost (ascending)", "Cost (descending)", "Distance", "Travel Time", "Risk Factor"]
            )
            
            col_algo, col_metric = st.columns(2)
            with col_algo:
                selected_algos = st.multiselect(
                    "Filter by Algorithm",
                    list(results['algorithms'].keys())
                )
            
        
        with tab3:
            st.subheader("Detailed Route Statistics")
            
            # Show detailed stats for best route
            if rankings:
                best_algo, best_cost = rankings[0]
                best_route = results['algorithms'][best_algo]
                
                st.info(f"**Best Route**: {best_algo} with cost {best_cost:.4f}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                stats = best_route['statistics']
                col1.metric("Total Distance", f"{stats['total_distance']/1000:.2f} km")
                col2.metric("Travel Time", f"{stats['total_travel_time_minutes']:.1f} min")
                col3.metric("Avg Risk Factor", f"{stats['avg_risk_factor']:.3f}")
                col4.metric("Number of Edges", stats['num_edges'])
                
                # Show all algorithm statistics
                st.subheader("All Algorithms Statistics")
                
                for algo_name, route_info in sorted(results['algorithms'].items()):
                    if route_info.get('path'):
                        with st.expander(f"📋 {algo_name}"):
                            stats = route_info['statistics']
                            
                            c1, c2, c3 = st.columns(3)
                            c1.write(f"**Distance**: {stats['total_distance']:.0f} m")
                            c2.write(f"**Time**: {stats['total_travel_time_minutes']:.1f} min")
                            c3.write(f"**Risk**: {stats['avg_risk_factor']:.3f}")
                            
                            c4, c5, c6 = st.columns(3)
                            c4.write(f"**Cost**: {route_info['cost']:.4f}")
                            c5.write(f"**Edges**: {stats['num_edges']}")
                            c6.write(f"**Nodes Expanded**: {route_info['nodes_expanded']}")
                    else:
                        st.warning(f"{algo_name}: {route_info.get('error', 'No path found')}")
        
        with tab4:
            st.subheader("Algorithm Information")
            
            # Algorithm descriptions
            algo_info = {
                'BFS': {
                    'type': 'Uninformed',
                    'optimal': '❌ Not optimal (only counts edges)',
                    'complete': '✅ Complete',
                    'description': 'Explores nodes level by level. Guarantees shortest path in terms of edge count, not cost.'
                },
                'DFS': {
                    'type': 'Uninformed',
                    'optimal': '❌ Not optimal',
                    'complete': '⚠️ Incomplete (without cycle detection)',
                    'description': 'Explores along a branch before backtracking. Memory efficient but no optimality guarantee.'
                },
                'UCS': {
                    'type': 'Uninformed',
                    'optimal': '✅ Optimal',
                    'complete': '✅ Complete',
                    'description': 'Expands lowest-cost node first. Guarantees minimum cost path without heuristic guidance.'
                },
                'DLS': {
                    'type': 'Uninformed',
                    'optimal': '❌ Not optimal',
                    'complete': '⚠️ Incomplete (may miss goal beyond depth limit)',
                    'description': 'Depth-first search with maximum depth constraint. Prevents infinite loops but may not find solution.'
                },
                'IDLS': {
                    'type': 'Uninformed',
                    'optimal': '✅ Optimal (with cost)',
                    'complete': '✅ Complete (within max depth)',
                    'description': 'Iterative deepening with depth limit. Combines DLS with iterative approach for better coverage.'
                },
                'IDS': {
                    'type': 'Uninformed',
                    'optimal': '✅ Optimal (with cost)',
                    'complete': '✅ Complete',
                    'description': 'Combines DFS space efficiency with BFS completeness through iterative deepening.'
                },
                'Greedy': {
                    'type': 'Informed',
                    'optimal': '❌ Not optimal',
                    'complete': '✅ Complete',
                    'description': 'Expands node with lowest heuristic value. Fast but may not find best path.'
                },
                'A*': {
                    'type': 'Informed',
                    'optimal': '✅ Optimal (if h is admissible)',
                    'complete': '✅ Complete',
                    'description': 'Expands nodes with lowest f(n)=g(n)+h(n). Best performance with admissible heuristic.'
                },
                'Weighted A*': {
                    'type': 'Informed',
                    'optimal': '⚠️ Suboptimal (prioritizes speed)',
                    'complete': '✅ Complete',
                    'description': 'A* variant with weighted heuristic (w>1). Sacrifices optimality for faster search.'
                },
            }
            
            for algo, info in algo_info.items():
                with st.expander(f"**{algo}** - {info['type']}"):
                    col1, col2 = st.columns(2)
                    col1.write(f"**Optimal**: {info['optimal']}")
                    col2.write(f"**Complete**: {info['complete']}")
                    st.write(f"**Description**: {info['description']}")
            
            # Heuristic documentation
            st.subheader("🧭 Heuristic Function")
            h_info = optimizer.get_heuristic_info()
            st.markdown(f"**{h_info['name']}**")
            st.write(h_info['description'])
            st.markdown("""
            **Formula:**
            ```
            h(n) = w_d × min(straight_line / 5000, 1.0)
                 + w_r × min_risk
                 + w_t × min_traffic
            ```
            **Admissibility proof:**  
            - `min(SL/5000, 1) ≤ sum of normalized edge distances` (triangle inequality)  
            - `min_risk ≤ every edge's risk_factor`  
            - `min_traffic ≤ every edge's traffic_cost`  
            - Therefore `h(n) ≤ actual_cost(n → goal)` ✅
            """)
            st.info("A* with this heuristic is guaranteed to find the optimal path.")
    
    else:
        st.error(results.get('error', 'Error finding routes'))

else:
    st.info("👈 Configure route parameters in the sidebar and click 'Find Routes' to begin")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>🚀 Dhaka Road Network Route Optimizer | AI Lab Project</p>
    <p>Using OSMnx for graph data and multiple search algorithms for pathfinding</p>
</div>
""", unsafe_allow_html=True)
