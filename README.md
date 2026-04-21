# 🗺️ Dhaka Road Network Route Optimizer

An intelligent pathfinding system for Dhaka city using multiple search algorithms with realistic edge factors and advanced heuristics.
Run the app via this command:
```
 venv\Scripts\streamlit run ui/streamlit_app.py
```
from
386945620
to
4369503575


## 📋 Project Overview

This AI Lab project implements a sophisticated route optimization system that:

- **Loads Dhaka's road network** using OSMnx and NetworkX
- **Models 16 edge attributes** including traffic, weather, road quality, safety factors, etc.
- **Implements 10 search algorithms**: BFS, DFS, UCS, DLS, IDLS, IDS, Bidirectional, Greedy, A*, Weighted A*
- **Uses 3 admissible heuristics** for informed search optimization
- **Calculates costs** using a weighted, customizable cost function
- **Adjusts factors dynamically** based on time of day and day of week
- **Visualizes routes** on an interactive map with color-coded paths
- **Provides multiple optimization criteria**: Fastest, Safest, Cheapest routes
- **Allows weight tuning** via interactive sliders in the UI

## 🏗️ Project Structure

```
Dhaka_Path/
├── core/                          # Core application modules
│   ├── __init__.py
│   ├── graph_loader.py           # Load and manage road network graph
│   ├── risk_generator.py         # Generate and persist edge attributes
│   ├── cost_function.py          # Calculate route costs
│   ├── heuristics.py             # Heuristic functions for informed search
│   ├── search_algorithms.py      # All 10 search algorithms
│   └── route_optimizer.py        # Main orchestrator
├── ui/
│   └── streamlit_app.py          # Interactive web application
├── data/
│   ├── dhaka_road_graph.graphml  # Road network graph
│   └── risk_database.pkl         # Persistent risk data cache
├── main.py                        # Entry point script
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── venv/                          # Virtual environment

```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Windows/Linux/Mac

### Installation

1. **Navigate to project directory**:
   ```bash
   cd "d:\code\AI LAB\Dhaka_Path"
   ```

2. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Streamlit web app**:
   ```bash
   python main.py
   ```
   
   OR directly:
   ```bash
   streamlit run ui/streamlit_app.py
   ```

2. **Open in browser**:
   - Streamlit will open automatically or navigate to `http://localhost:8501`

## 📊 Edge Attributes (Risk Database)

Each edge in the road network has 16 attributes:

| Attribute | Type | Range | Description |
|-----------|------|-------|-------------|
| `traffic_factor` | Categorical | low/medium/high | Current congestion level |
| `is_holiday` | Boolean | True/False | Holiday or regular day |
| `gender_predominant` | Categorical | male/female/mixed | Safe for gender |
| `age_group` | Categorical | child/adult/elderly | Age group safety |
| `vehicle_types` | Categorical | Various | Permitted vehicles |
| `construction_work` | Boolean | True/False | Ongoing construction |
| `weather_condition` | Categorical | clear/rain/fog/storm | Current weather |
| `tolled_street` | Boolean | True/False | Toll required |
| `num_vehicles` | Integer | 1-50 | Current vehicle count |
| `street_width` | Float | Meters | Road width |
| `num_accidents_per_year` | Integer | 0-20 | Historical accidents |
| `num_police_boxes_500m` | Integer | 0-5 | Nearby police presence |
| `street_lighting` | Categorical | none/partial/full | Lighting quality |
| `road_surface_condition` | Categorical | poor/fair/good | Pavement quality |
| `peak_usage_time` | Categorical | morning/afternoon/evening/night | Peak usage period |
| `risk_factor` | Float | 0.0-1.0 | Composite risk score |

## 💡 Cost Function

The cost function combines multiple factors with adjustable weights:

```
Cost = w_risk × risk + w_traffic × traffic + w_surface × surface + 
        w_weather × weather + w_construction × construction + 
        w_toll × toll + w_width × width + w_time × time
```

**Weight Presets**:
- **Fastest**: Prioritizes travel time and low traffic
- **Safest**: Prioritizes risk reduction and safety infrastructure
- **Cheapest**: Prioritizes toll avoidance

**User Adjustable**: Sliders allow real-time weight modification

## 🔍 Search Algorithms

### Uninformed Search
- **BFS (Breadth-First Search)**: Explores level by level, shortest edge count
- **DFS (Depth-First Search)**: Memory efficient, explores deeply
- **UCS (Uniform Cost Search)**: Optimal cost, no heuristic guidance
- **DLS (Depth-Limited Search)**: DFS with depth limit to prevent infinite loops
- **IDLS (Iterative Deepening with Limit)**: IDS variant with adjustable depth limit
- **IDS (Iterative Deepening Search)**: Combines DFS efficiency with BFS completeness

### Informed Search
- **Greedy Best-First**: Fast but not optimal, uses heuristic only
- **A***: Optimal with admissible heuristic, best performance
- **Weighted A***: Customizable heuristic weight for speed/optimality tradeoff

## 📐 Heuristic Functions

All heuristics are **admissible** (guarantee optimal solution with A*):

### 1. Distance-Only Heuristic
- Uses Euclidean (straight-line) distance
- Admissible: straight-line ≤ actual path distance
- Fast to compute, conservative estimate

### 2. Risk-Weighted Heuristic
- Combines distance with average adjacent edge risk
- Formula: `distance × (1 + avg_risk)`
- Admissible: risk factor scales linearly with actual risks
- Better guidance for safety-aware routing

### 3. Composite Heuristic
- Incorporates distance, risk, traffic, and time-of-day
- Formula: `distance × (1 + 0.5×risk + 0.3×traffic) × time_multiplier`
- Most informative, still admissible
- Best search performance (fewest nodes expanded)

**Admissibility Property**: For each heuristic h(n):
- `h(n) ≤ actual_cost(n → goal)` for all nodes
- Guarantees A* finds optimal solution
- Ensures completeness

## 🎯 Features

### Interactive Configuration
- **Route Selection**: Choose source and destination nodes
- **Time Settings**: Select day of week and hour for dynamic factor adjustment
- **Traveler Info**: Specify vehicle type, gender, age group
- **Algorithm Selection**: Compare multiple algorithms simultaneously
- **Optimization Criteria**: Switch between fastest/safest/cheapest
- **Weight Adjustment**: Fine-tune cost function weights with sliders

### Visualization
- **Interactive Map**: Shows all found routes with color coding
  - Dark green: Best route
  - Light green shades: Alternative routes
- **Hover Popups**: Show algorithm names and route statistics
- **Start/End Markers**: Green start, red end

### Route Comparison
- **Ranking Table**: Sort routes by cost, distance, time, risk
- **Statistics**: Distance, travel time, risk factor, edges
- **Algorithm Info**: Performance metrics (nodes expanded)

### Detailed Analysis
- **Route Statistics**: Comprehensive metrics for each algorithm
- **Algorithm Documentation**: Information about each algorithm's properties
- **Heuristic Documentation**: Admissibility proofs and justifications

## ⏰ Time-Based Dynamics

The system adjusts factors based on selected time:

- **Traffic**: Increases during morning (7-10) and evening (16-20) rush hours
- **Risk**: Varies with visibility and activity levels
- **Safety**: Different during peak vs. off-peak hours
- **Holiday**: Weekend vs. weekday variations (Saturday/Sunday)

## 🎯 Optimization Criteria

### Fastest Route
- Minimizes travel time and traffic
- Prefers main roads and low-congestion paths

### Safest Route
- Minimizes risk factor
- Prefers well-lit, good condition roads with police presence
- Considers accident history

### Cheapest Route
- Minimizes toll usage
- Focuses on toll-free alternatives
- Secondary consideration for distance

## 💾 Data Persistence

- **Risk Database**: Saved as `data/risk_database.pkl`
- **Automatic Loading**: Persisted data loads on startup
- **One-Time Generation**: Edge attributes generated once, then cached
- **No Regeneration**: Subsequent runs use cached data for speed

## 📊 Output Information

Each route search returns:
- **Path**: List of node IDs representing the route
- **Cost**: Total composite cost value
- **Distance**: Total distance in meters
- **Travel Time**: Estimated minutes
- **Avg Risk**: Average risk factor along route
- **Statistics**: Comprehensive metrics
- **Nodes Expanded**: Algorithm efficiency metric

## 🔧 Customization

### Modify Cost Function
```python
weights = {
    'risk_factor': 0.3,
    'traffic_factor': 0.2,
    'road_surface': 0.15,
    # ... other weights
}
optimizer.update_cost_weights(weights)
```

### Add Custom Heuristic
Extend `core/heuristics.py` with new heuristic functions following the admissibility property.

### Adjust Edge Attributes
Modify `core/risk_generator.py` to change how attributes are generated or calculated.

## ⚙️ Technical Stack

- **Graph Processing**: NetworkX, OSMnx
- **Web Framework**: Streamlit
- **Visualization**: Folium, Plotly
- **Data Processing**: NumPy, Pandas
- **Geospatial**: GeoPandas, Shapely
- **Persistence**: Pickle

## 📝 Algorithm Complexity

| Algorithm | Time | Space | Optimal | Complete |
|-----------|------|-------|---------|----------|
| BFS | O(b^d) | O(b^d) | ✅* | ✅ |
| DFS | O(b^m) | O(bm) | ❌ | ⚠️ |
| UCS | O(b^(1+⌊C*/ε⌋)) | O(b^(1+⌊C*/ε⌋)) | ✅ | ✅ |
| DLS | O(b^d) | O(bd) | ❌ | ⚠️ |
| IDLS | O(b^d) | O(bd) | ❌ | ⚠️ |
| IDS | O(b^d) | O(bd) | ✅* | ✅ |
| Bidirectional | O(b^(d/2)) | O(b^(d/2)) | ✅* | ✅ |
| Greedy | O(b^m) | O(b^m) | ❌ | ✅ |
| A* | O(b^d) | O(b^d) | ✅ | ✅ |
| Weighted A* | O(b^d) | O(b^d) | ⚠️ | ✅ |

*Optimal in terms of edge count, not cost

## 🐛 Troubleshooting

### Virtual Environment Issues
```bash
# Recreate venv if needed
rmdir /s /q venv
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### Port Already in Use
```bash
streamlit run ui/streamlit_app.py --server.port 8502
```

### Missing GraphML File
Ensure `data/dhaka_road_graph.graphml` exists in the data directory.

### Slow Initial Startup
First run generates risk database for all edges (~30 seconds). Subsequent runs use cache.

## 📚 References

- **NetworkX Documentation**: https://networkx.org/
- **OSMnx Documentation**: https://osmnx.readthedocs.io/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **A* Pathfinding**: http://theory.stanford.edu/~amitp/GameProgramming/

## 👥 Author
AI Lab Project - Dhaka Path Route Optimization

## 📄 License
Educational use

---

**Happy Route Optimization! 🚀**
