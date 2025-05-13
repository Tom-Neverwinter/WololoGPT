import os
import sys
import logging
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QMetaObject, Q_ARG
import json
import platform

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Add file logging
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PopupManager(QObject):
    show_popup_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.show_popup_signal.connect(self._show_popup)

    @pyqtSlot(str, str)
    def show_popup_message(self, title, text):
        logger.info(f"show_popup_message called with title: {title}, text: {text}")
        self.show_popup_signal.emit(title, text)

    def _show_popup(self, title, text):
        logger.info("_show_popup function started")
        app = QApplication.instance()
        if app is None:
            logger.info("No QApplication instance found, creating a new one")
            app = QApplication([])
        else:
            logger.info("Existing QApplication instance found")
        
        logger.info("Creating QMessageBox")
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        logger.info("Setting window flags")
        msg.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        logger.info("Getting screen geometry")
        screen = app.primaryScreen().geometry()
        
        logger.info("Calculating position")
        x = screen.width() - msg.width()
        y = (screen.height() - msg.height()) // 2
        
        logger.info(f"Moving message box to position: ({x}, {y})")
        msg.move(x, y)
        
        logger.info("Showing message box")
        msg.show()
        msg.raise_()
        msg.activateWindow()
        
        logger.info("Executing message box")
        msg.exec()
        logger.info("Message box closed")

popup_manager = PopupManager()

def show_popup_message(title, text):
    QMetaObject.invokeMethod(popup_manager, "show_popup_message",
                             Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, title),
                             Q_ARG(str, text))

def check_system_requirements():
    """Check if the system meets the minimum requirements for running the application"""
    try:
        # Check OS
        system = platform.system()
        if system != "Windows":
            logger.warning(f"Unsupported OS: {system}. This application is optimized for Windows.")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.warning(f"Unsupported Python version: {python_version.major}.{python_version.minor}. Recommended: 3.8+")
        
        # Check RAM
        import psutil
        memory = psutil.virtual_memory()
        ram_gb = round(memory.total / (1024**3), 1)
        if ram_gb < 4:
            logger.warning(f"Low RAM detected: {ram_gb}GB. Recommended: 8GB+")
        
        # Check for GPU
        gpu_info = "Unknown"
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_info = f"{gpu.name} with {round(gpu.memoryTotal / 1024, 1)}GB VRAM"
                if gpu.memoryTotal < 4000:  # Less than 4GB VRAM
                    logger.warning(f"Low VRAM detected: {round(gpu.memoryTotal / 1024, 1)}GB. Recommended: 4GB+")
            else:
                logger.warning("No GPU detected. Using CPU for AI processing will be slower.")
        except ImportError:
            logger.warning("GPUtil not installed. Cannot check GPU details.")
        
        # Check for Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                logger.info(f"Ollama is running with {len(model_names)} models: {', '.join(model_names)}")
            else:
                logger.warning("Ollama is running but returned an unexpected status code.")
        except:
            logger.warning("Ollama is not running or not installed. AI features will not work.")
        
        logger.info(f"System check completed - OS: {system}, RAM: {ram_gb}GB, GPU: {gpu_info}")
        return True
    except Exception as e:
        logger.error(f"Error during system check: {str(e)}")
        return False

def save_user_settings(settings):
    """Save user settings to JSON file"""
    try:
        with open("user_info.json", "w") as f:
            json.dump(settings, f, indent=4)
        logger.info("User settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving user settings: {str(e)}")
        return False

def load_user_settings():
    """Load user settings from JSON file"""
    default_settings = {
        "your_username": "",
        "teammates_usernames": "",
        "api_key": "",
        "audio_alerts_enabled": True,
        "idle_villager_audio_enabled": True,
        "villager_hotkey": "1",
        "castle_hotkey": "2",
        "ai_settings": {
            "use_ollama": True,
            "preferred_model": "gemma3:4b-it-qat",
            "fallback_model": "gemma3:1b-it-qat",
            "optimize_for_gaming": True
        },
        "api_tracking_enabled": True
    }
    
    try:
        if os.path.exists("user_info.json"):
            with open("user_info.json", "r") as f:
                settings = json.load(f)
            
            # Add any missing keys from default settings
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
            
            # For nested settings like ai_settings
            if "ai_settings" in default_settings and ("ai_settings" not in settings or not isinstance(settings["ai_settings"], dict)):
                settings["ai_settings"] = default_settings["ai_settings"]
            elif "ai_settings" in default_settings and "ai_settings" in settings:
                for key, value in default_settings["ai_settings"].items():
                    if key not in settings["ai_settings"]:
                        settings["ai_settings"][key] = value
            
            return settings
        else:
            return default_settings
    except Exception as e:
        logger.error(f"Error loading user settings: {str(e)}")
        return default_settings
