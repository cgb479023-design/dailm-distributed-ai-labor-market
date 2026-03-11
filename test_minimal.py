import sys
sys.path.append('.')
print("--- STARTING MINIMAL TEST ---")
try:
    from agents.matrix import ModelMatrix
    print("--- SUCCESS: MATRIX IMPORTED ---")
except Exception as e:
    print(f"--- FAILURE: {e} ---")
except:
    print("--- FATAL ERROR IN IMPORT ---")
