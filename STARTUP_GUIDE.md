# 🚀 Quick Start Guide - Dhaka Route Optimizer

## Before You Begin

Make sure you've run the setup verification:
```bash
python quickstart.py
```

All checks should pass with ✅ marks.

## Starting the Application

### Option 1: Using the launcher (Recommended)
```bash
python main.py
```

### Option 2: Direct Streamlit
```bash
streamlit run ui/streamlit_app.py
```

The application will open automatically in your browser at `http://localhost:8501`

---

## Using the Application

### Step 1: Configure Your Route
In the **left sidebar**, fill in:

1. **📍 Route Selection**
   - Select **Source Node ID** - starting point
   - Select **Destination Node ID** - ending point

2. **⏰ Time Settings**
   - Choose **Day of Week** (affects traffic patterns)
   - Choose **Hour of Day** (0-23, affects congestion)

3. **👤 Traveler Information**
   - **Vehicle Type**: car, motorcycle, bus, bicycle, rickshaw, truck
   - **Gender**: for safety considerations
   - **Age Group**: child, adult, elderly (affects route safety recommendations)

### Step 2: Select Algorithms
Choose one or more search algorithms to compare:
- **BFS** - Breadth-First Search (quickest result, but not optimal cost)
- **DFS** - Depth-First Search (memory efficient)
- **UCS** - Uniform Cost Search (finds lowest cost path)
- **DLS** - Depth-Limited Search (DFS with depth limit)
- **IDLS** - Iterative Deepening with Limit (IDS variant with adjustable depth)
- **IDS** - Iterative Deepening (combines efficiency with completeness)
- **Bidirectional** - Bidirectional Search (searches from both ends)
- **Greedy** - Greedy Best-First (fast, uses heuristic guidance)
- **A*** - A* Search (optimal with heuristic) ⭐ **RECOMMENDED**
- **Weighted A*** - Weighted A* Search (customizable optimality tradeoff)

**TIP**: A* usually finds the best routes

### Step 3: Set Optimization Criteria
Choose what to optimize for:

- **⚡ Fastest**: Minimize travel time and traffic
  - Best for commute routes
  - Prefers main roads and low-traffic paths

- **🛡️ Safest**: Minimize risk and maximize safety
  - Best for safety-conscious travelers
  - Considers accidents, lighting, police presence

- **💰 Cheapest**: Minimize tolls and overall cost
  - Best for budget-conscious travel
  - Avoids toll roads when possible

### Step 4: Adjust Cost Weights (Optional)
Click **"Adjust Weights"** expander to fine-tune:
- Risk Factor
- Traffic Factor
- Road Surface
- Weather Condition
- Construction Work
- Toll Factor
- Street Width
- Travel Time

**TIP**: Default weights are optimized for balanced routing

### Step 5: Find Routes
Click **"🚀 Find Routes"** button

The system will run all selected algorithms and find the best paths.

---

## Viewing Results

### 📍 Map View (Tab 1)
- **Color-coded paths** on interactive map:
  - 🟢 **Dark Green** = Best route (Rank #1)
  - 🟢 **Light Green** = Alternative routes
  
- **Hover over paths** to see:
  - Algorithm name
  - Total cost
  - Distance
  - Travel time
  - Average risk factor

- **Green marker** = Start
- **Red marker** = End

### 📊 Route Comparison (Tab 2)
- Table showing all routes ranked by cost
- Sort by: Cost, Distance, Travel Time, or Risk
- Filter by algorithm
- Compare efficiency metrics

### 📈 Statistics (Tab 3)
- **Best Route Summary** with key metrics
- **Detailed stats** for each algorithm:
  - Total distance (km)
  - Estimated travel time (minutes)
  - Average risk factor
  - Number of edges traversed
  - Nodes expanded (algorithm efficiency)

### 📚 Algorithm Info (Tab 4)
- **Algorithm descriptions** and properties
  - Optimality: Does it guarantee best path?
  - Completeness: Will it find a path if one exists?
  - Speed: How many nodes must it explore?

- **Heuristic documentation**:
  - How each heuristic works
  - Admissibility proofs
  - When to use each one

---

## Understanding the Results

### What Each Metric Means

**Cost**: Composite weighted score combining all factors (0.0 = best)

**Distance**: Total length of the route in meters/kilometers

**Travel Time**: Estimated time needed (minutes) at current traffic levels

**Avg Risk Factor**: Average safety score (0.0 = safest, 1.0 = most risky)
- Considers: accidents, weather, lighting, construction

**Nodes Expanded**: How many intersections the algorithm had to consider
- Lower = more efficient algorithm

### Reading the Map

The best route is shown in the **darkest green**. Alternative routes get progressively lighter.

All paths have the same start (green marker) and end (red marker).

The difference in color tells you which algorithm found the best route.

---

## Tips & Tricks

### Choose the Right Algorithm

| Situation | Best Algorithm |
|-----------|---|
| Shortest cost | A* ⭐ |
| Exploration/Learning | BFS or DFS |
| Budget optimization | Greedy (fast but not optimal) |
| Safety priority | A* with "Safest" criteria |
| Time priority | A* with "Fastest" criteria |

### Time-Based Optimization

- **Morning (7-10 AM)**: Rush hour, high traffic
- **Afternoon (10-4 PM)**: Normal traffic
- **Evening (4-8 PM)**: Rush hour, high traffic
- **Night (8 PM-7 AM)**: Low traffic

Pick the right time to see how routes change!

### Safety Considerations

- Female travelers: System marks safer routes
- Child travelers: Prefers well-lit, lower-traffic routes
- Elderly travelers: Prefers easier routes with less traffic

### Vehicle Restrictions

Some roads may not permit certain vehicles (e.g., rickshaws on highways).
The system automatically respects these when routing.

---

## Common Questions

**Q: Why do different algorithms give different routes?**
A: Uninformed algorithms (BFS, DFS) don't know about cost. Informed algorithms (A*, Greedy) use heuristics to guide search toward the best route.

**Q: Why is A* usually the best?**
A: A* combines actual cost with heuristic guidance, exploring fewer nodes while guaranteeing optimal path (if heuristic is admissible).

**Q: What's the difference between "Safest" and "Cheapest"?**
A: Safest minimizes risk (considers accidents, weather, lighting). Cheapest minimizes tolls and distance cost.

**Q: Why are weights adjustable?**
A: Different people prioritize different factors. Business travelers might value time. Budget travelers value tolls. Safety-conscious users value risk reduction.

**Q: How is risk calculated?**
A: Risk combines: historical accidents, road condition, lighting, weather, construction, traffic levels, and other safety factors.

---

## Troubleshooting

**Q: No paths found?**
A: Try different nodes or check if start and destination are actually connected. Use BFS first to verify connectivity.

**Q: Streamlit app won't start?**
A: Run `python quickstart.py` to verify setup. Then try:
```bash
streamlit run ui/streamlit_app.py --server.port 8502
```

**Q: App is slow first time?**
A: The first run generates the risk database for all edges (~1-2 minutes). Subsequent runs use the cache and are much faster.

**Q: Nodes not showing?**
A: The GraphML file might not have loaded properly. Check `data/dhaka_road_graph.graphml` exists (should be ~124 MB).

---

## File Structure for Reference

```
Key files you might interact with:
├── main.py                    ← Run this to start
├── ui/streamlit_app.py        ← The web interface
├── data/
│   ├── dhaka_road_graph.graphml
│   └── risk_database.pkl      ← Auto-generated cache
├── core/                      ← Algorithm implementations
│   ├── route_optimizer.py     ← Main logic
│   ├── search_algorithms.py   ← All 10 algorithms
│   └── ...
└── README.md                  ← Full technical docs
```

---

## Need Help?

1. **Setup issues**: Run `python quickstart.py`
2. **Functional issues**: Run `python test_system.py`
3. **Documentation**: Read `README.md`
4. **Algorithm questions**: See "📚 Algorithm Info" tab in app

---

**Happy routing! 🗺️🚗**

*Powered by NetworkX, OSMnx, and Streamlit*
