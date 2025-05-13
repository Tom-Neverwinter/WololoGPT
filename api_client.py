import os
import requests
import uuid
import socket
import platform
from config import API_BASE_URL
from utils import logger

class APIClient:
    def __init__(self):
        self.session_id = None
        self.api_enabled = True  # Flag to enable/disable API usage

    def create_user_session(self, username, teammates_username, app_version, client_info=None):
        if not self.api_enabled:
            logger.info("API tracking disabled. Not creating user session.")
            return
            
        try:
            # Get additional system info
            if client_info is None:
                client_info = {}
                
            # Add system resource info if available
            try:
                from ai_analysis import AIAnalysis
                resources = AIAnalysis.get_system_resource_info()
                client_info["system_resources"] = resources
            except Exception as e:
                logger.warning(f"Could not get system resources: {str(e)}")
            
            data = {
                "ip": self.get_ip(),
                "pc_name_description": self.get_windows_profile_name(),
                "username": username,
                "teammates_username": teammates_username,
                "app_version": app_version,
                "windows_version": platform.platform(),
                "ollama_enabled": self.check_ollama_status(),
                "client_info": client_info
            }
            response = requests.post(f"{API_BASE_URL}/user_sessions/", json=data)
            response.raise_for_status()
            self.session_id = response.json()["id"]
            logger.info(f"User session created with ID: {self.session_id}")
        except requests.RequestException as e:
            logger.error(f"Failed to create user session: {str(e)}")

    def create_action(self, action_type, description, additional_data=None):
        if not self.api_enabled or not self.session_id:
            logger.warning("No active session or API disabled. Cannot create action.")
            return

        try:
            data = {
                "session_id": self.session_id,
                "action_type": action_type,
                "description": description
            }
            
            # Add additional data if provided
            if additional_data:
                data["additional_data"] = additional_data
                
            response = requests.post(f"{API_BASE_URL}/actions/", json=data)
            response.raise_for_status()
            logger.info(f"Action created: {action_type} - {description}")
        except requests.RequestException as e:
            logger.error(f"Failed to create action: {str(e)}")

    @staticmethod
    def get_ip():
        try:
            return requests.get('https://api.ipify.org').text
        except requests.RequestException:
            return "Unknown"

    @staticmethod
    def get_windows_profile_name():
        try:
            return os.environ['USERNAME']
        except KeyError:
            return "Unknown"

    def check_server_status(self):
        try:
            response = requests.get(API_BASE_URL)
            return response.status_code == 200
        except requests.RequestException:
            return False
            
    def check_ollama_status(self):
        """Check if Ollama is running and available"""
        try:
            from ai_analysis import AIAnalysis
            success, _ = AIAnalysis.test_ollama_connection()
            return success
        except Exception as e:
            logger.error(f"Failed to check Ollama status: {str(e)}")
            return False
            
    def toggle_api(self, enabled=True):
        """Enable or disable API tracking"""
        self.api_enabled = enabled
        logger.info(f"API tracking {'enabled' if enabled else 'disabled'}")

api_client = APIClient()
