import unittest
import json
from sys_report import generate_system_report
import datetime

class TestSystemReport(unittest.TestCase):
    def test_report_structure(self):
        """Test if report contains valid structure and data types"""
        data = generate_system_report()
        
        # Verify required fields exist
        required_keys = {
            'timestamp', 'os_name', 'os_release',
            'python_version', 'cwd', 'env_vars'
        }
        self.assertTrue(
            required_keys.issubset(data.keys()),
            "Missing required keys in report"
        )
        
        # Verify environment variables are stored as list of strings
        self.assertIsInstance(
            data['env_vars'], list,
            "Environment variables should be stored as list"
        )
        for var in data['env_vars']:
            self.assertIsInstance(var, str, f"Invalid env var type: {type(var)}")
            
        # Verify timestamp format (ISO 8601)
        try:
            datetime.datetime.fromisoformat(data['timestamp'])
        except ValueError:
            self.fail("Invalid timestamp format")
            
        # Verify python_version is string
        self.assertIsInstance(data['python_version'], str)
        
        # Verify cwd is non-empty string
        self.assertIsInstance(data['cwd'], str)
        self.assertTrue(len(data['cwd']) > 0)

if __name__ == '__main__':
    unittest.main()
