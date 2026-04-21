#!/usr/bin/env python
"""Quick test to verify risk database has real data"""

import sys
sys.path.insert(0, '.')

try:
    import pickle
    
    # Just load the risk database, not the full graph
    print('Loading risk database...')
    with open('data/risk_database.pkl', 'rb') as f:
        risk_data = pickle.load(f)
    
    print(f'\nTotal edges in database: {len(risk_data)}')
    
    if risk_data:
        # Show sample data
        print('\nSample edge attributes:')
        for edge_id, attrs in list(risk_data.items())[:3]:
            print(f'\n  Edge: {edge_id}')
            for k, v in attrs.items():
                print(f'    {k}: {v}')
        
        # Check variation
        print('\n\nData variation:')
        risk_factors = [attrs.get('risk_factor', 0) for attrs in risk_data.values()]
        print(f'  Risk factor range: {min(risk_factors):.3f} - {max(risk_factors):.3f}')
        print(f'  Unique traffic levels: {set(attrs.get("traffic_factor") for attrs in risk_data.values())}')
        print(f'  Edges with construction: {sum(1 for attrs in risk_data.values() if attrs.get("construction_work"))}')
        print(f'  Tolled edges: {sum(1 for attrs in risk_data.values() if attrs.get("tolled_street"))}')
        print(f'  Construction + tolled: {sum(1 for attrs in risk_data.values() if attrs.get("construction_work") and attrs.get("tolled_street"))}')
    else:
        print('Risk database is empty!')

except FileNotFoundError:
    print('Risk database not found at data/risk_database.pkl')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
