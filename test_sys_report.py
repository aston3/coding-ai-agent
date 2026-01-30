import unittest
import json
from sys_report import generate_system_report
import datetime
import os

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

    def test_sensitive_env_vars_filtered(self):
        """Test that sensitive environment variables are filtered out"""
        # Set test environment variables
        os.environ['TEST_SECRET'] = 'secret_value'
        os.environ['AWS_ACCESS_KEY'] = 'fake_key'
        os.environ['SAFE_VAR'] = 'safe_value'
        
        report = generate_system_report()
        
        # Verify sensitive variables are filtered
        self.assertNotIn('TEST_SECRET', report['env_vars'])
        self.assertNotIn('AWS_ACCESS_KEY', report['env_vars'])
        
        # Verify safe variable remains
        self.assertIn('SAFE_VAR', report['env_vars'])
        
        # Cleanup
        del os.environ['TEST_SECRET']
        del os.environ['AWS_ACCESS_KEY']
        del os.environ['SAFE_VAR']

if __name__ == '__main__':
    unittest.main()