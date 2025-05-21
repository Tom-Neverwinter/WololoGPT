import keyboard
import time
import json # Added import
from screenshot_manager import ScreenshotManager
from ai_analysis import AIAnalysis
from utils import logger, show_popup_message
from config import get_default_civ_counter_prompt as get_civ_counter_prompt, RESOURCE_CHECK_PROMPT, AI_CONFIG # API_KEYS removed
from api_client import api_client


class GameActions:
    villager_creation_enabled = True
    castle_unit_creation_enabled = True
    VILLAGER_TARGETS_PER_AGE = {
        "Dark Age": 23,
        "Feudal Age": 35,
        "Castle Age": 60,
        "Imperial Age": 80
    }
    _auto_villager_boost_done_for_age = {
        "Dark Age": False,
        "Feudal Age": False,
        "Castle Age": False,
        "Imperial Age": False,
        "Unknown": True # Default to True for unknown to prevent action
    }

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
    def select_all_castles_create_unique_unit():
        """Select all Castles and create one unique unit"""
        if GameActions.castle_unit_creation_enabled:
            time.sleep(0.1)
            keyboard.press('ctrl')
            keyboard.press('shift')
            keyboard.press_and_release('c')  # Select all Castles
            keyboard.release('shift')
            keyboard.release('ctrl')
            keyboard.press_and_release('q')  # Create unique unit

    @staticmethod
    def enable_castle_unit_creation():
        """Enable automatic castle unit creation"""
        GameActions.castle_unit_creation_enabled = True

    @staticmethod
    def disable_castle_unit_creation():
        """Disable automatic castle unit creation"""
        GameActions.castle_unit_creation_enabled = False

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

            # Ensure AI_CONFIG is imported from config (already done at module level)
            ollama_model_name = AI_CONFIG.get("default_models", {}).get("image")
            if not ollama_model_name:
                logger.error("Ollama image model name not found in config for show_civs_counters.")
                show_popup_message("Civ Counters Error", "Ollama image model not configured. Check logs.")
                return

            # Assuming AIAnalysis.analyze_civ_screenshot is updated or routes to an Ollama compatible method
            # when given a model name instead of an API key.
            # The subtask description for analyze_civ_screenshot in screenshot_manager.py did not specify this change,
            # but this subtask implies AIAnalysis.analyze_civ_screenshot can handle a model_name.
            analysis = AIAnalysis.analyze_civ_screenshot(screenshot_path, ollama_model_name, civ_counter_prompt)
            logger.info(f"Analysis completed: {analysis}")
            counters = AIAnalysis.get_counters_for_civs(analysis) # This method might also need review if analysis format changes
            logger.info(f"Counters retrieved: {counters}")
            show_popup_message("Civilization Counters", counters)
            logger.info("Popup message shown successfully")
            api_client.create_action("show_civs_counters", "User requested civilization counters")
        except Exception as e:
            logger.error(f"Error in show_civs_counters: {str(e)}")
            show_popup_message("Error", f"An error occurred: {str(e)}")

    @staticmethod
    def auto_create_villagers_to_target(): # api_key parameter removed
        # Module-level imports (ScreenshotManager, AIAnalysis, logger, RESOURCE_CHECK_PROMPT, show_popup_message, AI_CONFIG)
        # are used as they are already available.
        try:
            logger.info("Attempting to auto-create villagers to target...")
            show_popup_message("Auto Villager Boost", "Analyzing game state...")
            
            # 1. Get Current Game State
            # Assuming take_resource_screenshot exists and is the correct method for game state
            screenshot_path = ScreenshotManager.take_resource_screenshot()
            if not screenshot_path:
                logger.error("Failed to take resource screenshot.")
                show_popup_message("Auto Villager Boost", "Error processing game state. Check logs for details.")
                return

            # Fetch Ollama model name from config
            ollama_model_name = AI_CONFIG.get("default_models", {}).get("image")
            if not ollama_model_name:
                logger.error("Ollama image model name not found in config (AI_CONFIG['default_models']['image']).")
                show_popup_message("Auto Villager Boost", "Ollama image model not configured. Check logs.")
                return

            # Use Ollama for analysis
            logger.info(f"Using Ollama model '{ollama_model_name}' for resource analysis.")
            analysis_result_str = AIAnalysis.analyze_image_ollama(screenshot_path, RESOURCE_CHECK_PROMPT, ollama_model_name)
            if not analysis_result_str:
                logger.error("Failed to analyze resource screenshot with Ollama or got empty result.")
                show_popup_message("Auto Villager Boost", "Error processing game state with Ollama. Check logs.")
                return

            game_state_json = json.loads(analysis_result_str) # Potential JSONDecodeError
            
            current_age = game_state_json.get("Current_age", "Unknown")
            current_villagers = 0
            try:
                # Villager count might be a string, ensure conversion
                current_villagers = int(game_state_json.get("Units", {}).get("number of villagers", 0))
            except ValueError:
                logger.error(f"Could not parse villager count from JSON: {game_state_json.get('Units', {}).get('number of villagers')}")
                show_popup_message("Auto Villager Boost", "Error processing game state. Check logs for details.")
                return

            logger.info(f"Current game state: Age - {current_age}, Villagers - {current_villagers}")

            # 2. "Once Per Age/Trigger" Logic
            if GameActions._auto_villager_boost_done_for_age.get(current_age, True): # Default to True if age not in dict
                message = f"Boost for {current_age} already applied or not needed."
                logger.info(message)
                show_popup_message("Auto Villager Boost", message)
                return

            # 3. Determine Target and Needed Villagers
            target_villagers = GameActions.VILLAGER_TARGETS_PER_AGE.get(current_age)
            if target_villagers is None:
                message = f"No specific villager target for {current_age}."
                logger.info(message)
                show_popup_message("Auto Villager Boost", message)
                # Mark as done for this specific (current_age) key to prevent repeated checks for an untargeted age.
                GameActions._auto_villager_boost_done_for_age[current_age] = True 
                return

            needed_villagers = target_villagers - current_villagers

            # 4. Create Villagers
            if needed_villagers > 0:
                if not GameActions.villager_creation_enabled:
                    message = "Villager creation is disabled in settings."
                    logger.info(message)
                    show_popup_message("Auto Villager Boost", message)
                    # Do NOT mark as done for the age, allow retry on next trigger if enabled.
                    return
                
                max_at_once = 10 
                villagers_to_create_this_run = min(needed_villagers, max_at_once)
                
                popup_message_creation = f"Creating {villagers_to_create_this_run} villagers for {current_age}."
                logger.info(f"Target: {target_villagers} for {current_age}. Current: {current_villagers}. Need to create: {needed_villagers} villagers. Will create {villagers_to_create_this_run} now.")
                show_popup_message("Auto Villager Boost", popup_message_creation)

                for i in range(villagers_to_create_this_run):
                    GameActions.select_all_tcs_create_one_villager()
                    logger.info(f"Queued villager {i+1} of {villagers_to_create_this_run}.")
                    time.sleep(0.3) # Small delay between each command

                # Mark boost as done for this age after attempting creation
                GameActions._auto_villager_boost_done_for_age[current_age] = True
                logger.info(f"Auto-villager creation attempt completed for {current_age}.")
            else:
                message = f"Villager target for {current_age} already met. (Current: {current_villagers}, Target: {target_villagers})"
                logger.info(message)
                show_popup_message("Auto Villager Boost", message)
                GameActions._auto_villager_boost_done_for_age[current_age] = True
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in auto_create_villagers_to_target: {e}. Response was: {analysis_result_str if 'analysis_result_str' in locals() else 'Unavailable'}")
            show_popup_message("Auto Villager Boost", "Error processing game state. Check logs for details.")
        except Exception as e:
            logger.error(f"An unexpected error occurred in auto_create_villagers_to_target: {e}", exc_info=True)
            show_popup_message("Auto Villager Boost", "Error processing game state. Check logs for details.")
