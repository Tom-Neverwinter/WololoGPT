import os
import datetime
import pyautogui

# Assuming ai_analysis.py and config.py exist in the same directory or are accessible
# For example, if they are in the same package:
from ai_analysis import AIAnalysis
from config import AI_CONFIG, RESOURCE_CHECK_PROMPT, CIV_COUNTER_PROMPT
from utils import logger # Assuming logger is exposed in utils.py

class ScreenshotManager:
    """Manages taking and analyzing screenshots."""

    @staticmethod
    def take_civ_screenshot():
        """
        Takes a screenshot, saves it to the 'screenshots/civs/' directory,
        and logs the path.
        """
        try:
            screenshot_dir = os.path.join("screenshots", "civs")
            os.makedirs(screenshot_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_civ_{timestamp}.jpg"
            filepath = os.path.join(screenshot_dir, filename)

            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            logger.info(f"Civilization screenshot saved to: {filepath}")
            return filepath
        except ImportError:
            logger.error("pyautogui is not installed. Please install it to use screenshot functionality.")
            return None
        except Exception as e:
            logger.error(f"Error taking civilization screenshot: {str(e)}")
            return None

    @staticmethod
    def analyze_resource_screenshot(screenshot_path):
        """Analyze a resource screenshot using AI Analysis."""
        if not screenshot_path:
            logger.error("No screenshot path provided for resource analysis.")
            return None
        try:
            # Use default image model from config
            model_name = AI_CONFIG["default_models"]["image"]
            
            logger.info(f"Analyzing resource screenshot '{screenshot_path}' with {model_name}...")
            # Assuming AIAnalysis.analyze_image_ollama is the correct method
            result = AIAnalysis.analyze_image_ollama(screenshot_path, RESOURCE_CHECK_PROMPT, model_name)
            
            return result
        except KeyError:
            logger.error("AI_CONFIG is missing 'default_models' or 'image' key.")
            return None
        except Exception as e:
            logger.error(f"Error analyzing resource screenshot '{screenshot_path}': {str(e)}")
            return None

    @staticmethod
    def analyze_civ_screenshot(screenshot_path):
        """Analyze a civilization screenshot using AI Analysis."""
        if not screenshot_path:
            logger.error("No screenshot path provided for civ analysis.")
            return None
        try:
            # Use default image model from config
            model_name = AI_CONFIG["default_models"]["image"]
            
            logger.info(f"Analyzing civilization screenshot '{screenshot_path}' with {model_name}...")
            # Assuming AIAnalysis.analyze_civ_screenshot is the correct method
            # Based on original code, it seems it was AIAnalysis.analyze_civ_screenshot itself
            result = AIAnalysis.analyze_civ_screenshot(screenshot_path, model_name, CIV_COUNTER_PROMPT)
            
            return result
        except KeyError:
            logger.error("AI_CONFIG is missing 'default_models' or 'image' key.")
            return None
        except Exception as e:
            logger.error(f"Error analyzing civilization screenshot '{screenshot_path}': {str(e)}")
            return None

if __name__ == '__main__':
    # Example usage (requires dummy files/classes for AIAnalysis and config)
    # Create dummy ai_analysis.py
    # class AIAnalysis:
    #     @staticmethod
    #     def analyze_image_ollama(path, prompt, model):
    #         print(f"DUMMY: Analyzing image {path} with prompt '{prompt}' using {model}")
    #         return "Dummy resource analysis result"
    #     @staticmethod
    #     def analyze_civ_screenshot(path, model, prompt):
    #         print(f"DUMMY: Analyzing civ screenshot {path} with prompt '{prompt}' using {model}")
    #         return "Dummy civ analysis result"

    # Create dummy config.py
    # AI_CONFIG = {"default_models": {"image": "dummy_model"}}
    # RESOURCE_CHECK_PROMPT = "Is this a resource?"
    # CIV_COUNTER_PROMPT = "What civ is this and what are its counters?"

    # Create dummy utils.py with a logger
    # import logging
    # logger = logging.getLogger(__name__)
    # logger.setLevel(logging.INFO)
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    
    # To run this example, you'd need to ensure these dummy files are created
    # or the actual files are in place.
    # For the purpose of this tool, only the main class structure is important.

    # Test take_civ_screenshot
    civ_screenshot_path = ScreenshotManager.take_civ_screenshot()
    if civ_screenshot_path:
        print(f"Civ screenshot taken: {civ_screenshot_path}")
        # Test analyze_civ_screenshot
        # analysis_result = ScreenshotManager.analyze_civ_screenshot(civ_screenshot_path)
        # print(f"Civ analysis result: {analysis_result}")


    # To test analyze_resource_screenshot, you'd need a dummy image file
    # dummy_resource_path = "dummy_resource_screenshot.jpg"
    # with open(dummy_resource_path, "w") as f:
    # with open(dummy_resource_path, "w") as f:
    #     f.write("dummy image data") # Create a dummy file
    # resource_analysis_result = ScreenshotManager.analyze_resource_screenshot(dummy_resource_path)
    # print(f"Resource analysis result: {resource_analysis_result}")
    pass
