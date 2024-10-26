import keyboard
import time
from screenshot_manager import ScreenshotManager
from ai_analysis import AIAnalysis
from utils import logger, show_popup_message
from config import get_civ_counter_prompt, API_KEYS
from api_client import api_client


class GameActions:
    villager_creation_enabled = True

    @staticmethod
    def select_all_tcs_create_one_villager():
        """Select all Town Centers and create one villager"""
        if GameActions.villager_creation_enabled:
            time.sleep(0.1)
            keyboard.press('ctrl')
            keyboard.press('shift')
            keyboard.press_and_release('h')  # Select all Town Centers
            keyboard.release('shift')
            keyboard.release('ctrl')
            keyboard.press_and_release('q')  # Create villager

    @staticmethod
    def enable_villager_creation():
        """Enable automatic villager creation"""
        GameActions.villager_creation_enabled = True

    @staticmethod
    def disable_villager_creation():
        """Disable automatic villager creation"""
        GameActions.villager_creation_enabled = False

    @staticmethod
    def show_civs_counters(username, teammates):
        """Show civilization counters based on screenshot analysis"""
        try:
            logger.info("Starting show_civs_counters method")
            screenshot_path = ScreenshotManager.take_civ_screenshot()
            logger.info(f"Screenshot taken: {screenshot_path}")
            
            # Get the customized prompt
            civ_counter_prompt = get_civ_counter_prompt(username, teammates)
            
            analysis = AIAnalysis.analyze_civ_screenshot(screenshot_path, API_KEYS["GOOGLE"], civ_counter_prompt)
            logger.info(f"Analysis completed: {analysis}")
            counters = AIAnalysis.get_counters_for_civs(analysis)
            logger.info(f"Counters retrieved: {counters}")
            show_popup_message("Civilization Counters", counters)
            logger.info("Popup message shown successfully")
            api_client.create_action("show_civs_counters", "User requested civilization counters")
        except Exception as e:
            logger.error(f"Error in show_civs_counters: {str(e)}")
            show_popup_message("Error", f"An error occurred: {str(e)}")
