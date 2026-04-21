# Pathfinding Comparison: Fastest vs Safest vs Cheapest

## 🔄 **How A* Works with Different Criteria**

### **A* Formula: f(n) = g(n) + h(n)**
- **f(n)**: Total evaluation score
- **g(n)**: Actual cost from start to current node (**THIS CHANGES**)
- **h(n)**: Heuristic estimate to goal (**THIS STAYS SAME**)

---

## 📊 **Weight Priority Comparison**

| Component | Fastest | Safest | Cheapest | Description |
|-----------|---------|--------|----------|-------------|
| **Travel Time** | 🔴 40% | 🟢 5% | 🟡 10% | Speed-based travel duration |
| **Traffic Factor** | 🔴 35% | 🟡 15% | 🟡 10% | Congestion level penalty |
| **Risk Factor** | 🟢 5% | 🔴 35% | 🟡 10% | Safety/accident risk |
| **Road Surface** | 🟢 5% | 🟡 15% | 🟢 5% | Road condition quality |
| **Weather** | 🟢 5% | 🟡 10% | 🟢 5% | Weather impact on safety |
| **Construction** | 🟢 5% | 🟡 10% | 🟢 5% | Construction work penalty |
| **Toll Roads** | ⚪ 0% | ⚪ 0% | 🔴 50% | Monetary cost of tolls |
| **Street Width** | 🟢 5% | 🟡 10% | 🟢 5% | Narrow road penalty |

**Legend**: 🔴 High Priority | 🟡 Medium Priority | 🟢 Low Priority | ⚪ Ignored

---

## 🛣️ **Example Scenario Analysis**

### **Road Segment Properties:**
```
Distance: 2 km
Traffic: Heavy (high)
Weather: Rainy  
Surface: Poor condition
Has toll: Yes ($2)
Risk level: High (0.8)
Width: Narrow (4m)
```

### **Cost Calculations:**

#### **🏃 FASTEST Route:**
```
Prioritizes: Speed + Low Traffic
Result: Avoids this segment (high traffic + poor surface = slow)
Alternative: Takes highway even if longer distance
Reasoning: "I don't care about tolls or risk, just get me there fast"
```

#### **🛡️ SAFEST Route:**  
```
Prioritizes: Low Risk + Good Infrastructure
Result: Definitely avoids this segment (high risk + poor surface + narrow)
Alternative: Takes well-lit main roads with good surface
Reasoning: "I don't care about time or cost, just get me there safely"
```

#### **💰 CHEAPEST Route:**
```
Prioritizes: No Tolls + Low Cost
Result: Might use this segment despite issues (no toll penalty)
Alternative: Avoids highways and toll roads
Reasoning: "I don't care about time or risk, just save money"
```

---

## 🧮 **Numerical Example**

### **Same Edge, Different Costs:**

| Criteria | Risk×Weight | Traffic×Weight | Toll×Weight | Time×Weight | **Total Cost** |
|----------|-------------|----------------|-------------|-------------|----------------|
| **Fastest** | 0.8×0.05=0.04 | 0.9×0.35=0.315 | 0.3×0.00=0 | 0.8×0.40=0.32 | **0.675** |
| **Safest** | 0.8×0.35=0.28 | 0.9×0.15=0.135 | 0.3×0.00=0 | 0.8×0.05=0.04 | **0.455** |
| **Cheapest** | 0.8×0.10=0.08 | 0.9×0.10=0.09 | 0.3×0.50=0.15 | 0.8×0.10=0.08 | **0.40** |

### **A* Evaluation (f = g + h):**
```
Assuming heuristic h = 500m (straight-line distance to goal)

Fastest:  f = 0.675 + 500 = 500.675
Safest:   f = 0.455 + 500 = 500.455  
Cheapest: f = 0.40 + 500 = 500.40
```

**Result**: Cheapest will explore this edge first, Safest second, Fastest last.

---

## 🎯 **Path Selection Logic**

### **FASTEST Algorithm Thinking:**
```
"This edge has heavy traffic and poor surface → very slow travel time
→ high cost (0.675) → explore other options first
→ prefer highways even if they have tolls"
```

### **SAFEST Algorithm Thinking:**  
```
"This edge has high risk and poor conditions → dangerous
→ medium cost (0.455) → explore safer alternatives first
→ prefer well-maintained roads with good lighting"
```

### **CHEAPEST Algorithm Thinking:**
```
"This edge has no tolls → saves money
→ low cost (0.40) → explore this option first  
→ avoid highways and toll roads even if slower/riskier"
```

---

## 🔍 **Heuristic Behavior (Same for All)**

### **Available Heuristics:**
1. **Euclidean**: `h = √[(x₂-x₁)² + (y₂-y₁)²]`
2. **Manhattan**: `h = |x₂-x₁| + |y₂-y₁|`  
3. **Conservative**: `h = 0.9 × Euclidean`
4. **Zero**: `h = 0` (A* becomes UCS)

### **Why Heuristics Don't Change:**
- Heuristics estimate **remaining distance**, not **travel preferences**
- They must be **admissible** (never overestimate) for A* optimality
- User preferences are captured in the **actual cost function** (g), not heuristic (h)

---

## 🚀 **Real-World Impact**

### **Fastest Route Characteristics:**
- ✅ Uses highways and expressways
- ✅ Avoids traffic-congested areas  
- ✅ Prioritizes high-speed roads
- ❌ May use toll roads
- ❌ May use riskier but faster routes

### **Safest Route Characteristics:**
- ✅ Uses well-lit main roads
- ✅ Avoids high-crime areas
- ✅ Prefers good road conditions
- ❌ May take longer routes
- ❌ May use toll roads for safety

### **Cheapest Route Characteristics:**  
- ✅ Avoids all toll roads
- ✅ Minimizes fuel costs (shorter distance)
- ✅ Uses free local roads
- ❌ May be slower
- ❌ May be less safe

This system gives users **true choice** in their routing preferences while maintaining **mathematical optimality** through A* search!