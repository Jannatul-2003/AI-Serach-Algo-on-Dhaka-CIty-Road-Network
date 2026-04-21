# Cost Calculation Explanation: Fastest vs Safest vs Cheapest

## 🎯 Overview

The pathfinding system uses different **weight distributions** to optimize for different criteria. Here's how **evaluation plan**, **actual cost**, and **heuristic** are calculated for each:

**IMPORTANT**: Distance is now a **fundamental component** of actual cost, representing fuel consumption, vehicle wear, and base travel cost.

---

## 📊 **1. FASTEST Path Finding**

### **Weight Distribution:**
```python
'distance': 0.10         # Low priority (10%) - willing to go longer for speed
'risk_factor': 0.05      # Very low priority (5%)
'traffic_factor': 0.35   # High priority (35%) 
'road_surface': 0.05     # Low priority (5%)
'weather': 0.05          # Low priority (5%)
'construction': 0.05     # Low priority (5%)
'toll': 0.00             # Ignored (0%)
'street_width': 0.05     # Low priority (5%)
'travel_time': 0.30      # High priority (30%)
```

### **Actual Cost Calculation:**
```
Edge Cost = (0.10 × distance) + (0.05 × risk) + (0.35 × traffic) + 
            (0.05 × surface) + (0.05 × weather) + (0.05 × construction) + 
            (0.00 × toll) + (0.05 × width_penalty) + (0.30 × travel_time)
```

### **Distance Component (10% weight):**
```python
# Normalize distance to 0-1 scale (max 5km per edge)
max_edge_distance = 5000.0  # meters
distance_cost = min(distance / max_edge_distance, 1.0)

# Example: 1000m edge → distance_cost = 1000/5000 = 0.2
# With 10% weight: 0.10 × 0.2 = 0.02 cost contribution
```

---

## 🛡️ **2. SAFEST Path Finding**

### **Weight Distribution:**
```python
'distance': 0.15         # Moderate priority (15%) - some distance consideration
'risk_factor': 0.30      # Highest priority (30%)
'traffic_factor': 0.15   # Medium priority (15%)
'road_surface': 0.15     # Medium priority (15%)
'weather': 0.10          # Medium priority (10%)
'construction': 0.10     # Medium priority (10%)
'toll': 0.00             # Ignored (0%)
'street_width': 0.05     # Low priority (5%)
'travel_time': 0.00      # Ignored (0%) - safety over speed
```

### **Actual Cost Calculation:**
```
Edge Cost = (0.15 × distance) + (0.30 × risk) + (0.15 × traffic) + 
            (0.15 × surface) + (0.10 × weather) + (0.10 × construction) + 
            (0.00 × toll) + (0.05 × width_penalty) + (0.00 × travel_time)
```

---

## 💰 **3. CHEAPEST Path Finding**

### **Weight Distribution:**
```python
'distance': 0.35         # Highest priority (35%) - fuel cost is major factor
'risk_factor': 0.05      # Low priority (5%)
'traffic_factor': 0.10   # Low priority (10%)
'road_surface': 0.05     # Very low priority (5%)
'weather': 0.05          # Very low priority (5%)
'construction': 0.05     # Very low priority (5%)
'toll': 0.30             # High priority (30%) - avoid monetary costs
'street_width': 0.03     # Very low priority (3%)
'travel_time': 0.02      # Very low priority (2%)
```

### **Actual Cost Calculation:**
```
Edge Cost = (0.35 × distance) + (0.05 × risk) + (0.10 × traffic) + 
            (0.05 × surface) + (0.05 × weather) + (0.05 × construction) + 
            (0.30 × toll) + (0.03 × width_penalty) + (0.02 × travel_time)
```

### **Why Distance is 35% for Cheapest:**
- **Fuel consumption**: Longer distances = more fuel = higher cost
- **Vehicle wear**: More kilometers = more maintenance cost
- **Time cost**: Even if time isn't prioritized, longer trips cost more
- **Efficiency**: Shortest distance often means most economical

---

### **Travel Time Component (40% weight):**
```python
# Speed based on traffic level
speed_map = {
    'low': 15 m/s,     # ~54 km/h
    'medium': 10 m/s,  # ~36 km/h  
    'high': 5 m/s      # ~18 km/h
}

# Adjust for road surface
surface_multiplier = {
    'poor': 0.6,   # 60% of base speed
    'fair': 0.8,   # 80% of base speed
    'good': 1.0    # 100% of base speed
}

actual_speed = base_speed × surface_multiplier
travel_time = distance / actual_speed
normalized_time = min(travel_time / 300.0, 1.0)  # Max 5 minutes
```

### **Heuristic (Same for all criteria):**
- **Euclidean Distance**: Straight-line distance in meters
- **Manhattan Distance**: Grid-based distance  
- **Conservative**: 90% of Euclidean distance
- **Zero**: Always returns 0 (A* becomes UCS)

**Note**: Heuristics are **admissible** and don't change based on optimization criteria. Only the **actual cost** changes.

---

## 🛡️ **2. SAFEST Path Finding**

### **Weight Distribution:**
```python
'risk_factor': 0.35      # Highest priority (35%)
'traffic_factor': 0.15   # Medium priority (15%)
'road_surface': 0.15     # Medium priority (15%)
'weather': 0.10          # Medium priority (10%)
'construction': 0.10     # Medium priority (10%)
'toll': 0.00             # Ignored (0%)
'street_width': 0.10     # Medium priority (10%)
'travel_time': 0.05      # Very low priority (5%)
```

### **Actual Cost Calculation:**
```
Edge Cost = (0.35 × risk) + (0.15 × traffic) + (0.15 × surface) + 
            (0.10 × weather) + (0.10 × construction) + (0.00 × toll) + 
            (0.10 × width_penalty) + (0.05 × travel_time)
```

### **Risk Factor Component (35% weight):**
```python
# Base risk factors
risk = 0.0
risk += traffic_risk      # 0.05-0.30 based on traffic level
risk += weather_risk      # 0.0-0.20 based on weather
risk += construction_risk # 0.15 if construction present
risk += surface_risk      # 0.02-0.15 based on road condition
risk += accident_risk     # Based on historical accidents
risk += lighting_risk     # 0.0-0.10 based on street lighting
risk += vehicle_density   # Based on number of vehicles
risk += narrow_road_risk  # Higher risk for narrow roads
risk -= police_presence   # Reduces risk if police nearby

final_risk = max(0.0, min(risk, 1.0))  # Clamp to [0,1]
```

---

## 💰 **3. CHEAPEST Path Finding**

### **Weight Distribution:**
```python
'risk_factor': 0.10      # Low priority (10%)
'traffic_factor': 0.10   # Low priority (10%)
'road_surface': 0.05     # Very low priority (5%)
'weather': 0.05          # Very low priority (5%)
'construction': 0.05     # Very low priority (5%)
'toll': 0.50             # Highest priority (50%)
'street_width': 0.05     # Very low priority (5%)
'travel_time': 0.10      # Low priority (10%)
```

### **Actual Cost Calculation:**
```
Edge Cost = (0.10 × risk) + (0.10 × traffic) + (0.05 × surface) + 
            (0.05 × weather) + (0.05 × construction) + (0.50 × toll) + 
            (0.05 × width_penalty) + (0.10 × travel_time)
```

### **Toll Component (50% weight):**
```python
toll_cost = 0.3 if edge_attributes.get('tolled_street', False) else 0.0
# If road has tolls, adds 0.3 to the cost
# With 50% weight: 0.50 × 0.3 = 0.15 penalty for toll roads
```

---

## 🔍 **Detailed Cost Components**

### **Traffic Factor:**
```python
traffic_map = {
    'low': 0.1,     # 10% cost penalty
    'medium': 0.5,  # 50% cost penalty  
    'high': 0.9     # 90% cost penalty
}
# Adjusted by vehicle count
vehicle_factor = min(num_vehicles / 50.0, 1.0)
final_traffic_cost = base_cost + (vehicle_factor × 0.1)
```

### **Weather Factor:**
```python
weather_map = {
    'clear': 0.0,   # No penalty
    'rain': 0.3,    # 30% penalty
    'fog': 0.5,     # 50% penalty
    'storm': 0.9    # 90% penalty
}
```

### **Road Surface Factor:**
```python
surface_map = {
    'poor': 0.8,    # 80% penalty
    'fair': 0.4,    # 40% penalty
    'good': 0.1     # 10% penalty
}
```

---

## 🧮 **Example Calculation**

### **Scenario**: Edge with following attributes:
- **Distance: 1000m**
- Traffic: 'high' 
- Weather: 'rain'
- Surface: 'fair'
- Has toll: Yes
- Risk factor: 0.6

### **Distance Cost Calculation:**
```
distance_cost = min(1000 / 5000, 1.0) = 0.2
```

### **FASTEST Calculation:**
```
travel_time = 1000m / 5m/s = 200s → normalized = 200/300 = 0.67
Edge Cost = (0.10×0.2) + (0.05×0.6) + (0.35×0.9) + (0.05×0.4) + 
            (0.05×0.3) + (0.05×0.0) + (0.00×0.3) + (0.05×0.2) + (0.30×0.67)
          = 0.02 + 0.03 + 0.315 + 0.02 + 0.015 + 0 + 0 + 0.01 + 0.201
          = 0.611
```

### **SAFEST Calculation:**
```
Edge Cost = (0.15×0.2) + (0.30×0.6) + (0.15×0.9) + (0.15×0.4) + 
            (0.10×0.3) + (0.10×0.0) + (0.00×0.3) + (0.05×0.2) + (0.00×0.67)
          = 0.03 + 0.18 + 0.135 + 0.06 + 0.03 + 0 + 0 + 0.01 + 0
          = 0.445
```

### **CHEAPEST Calculation:**
```
Edge Cost = (0.35×0.2) + (0.05×0.6) + (0.10×0.9) + (0.05×0.4) + 
            (0.05×0.3) + (0.05×0.0) + (0.30×0.3) + (0.03×0.2) + (0.02×0.67)
          = 0.07 + 0.03 + 0.09 + 0.02 + 0.015 + 0 + 0.09 + 0.006 + 0.0134
          = 0.3044
```

---

## 🎯 **Key Insights**

1. **Heuristic is the same** for all criteria - only **actual cost** changes
2. **Fastest** heavily penalizes slow roads and traffic congestion
3. **Safest** heavily penalizes risky conditions and poor infrastructure  
4. **Cheapest** heavily penalizes toll roads and optimizes for cost
5. **A* evaluation**: f(n) = g(n) + h(n) where g(n) uses the weighted cost above

This system allows the same search algorithm (A*) to find different optimal paths based on what the user values most!