import os
import sys

# fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("🚀 Running full pipeline...")

# Step 1: signals
os.system("python engine/bootstrap_signal_universe.py")

# Step 2: execution filtering
os.system("python engine/run_execution_selection.py")

# Step 3: symbol intelligence
os.system("python engine/run_symbol_intelligence.py")

print("✅ Pipeline complete.")
