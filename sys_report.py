import os
import sys
import platform
import json
import datetime

def generate_system_report():
    """Collect system information and return as dictionary"""
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "os_name": platform.system(),
        "os_release": platform.release(),
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "env_vars": list(os.environ.keys())
    }
    return report

if __name__ == "__main__":
    report = generate_system_report()
    print(json.dumps(report))