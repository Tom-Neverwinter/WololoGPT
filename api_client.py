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

    def create_user_session(self, username, teammates_username, app_version):
        try:
            data = {
                "ip": self.get_ip(),
                "pc_name_description": self.get_windows_profile_name(),
                "username": username,
                "teammates_username": teammates_username,
                "app_version": app_version,
                "windows_version": platform.platform()
            }
            response = requests.post(f"{API_BASE_URL}/user_sessions/", json=data)
            response.raise_for_status()
            self.session_id = response.json()["id"]
            logger.info(f"User session created with ID: {self.session_id}")
        except requests.RequestException as e:
            logger.error(f"Failed to create user session: {str(e)}")

    def create_action(self, action_type, description):
        if not self.session_id:
            logger.warning("No active session. Cannot create action.")
            return

        try:
            data = {
                "session_id": self.session_id,
                "action_type": action_type,
                "description": description
            }
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

api_client = APIClient()
