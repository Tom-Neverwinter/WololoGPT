import unittest
from unittest.mock import patch, MagicMock
import time
import json # Ensure json is imported for json.JSONDecodeError

# Adjust imports based on your project structure.
# This assumes resource_alerts_thread.py, ai_analysis.py, etc., are discoverable.
# You might need to add `sys.path.append('..')` or similar if running tests directly from tests/
# For a proper package, this might not be needed if tests are run with `python -m unittest discover`
import sys
import os
# Add project root to sys.path to allow importing project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from resource_alerts_thread import ResourceAlertsThread
from ai_analysis import AIAnalysis # To mock its methods
from screenshot_manager import ScreenshotManager # To mock its methods
from utils import logger # To check if logger.error was called

class TestResourceAlertsThread(unittest.TestCase):

    @patch('resource_alerts_thread.ScreenshotManager.take_resource_screenshot')
    @patch('resource_alerts_thread.AIAnalysis.analyze_image_gemini')
    @patch('resource_alerts_thread.logger.error') # Mocking logger.error
    @patch('resource_alerts_thread.AudioManager.play_audio') # Mock to prevent actual audio
    @patch.object(ResourceAlertsThread, 'check_house_limit') # Mock other checks
    @patch.object(ResourceAlertsThread, 'check_villager_count')
    @patch.object(ResourceAlertsThread, 'check_floating_resources')
    @patch.object(ResourceAlertsThread, 'check_idle_villagers')
    def test_run_handles_non_json_response(self,
                                          mock_check_idle_villagers,
                                          mock_check_floating_resources,
                                          mock_check_villager_count,
                                          mock_check_house_limit,
                                          mock_play_audio,
                                          mock_logger_error,
                                          mock_analyze_image,
                                          mock_take_screenshot):

        # --- Setup Mocks ---
        mock_take_screenshot.return_value = "dummy_screenshot_path.png"
        
        # Simulate AIAnalysis returning a non-JSON error string
        error_response_string = "Error: Ollama not available or model failed to load."
        mock_analyze_image.return_value = error_response_string
        
        # --- Initialize and Run Thread ---
        api_key = "test_api_key"
        thread = ResourceAlertsThread(api_key)
        thread.running = True # Set running to True to enter the loop

        # We want the thread's run method to execute a few times and then stop.
        # To do this, we can patch time.sleep to raise an exception after N calls,
        # or make analyze_image_gemini set thread.running to False after a call.
        
        # Let's make mock_analyze_image stop the thread after the first call for this test
        def side_effect_stop_thread(*args, **kwargs):
            thread.running = False # Stop the thread after this call
            return error_response_string
        mock_analyze_image.side_effect = side_effect_stop_thread

        thread.start() # Start the thread
        thread.join(timeout=5) # Wait for the thread to finish (or timeout)

        if thread.is_alive():
            # If thread is still alive, something went wrong, force stop it.
            thread.running = False
            thread.join()
            self.fail("Thread did not terminate as expected.")

        # --- Assertions ---
        # 1. AIAnalysis.analyze_image_gemini was called
        mock_analyze_image.assert_called_once_with("dummy_screenshot_path.png", unittest.mock.ANY, api_key)

        # 2. logger.error was called due to JSONDecodeError
        #    The actual ResourceAlertsThread should catch json.JSONDecodeError
        #    and log the error_response_string.
        #    The log message format in ResourceAlertsThread is:
        #    f"Failed to parse AI analysis response as JSON. Response: '{resources}'. Error: {e}"
        
        # Check if logger.error was called.
        self.assertTrue(mock_logger_error.called)
        
        # Check the content of the log call.
        # We expect a log message containing the error_response_string and mentioning JSONDecodeError.
        found_correct_log = False
        for call_args in mock_logger_error.call_args_list:
            log_message = call_args[0][0] # First argument of the call
            if error_response_string in log_message and "Failed to parse AI analysis response as JSON" in log_message:
                found_correct_log = True
                break
        self.assertTrue(found_correct_log, f"Expected log message not found. Actual calls: {mock_logger_error.call_args_list}")
        
        # 3. Ensure other processing methods (like check_house_limit) were NOT called
        #    because the JSON parsing should have failed and the loop continued.
        mock_check_house_limit.assert_not_called()
        mock_check_villager_count.assert_not_called()
        mock_check_floating_resources.assert_not_called()
        mock_check_idle_villagers.assert_not_called()

if __name__ == '__main__':
    unittest.main()
