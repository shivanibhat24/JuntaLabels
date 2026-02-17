#!/usr/bin/env python3
"""
Main entry point for Sustainability Deception Detector
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gui.main_window import main

if __name__ == "__main__":
    print("="*70)
    print(" " * 10 + "🌍 SUSTAINABILITY DECEPTION DETECTOR 🌍")
    print("="*70)
    print("\n Detecting: Greenwashing • Brownwashing • Bluewashing\n")
    print(" Loading application...\n")
    
    main()
