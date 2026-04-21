#!/usr/bin/env python3
"""
Quick Start Guide and Setup Verification
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up"""
    
    print("=" * 60)
    print("🔍 DHAKA ROUTE OPTIMIZER - SETUP VERIFICATION")
    print("=" * 60)
    
    # Check virtual environment
    print("\n1️⃣  Checking Virtual Environment...")
    venv_path = Path('venv')
    if venv_path.exists():
        print("   ✅ Virtual environment found")
    else:
        print("   ❌ Virtual environment NOT found")
        print("   👉 Run: python -m venv venv")
        return False
    
    # Check data directory
    print("\n2️⃣  Checking Data Directory...")
    data_path = Path('data')
    if data_path.exists():
        print("   ✅ Data directory found")
    else:
        print("   ❌ Data directory NOT found")
        return False
    
    # Check GraphML file
    print("\n3️⃣  Checking GraphML File...")
    graphml_path = Path('data/dhaka_road_graph.graphml')
    if graphml_path.exists():
        size_mb = graphml_path.stat().st_size / (1024*1024)
        print(f"   ✅ GraphML file found ({size_mb:.1f} MB)")
    else:
        print("   ❌ GraphML file NOT found")
        print("   👉 Ensure dhaka_road_graph.graphml is in data/ directory")
        return False
    
    # Check core modules
    print("\n4️⃣  Checking Core Modules...")
    modules = [
        'core/__init__.py',
        'core/graph_loader.py',
        'core/risk_generator.py',
        'core/cost_function.py',
        'core/heuristics.py',
        'core/search_algorithms.py',
        'core/route_optimizer.py',
    ]
    
    all_exist = True
    for module in modules:
        if Path(module).exists():
            print(f"   ✅ {module}")
        else:
            print(f"   ❌ {module}")
            all_exist = False
    
    if not all_exist:
        return False
    
    # Check UI
    print("\n5️⃣  Checking UI...")
    ui_path = Path('ui/streamlit_app.py')
    if ui_path.exists():
        print("   ✅ Streamlit app found")
    else:
        print("   ❌ Streamlit app NOT found")
        return False
    
    # Check requirements
    print("\n6️⃣  Checking Dependencies...")
    req_path = Path('requirements.txt')
    if req_path.exists():
        print("   ✅ requirements.txt found")
    else:
        print("   ❌ requirements.txt NOT found")
        return False
    
    # Try importing key modules
    print("\n7️⃣  Testing Python Imports...")
    try:
        import networkx as nx
        print("   ✅ networkx")
    except ImportError:
        print("   ❌ networkx - Install with: pip install networkx")
        return False
    
    try:
        import streamlit as st
        print("   ✅ streamlit")
    except ImportError:
        print("   ⚠️  streamlit - Will be needed for UI")
    
    return True


def print_quick_start():
    """Print quick start instructions"""
    
    print("\n" + "=" * 60)
    print("🚀 QUICK START INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1️⃣  ACTIVATE VIRTUAL ENVIRONMENT (if not already active):")
    print("   Windows: venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")
    
    print("\n2️⃣  INSTALL DEPENDENCIES (if needed):")
    print("   pip install -r requirements.txt")
    
    print("\n3️⃣  RUN THE APPLICATION:")
    print("   Option A: python main.py")
    print("   Option B: streamlit run ui/streamlit_app.py")
    
    print("\n4️⃣  OPEN IN BROWSER:")
    print("   http://localhost:8501")
    
    print("\n" + "=" * 60)
    print("📊 FEATURES TO TRY:")
    print("=" * 60)
    print("""
    1. Select source and destination nodes
    2. Choose date and time for dynamic factors
    3. Enter traveler information (vehicle, age, gender)
    4. Select multiple search algorithms to compare
    5. Choose optimization criteria (fastest, safest, cheapest)
    6. Adjust cost function weights with sliders
    7. View color-coded paths on the interactive map
    8. Hover over paths to see algorithm details
    9. Compare routes in statistics view
    10. Read algorithm and heuristic documentation
    """)


def main():
    """Main entry point"""
    
    print("\n")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check environment
    if check_environment():
        print("\n✅ ALL CHECKS PASSED! Environment is ready.")
        print_quick_start()
    else:
        print("\n❌ SETUP INCOMPLETE")
        print("Please fix the issues above and try again.")
        print("\nFor help, see README.md")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
