import unittest
import subprocess
import json

class TestSystemReport(unittest.TestCase):
    def test_report_output(self):
        """Test if script produces valid JSON with expected keys"""
        result = subprocess.run(
            ['python', 'sys_report.py'],
            capture_output=True,
            text=True
        )
        
        # Verify script executed successfully
        self.assertEqual(result.returncode, 0, 
                         "Script execution failed")
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
            
        # Verify required fields exist
        required_keys = {
            'timestamp', 'os_name', 'os_release',
            'python_version', 'cwd', 'env_vars'
        }
        self.assertTrue(
            required_keys.issubset(data.keys()),
            "Missing required keys in report"
        )
        
        # Verify environment variables are stored as list
        self.assertIsInstance(
            data['env_vars'], list,
            "Environment variables should be stored as list"
        )

if __name__ == '__main__':
    unittest.main()