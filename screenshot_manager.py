import pyautogui
import datetime
import os
from config import RESOURCE_SCREENSHOT_REGION
from PIL import Image
import time
class ScreenshotManager:
    @staticmethod
    def take_resource_screenshot():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.jpg"
        screenshots_dir = os.path.join("screenshots", "resources")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, filename)
        screenshot = pyautogui.screenshot(region=RESOURCE_SCREENSHOT_REGION)
        screenshot.save(screenshot_path, format='JPEG', quality=50)
        return screenshot_path

    @staticmethod
    def take_civ_screenshot():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_civ_{timestamp}.jpg"
        screenshots_dir = os.path.join("screenshots", "civs")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, filename)
        
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        
        # Define the region for the bottom right corner (e.g., 200x200 pixels)
        region_width, region_height = 600, 400
        region = (screen_width - region_width, screen_height - region_height, region_width, region_height)
        
        # Take the screenshot
        screenshot = pyautogui.screenshot(region=region)
        
        # Check if the screenshot is entirely black
        if screenshot.getcolors() == [(screenshot.width * screenshot.height, (0, 0, 0))]:
            print(f"Warning: The screenshot appears to be entirely black.")
            print(f"Screenshot region: {region}")
        
        # Save the screenshot as compressed JPG
        screenshot.save(screenshot_path, format='JPEG', quality=50)
        return screenshot_path


if __name__ == "__main__":
    # Test the ScreenshotManager
    print("Taking resource screenshot...")
    time.sleep(5)
    resource_screenshot = ScreenshotManager.take_resource_screenshot()
    print(f"Resource screenshot saved at: {resource_screenshot}")

    print("\nTaking civilization screenshot...")
    civ_screenshot = ScreenshotManager.take_civ_screenshot()
    print(f"Civilization screenshot saved at: {civ_screenshot}")

    print("\nScreenshot tests completed.")