import pyautogui
import datetime
import os
from config import RESOURCE_SCREENSHOT_REGION, CIV_SCREENSHOT_REGION
from PIL import Image
import time
from utils import logger

class ScreenshotManager:
    @staticmethod
    def take_resource_screenshot():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.jpg"
        screenshots_dir = os.path.join("screenshots", "resources")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, filename)
        
        try:
            screenshot = pyautogui.screenshot(region=RESOURCE_SCREENSHOT_REGION)
            screenshot.save(screenshot_path, format='JPEG', quality=50)
            logger.info(f"Resource screenshot saved at: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Error taking resource screenshot: {str(e)}")
            return None

    @staticmethod
    def take_civ_screenshot():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_civ_{timestamp}.jpg"
        screenshots_dir = os.path.join("screenshots", "civs")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, filename)
        
        try:
            # Take the screenshot using the predefined region from config
            screenshot = pyautogui.screenshot(region=CIV_SCREENSHOT_REGION)
            
            # Check if the screenshot is entirely black
            is_black = all(pixel == (0, 0, 0) for pixel in screenshot.getdata())
            if is_black:
                logger.warning(f"Warning: The civ screenshot appears to be entirely black.")
                logger.warning(f"Screenshot region: {CIV_SCREENSHOT_REGION}")
            
            # Save the screenshot as compressed JPG
            screenshot.save(screenshot_path, format='JPEG', quality=50)
            logger.info(f"Civilization screenshot saved at: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Error taking civilization screenshot: {str(e)}")
            return None
    
    @staticmethod
    def analyze_resource_screenshot(screenshot_path):
        """Analyze a resource screenshot using AI Analysis"""
        try:
            from ai_analysis import AIAnalysis
            from config import AI_CONFIG, RESOURCE_CHECK_PROMPT
            
            # Use default image model from config
            model_name = AI_CONFIG["default_models"]["image"]
            
            logger.info(f"Analyzing resource screenshot with {model_name}...")
            result = AIAnalysis.analyze_image_ollama(screenshot_path, RESOURCE_CHECK_PROMPT, model_name)
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing resource screenshot: {str(e)}")
            return None
    
    @staticmethod
    def analyze_civ_screenshot(screenshot_path):
        """Analyze a civilization screenshot using AI Analysis"""
        try:
            from ai_analysis import AIAnalysis
            from config import AI_CONFIG, CIV_COUNTER_PROMPT
            
            # Use default image model from config
            model_name = AI_CONFIG["default_models"]["image"]
            
            logger.info(f"Analyzing civilization screenshot with {model_name}...")
            result = AIAnalysis.analyze_civ_screenshot(screenshot_path, model_name, CIV_COUNTER_PROMPT)
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing civilization screenshot: {str(e)}")
            return None

if __name__ == "__main__":
    # Test the ScreenshotManager
    print("Taking resource screenshot in 5 seconds...")
    time.sleep(5)
    resource_screenshot = ScreenshotManager.take_resource_screenshot()
    if resource_screenshot:
        print(f"Resource screenshot saved at: {resource_screenshot}")
        
        # Test resource analysis
        print("\nAnalyzing resource screenshot...")
        resource_analysis = ScreenshotManager.analyze_resource_screenshot(resource_screenshot)
        print(f"Resource analysis result: {resource_analysis}")

    print("\nTaking civilization screenshot...")
    civ_screenshot = ScreenshotManager.take_civ_screenshot()
    if civ_screenshot:
        print(f"Civilization screenshot saved at: {civ_screenshot}")
        
        # Test civ analysis
        print("\nAnalyzing civilization screenshot...")
        civ_analysis = ScreenshotManager.analyze_civ_screenshot(civ_screenshot)
        print(f"Civilization analysis result: {civ_analysis}")

    print("\nScreenshot tests completed.")
