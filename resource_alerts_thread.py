from PyQt6.QtCore import QThread, pyqtSignal, QObject
from screenshot_manager import ScreenshotManager
from ai_analysis import AIAnalysis
from audio_manager import AudioManager
from config import RESOURCE_CHECK_PROMPT, RESOURCE_CHECK_INTERVAL, VILLAGER_WARNING_INTERVAL
from utils import logger
import json
import time
from queue import Queue
from color_flash import color_flash
from api_client import api_client

class ResourceAlertsThread(QThread):
    alert_signal = pyqtSignal(str)
    color_flash_signal = pyqtSignal(str, float, tuple, tuple, float, str)

    def __init__(self, api_key):
        super().__init__()
        self.running = False
        self.audio_queue = Queue()
        self.color_flash_queue = Queue()
        self.last_villager_check_time = 0
        self.api_key = api_key
        self.color_flash_enabled = True
        self.audio_alerts_enabled = True
        self.idle_villager_audio_enabled = True

    def run(self):
        """Main loop for resource alerts"""
        while self.running:
            screenshot_path = ScreenshotManager.take_resource_screenshot()
            resources = AIAnalysis.analyze_image_gemini(screenshot_path, RESOURCE_CHECK_PROMPT, self.api_key)
            
            # Track the resource check
            api_client.create_action("resource_check", "Resource check performed")
            
            if resources:
                try:
                    resources_json = json.loads(resources)
                    self.check_house_limit(resources_json)
                    self.check_villager_count(resources_json)
                    self.check_floating_resources(resources_json)
                    self.check_idle_villagers(resources_json)
                    self.play_queued_warnings()
                    logger.info(resources)
                    
                    # Track successful resource analysis
                    #api_client.create_action("resource_analysis", f"Resource analysis completed: {resources}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse AI analysis response as JSON. Response: '{resources}'. Error: {e}")
                    # Track failed resource analysis
                    api_client.create_action("resource_analysis_error", f"Failed to parse AI analysis response: {resources}")
                    continue  # Continue to the next iteration of the loop
            else:
                logger.error("Error with LLM provider or empty response")
                # Track failed resource analysis
                api_client.create_action("resource_analysis_error", "LLM provider returned empty response")
            
            time.sleep(RESOURCE_CHECK_INTERVAL)

    def check_house_limit(self, resources_json):
        """Check if the player is approaching the house limit"""
        total_active_units = int(resources_json["Units"]["number of total units"])
        current_house_limit = int(resources_json["Units"]["Current House limit"])

        buffer = 3
        if total_active_units > 125:
            buffer += 15
        elif total_active_units > 75:
            buffer += 10
        elif total_active_units > 50:
            buffer += 5
        if total_active_units != 0 and (total_active_units == current_house_limit or current_house_limit - total_active_units <= buffer) and current_house_limit != 200:
            self.audio_queue.put('audio/warnings/maison.mp3')
            self.color_flash_queue.put(("yellow", 2, (0, 100), (300, 100), 0.80, "Build Houses!"))
            api_client.create_action("house_limit_warning", f"House limit warning triggered: {total_active_units}/{current_house_limit}")

    def check_villager_count(self, resources_json):
        """Check if the villager count is low in late game stages"""
        current_time = time.time()
        if current_time - self.last_villager_check_time >= VILLAGER_WARNING_INTERVAL:
            self.last_villager_check_time = current_time
            current_age = resources_json.get("Current_age", "")
            villagers_count = int(resources_json.get("Units", {}).get("number of villagers", 0))
            if current_age in ["Castle Age", "Imperial Age"] and villagers_count < 100:
                self.audio_queue.put('audio/warnings/villageois.mp3')
                self.color_flash_queue.put(("orange", 2, (0, 100), (300, 100), 0.80, "Create Villagers!"))
                api_client.create_action("low_villager_count_warning", f"Low villager count warning triggered: {villagers_count} villagers in {current_age}")

    def check_floating_resources(self, resources_json):
        """Check for excess unused resources"""
        res_json = resources_json.get("Resources", {})
        
        try:
            stone_amount = int(res_json.get("Stone", 0))
            if stone_amount > 650:
                self.audio_queue.put('audio/warnings/floating_stone.mp3')
                self.color_flash_queue.put(("grey", 2, (0, 200), (300, 100), 0.80, "Use Stone!"))
                api_client.create_action("floating_stone_warning", f"Floating stone warning triggered: {stone_amount} stone")
            
            current_age = resources_json.get("Current_age", "")
            if current_age == "Castle Age":
                self._check_resource_threshold(res_json, 1000, "castle_age")
            
            if current_age == "Imperial Age":
                self._check_resource_threshold(res_json, 2000, "imperial_age")
        except Exception as e:
            logger.error(f"Error in check_floating_resources: {str(e)}")
            api_client.create_action("floating_resources_check_error", f"Error checking floating resources: {str(e)}")

    def _check_resource_threshold(self, res_json, threshold, age):
        """Helper method to check if resources exceed a given threshold"""
        for resource, amount in res_json.items():
            try:
                if int(amount) >= threshold:
                    self.audio_queue.put(f'audio/warnings/floating_{resource.lower()}.mp3')
                    color = {"Wood": "brown", "Food": "red", "Gold": "gold", "Stone": "grey"}
                    self.color_flash_queue.put((color.get(resource, "blue"), 2, (0, 300), (300, 100), 0.80, f"Use {resource}!"))
                    api_client.create_action(f"floating_{resource.lower()}_warning", f"Floating {resource} warning triggered: {amount} {resource} in {age}")
            except ValueError:
                logger.warning(f"Invalid amount for resource {resource}: {amount}")

    def enable_color_flash(self, enabled=True):
        """Enable or disable color flash alerts"""
        self.color_flash_enabled = enabled
        logger.debug(f"Color flash {'enabled' if enabled else 'disabled'}")

    def disable_color_flash(self):
        """Disable color flash alerts"""
        self.color_flash_enabled = False

    def enable_audio_alerts(self, enabled=True):
        """Enable or disable all audio alerts"""
        self.audio_alerts_enabled = enabled
        logger.debug(f"Audio alerts {'enabled' if enabled else 'disabled'}")

    def enable_idle_villager_audio(self, enabled=True):
        """Enable or disable idle villager audio alert"""
        self.idle_villager_audio_enabled = enabled
        logger.debug(f"Idle villager audio alert {'enabled' if enabled else 'disabled'}")

    def play_queued_warnings(self):
        """Play all queued audio warnings and show color flashes"""
        while not self.audio_queue.empty() or not self.color_flash_queue.empty():
            if not self.audio_queue.empty():
                audio_file = self.audio_queue.get()
                if self.audio_alerts_enabled:
                    if 'idle_villagers.wav' not in audio_file or self.idle_villager_audio_enabled:
                        AudioManager.play_audio(audio_file, volume=0.35)
            
            if not self.color_flash_queue.empty() and self.color_flash_enabled:
                color_flash_params = self.color_flash_queue.get()
                logger.debug(f"Emitting color flash signal: {color_flash_params}")
                self.color_flash_signal.emit(*color_flash_params)
            
            time.sleep(2)

    def stop(self):
        """Stop the resource alerts thread"""
        self.running = False

    def check_idle_villagers(self, resources_json):
        """Check if there are any idle villagers"""
        idle_villagers = int(resources_json.get("Idle Villagers", 0))
        if idle_villagers > 0:
            if self.idle_villager_audio_enabled:
                self.audio_queue.put('audio/warnings/idle_villagers.wav')
            self.color_flash_queue.put(("grey", 2, (0, 400), (300, 100), 0.80, f"{idle_villagers} Idle Villager{'s' if idle_villagers > 1 else ''}!"))
            api_client.create_action("idle_villagers_warning", f"Idle villagers warning triggered: {idle_villagers} idle villager(s)")
