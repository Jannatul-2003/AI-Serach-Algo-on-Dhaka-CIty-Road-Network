#!/usr/bin/env python3
"""
Main entry point for Dhaka Road Network Route Optimizer
Run this script to start the Streamlit web application
"""

import subprocess
import sys
import os

def main():
    """Start the Streamlit application"""
    
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    streamlit_app = os.path.join(current_dir, 'ui', 'streamlit_app.py')
    
    # Run Streamlit app
    subprocess.run([
        sys.executable, '-m', 'streamlit', 'run',
        streamlit_app,
        '--logger.level=info'
    ])

if __name__ == '__main__':
    main()
