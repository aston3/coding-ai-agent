import os
import sys
import platform
import json
import datetime

def generate_system_report():
    """Collect system information and return as dictionary"""
    # Filter sensitive environment variable keys
    forbidden_substrings = ['SECRET', 'KEY', 'PASSWORD', 'TOKEN', 'CREDENTIAL']
    env_keys = [
        key for key in os.environ.keys()
        if not any(sub in key.upper() for sub in forbidden_substrings)
    ]
    
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "os_name": platform.system(),
        "os_release": platform.release(),
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "env_vars": env_keys
    }
    return report

if __name__ == "__main__":
    report = generate_system_report()
    print(json.dumps(report, indent=2))
