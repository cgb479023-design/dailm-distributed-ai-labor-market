import subprocess
import os
import sys

def run_test_module(module_path, log_file):
    print(f"Running {module_path}...")
    try:
        # Use venv python if available
        python_exe = os.path.join("venv", "Scripts", "python.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable
        
        result = subprocess.run(
            [python_exe, "-m", "unittest", module_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60 # Prevent hanging
        )
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"=== TEST MODULE: {module_path} ===\n")
            f.write(f"STDOUT:\n{result.stdout}\n")
            f.write(f"STDERR:\n{result.stderr}\n")
            f.write(f"EXIT CODE: {result.returncode}\n\n")
        
        return result.returncode == 0
    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"ERROR RUNNING {module_path}: {e}\n")
        return False

def run_script(script_path, log_file):
    print(f"Running script {script_path}...")
    try:
        python_exe = os.path.join("venv", "Scripts", "python.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable
            
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120 # E2E needs more time
        )
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"=== TEST SCRIPT: {script_path} ===\n")
            f.write(f"STDOUT:\n{result.stdout}\n")
            f.write(f"STDERR:\n{result.stderr}\n")
            f.write(f"EXIT CODE: {result.returncode}\n\n")
        
        return result.returncode == 0
    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"ERROR RUNNING {script_path}: {e}\n")
        return False

if __name__ == "__main__":
    log_file = "verification_results.log"
    # Clear log file
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("--- DAILM AUTOMATED VERIFICATION START ---\n")
    
    test_modules = ["tests/test_planner.py", "tests/test_patent_logic.py"]
    test_scripts = ["tests/e2e_resurrection_test.py"]
    
    all_passed = True
    for mod in test_modules:
        if not run_test_module(mod, log_file):
            all_passed = False
            
    for script in test_scripts:
        if not run_script(script, log_file):
            all_passed = False
            
    if all_passed:
        print("ALL TESTS PASSED.")
    else:
        print("SOME TESTS FAILED. CHECK verification_results.log")
