print("WololoGPT loading... loading python environment, checking admin rights...")

from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QTextBrowser, QHBoxLayout, QMessageBox, QScrollArea, QCheckBox, QComboBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QKeyEvent
from PyQt6.QtCore import QUrl
# Remove this line:
# from PyQt6.QtWebEngineWidgets import QWebEngineView
from game_actions import GameActions
import keyboard
import json
import requests
from resource_alerts_thread import ResourceAlertsThread
from audio_manager import AudioManager
from config import set_api_key, API_KEYS
from utils import logger, show_popup_message
from gui_layout import create_main_layout, resource_path
from ai_analysis import AIAnalysis
from color_flash import color_flash, process_color_flashes, initialize_root
from api_client import api_client
import sys
import os
import traceback
import ctypes

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Python Version Check ---
MIN_PYTHON_VERSION = (3, 9)
MAX_PYTHON_VERSION = (3, 11)
current_python_version = sys.version_info

if not (MIN_PYTHON_VERSION <= current_python_version <= MAX_PYTHON_VERSION):
    # Version is incompatible
    version_str = f"{current_python_version.major}.{current_python_version.minor}.{current_python_version.micro}"
    error_message = (
        f"Unsupported Python Version: {version_str}\n\n"
        f"WololoGPT requires Python version {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} "
        f"to {MAX_PYTHON_VERSION[0]}.{MAX_PYTHON_VERSION[1]}.\n\n"
        "Please use a compatible Python version (e.g., via pyenv)."
    )
    
    print(error_message, file=sys.stderr) # Always print to console

    try:
        # Attempt to show a GUI message box if PyQt is available
        # Note: QApplication and QMessageBox are already imported at the top of main.py
        # from PyQt6.QtWidgets import QApplication, QMessageBox # Not needed again if already globally imported
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([]) # Temporary app instance
            
        QMessageBox.critical(None, "Unsupported Python Version", error_message)
    except ImportError:
        # PyQt6 not available yet or import failed, console message is the fallback.
        pass 
    except RuntimeError:
        # This can happen if QApplication is created but then we try to create another
        # or if some other Qt issue occurs this early.
        pass
        
    sys.exit(1)
# --- End Python Version Check ---

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resource_alerts_thread = None
        self.activity_check_timer = None
        self.server_status_timer = None
        self.app_version = "1.0.0"  # Define the app version here
        self.api_key_validated = False  # Add this line to track API key validation status
        
        # Initialize hotkeys before initUI
        self.villager_hotkey = "1"  # Default hotkey
        self.castle_hotkey = "2"  # Default castle hotkey
        
        self.initUI()
        self.setup_message_update()
        self.setup_server_status_check()
        self.color_flash_windows = []
        initialize_root()  # Initialize the Tkinter root window
        
        # Load user info at startup (without showing popups)
        self.load_user_info(show_popups=False)
        
        # Create user session when the app starts, but use loaded data
        api_client.create_user_session(
            self.your_username_input.text(),
            self.teammates_usernames_input.text(),
            self.app_version
        )

        # Disable Start and Stop buttons initially
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        # Play welcome audio
        AudioManager.play_audio('audio/warnings/welcome.mp3', volume=0.5)

        # Check Ollama status after UI is initialized and user info loaded
        self.check_ollama_status()

    def initUI(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Add the existing layout from gui_layout.py
        existing_layout = create_main_layout(self)
        layout.addLayout(existing_layout)
        
        # Add API key status icon
        self.api_key_status_icon = QLabel(self)
        self.api_key_status_icon.setFixedSize(16, 16)
        
        # Find the API key layout and add the status icon
        for i in range(existing_layout.count()):
            item = existing_layout.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.itemAt(0).widget().text() == "Google LLM API Key:":
                    item.addWidget(self.api_key_status_icon)
                    break
        
        # Add LLM API status indicator
        self.llm_api_status_layout = self.create_llm_api_status_layout()
        layout.addLayout(self.llm_api_status_layout)

        # Add Ollama status indicator
        self.ollama_status_layout = self.create_ollama_status_layout()
        layout.addLayout(self.ollama_status_layout)
        
        # Add server status indicator
        self.server_status_layout = self.create_server_status_layout()
        layout.addLayout(self.server_status_layout)
        
        # Add message display area
        self.create_message_area(layout)
        
        # Add version display at the bottom as a clickable link
        self.version_label = QLabel(f'<a href="https://wolologpt.com/?utm_source=program&utm_medium=app_link">Version: {self.app_version}</a>')
        self.version_label.setOpenExternalLinks(True)
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.version_label.setToolTip("Click to visit wolologpt.com")
        layout.addWidget(self.version_label)
        
        self.setLayout(layout)

        # Connect signals to slots
        self.connect_signals()

        self.setWindowTitle('WololoGPT')  # Update the window title here
        self.setMinimumWidth(400)

        # Enable start button by default
        self.start_button.setEnabled(True)

        # Update the start button text based on API key validation
        self.update_start_button_text()

        # Disable Start button by default
        self.start_button.setEnabled(False)

        # Hide the API key status icon initially
        self.api_key_status_icon.hide()

    def create_user_info_layout(self):
        """Create the user info input layout"""
        user_info_layout = QVBoxLayout()
        
        # Your username input
        your_username_layout = QHBoxLayout()
        self.your_username_label = QLabel("Your Username:")
        self.your_username_input = QLineEdit()
        self.your_username_save_button = QPushButton("Save")
        self.your_username_save_button.clicked.connect(self.save_your_username)
        
        your_username_layout.addWidget(self.your_username_label)
        your_username_layout.addWidget(self.your_username_input)
        your_username_layout.addWidget(self.your_username_save_button)
        
        # Teammates' usernames input
        teammates_usernames_layout = QHBoxLayout()
        self.teammates_usernames_label = QLabel("Teammates' Usernames:")
        self.teammates_usernames_input = QLineEdit()
        self.teammates_usernames_input.setPlaceholderText("Enter teammates' usernames separated by commas (e.g., user1, user2)")
        self.teammates_usernames_save_button = QPushButton("Save")
        self.teammates_usernames_save_button.clicked.connect(self.save_teammates_usernames)
        
        teammates_usernames_layout.addWidget(self.teammates_usernames_label)
        teammates_usernames_layout.addWidget(self.teammates_usernames_input)
        teammates_usernames_layout.addWidget(self.teammates_usernames_save_button)
        
        user_info_layout.addLayout(your_username_layout)
        user_info_layout.addLayout(teammates_usernames_layout)
        
        return user_info_layout

    def create_llm_api_status_layout(self):
        """Create the LLM API status indicator layout"""
        llm_api_status_layout = QHBoxLayout()
        self.llm_api_status_label = QLabel("LLM API Status:")
        self.llm_api_status_indicator = QLabel()
        self.llm_api_status_indicator.setFixedSize(16, 16)
        
        llm_api_status_layout.addWidget(self.llm_api_status_label)
        llm_api_status_layout.addWidget(self.llm_api_status_indicator)
        llm_api_status_layout.addStretch()
        
        return llm_api_status_layout

    def create_message_area(self, layout):
        """Create the message display area"""
        self.message_area = QTextBrowser()
        self.message_area.setReadOnly(True)
        self.message_area.setMaximumHeight(100)
        self.message_area.setOpenExternalLinks(True)
        layout.addWidget(QLabel("Updates and News:"))
        layout.addWidget(self.message_area)

    def connect_signals(self):
        """Connect signals to their respective slots"""
        self.start_button.clicked.connect(self.start_resource_alerts)
        self.stop_button.clicked.connect(self.stop_resource_alerts)
        self.villager_checkbox.stateChanged.connect(self.toggle_villager_creation)
        self.castle_checkbox.stateChanged.connect(self.toggle_castle_unit_creation)
        self.civ_counters_checkbox.stateChanged.connect(self.toggle_civ_counters_hotkey)
        self.color_flash_checkbox.stateChanged.connect(self.toggle_color_flash_alerts)
        self.your_username_save_button.clicked.connect(self.save_your_username)
        self.teammates_usernames_save_button.clicked.connect(self.save_teammates_usernames)
        self.audio_alerts_checkbox.stateChanged.connect(self.toggle_audio_alerts)
        self.idle_villager_audio_checkbox.stateChanged.connect(self.toggle_idle_villager_audio)
        self.api_key_test_button.clicked.connect(self.test_api_key)
        self.villager_hotkey_input.textChanged.connect(self.update_villager_hotkey)
        self.castle_hotkey_input.textChanged.connect(self.update_castle_hotkey)
        self.villager_hotkey_input.installEventFilter(self)
        self.castle_hotkey_input.installEventFilter(self)

    def setup_message_update(self):
        """Set up periodic message updates"""
        self.update_message()
        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.update_message)
        self.message_timer.start(300000)  # Update every 5 minutes

    def update_message(self):
        """Update the message area with news or updates from the website"""
        try:
            url = "https://wolologpt.com/in-program-messagebox.html"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad responses
            
            html_content = response.text
            
            # Update the QTextBrowser with the fetched HTML content
            self.message_area.setHtml(html_content)
            
            logger.info("Message updated successfully from the website")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch message from the website: {str(e)}")
            self.message_area.setHtml("<p>Failed to load latest news. Dang!</p>")

    def start_resource_alerts(self):
        """Start the resource alerts thread and activity check timer"""
        if not self.api_key_input.text():
            show_popup_message("API Key Required", "Please enter a valid LLM API key before starting resource alerts.")
            return

        if self.resource_alerts_thread is None or not self.resource_alerts_thread.isRunning():
            self.resource_alerts_thread = ResourceAlertsThread(API_KEYS["GOOGLE"])
            self.resource_alerts_thread.color_flash_signal.connect(self.show_color_flash)
            logger.debug("Color flash signal connected")
        self.resource_alerts_thread.enable_color_flash(self.color_flash_checkbox.isChecked())
        self.resource_alerts_thread.running = True
        self.resource_alerts_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Start the activity check timer
        self.start_activity_check_timer()

        # Log the action
        api_client.create_action("start_resource_alerts", "User started resource alerts")

    def stop_resource_alerts(self):
        """Stop the resource alerts thread and activity check timer"""
        if self.resource_alerts_thread and self.resource_alerts_thread.isRunning():
            self.resource_alerts_thread.stop()
            self.resource_alerts_thread.wait()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Stop the activity check timer
        self.stop_activity_check_timer()

        # Log the action
        api_client.create_action("stop_resource_alerts", "User stopped resource alerts")

    def start_activity_check_timer(self):
        """Start the timer for activity check"""
        self.activity_check_timer = QTimer(self)
        self.activity_check_timer.timeout.connect(self.show_activity_check_popup)
        self.activity_check_timer.start(2 * 60 * 60 * 1000)  # 2 hours in milliseconds
        

    def stop_activity_check_timer(self):
        """Stop the activity check timer"""
        if self.activity_check_timer:
            self.activity_check_timer.stop()

    def show_activity_check_popup(self):
        """Show the activity check popup"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Activity Check")
        msg_box.setText("Are you still active?\n\nThis check is to prevent excessive LLM API calls and reduce costs.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            # User is still active, reset the timer
            self.activity_check_timer.start()
        else:
            # User is not active, stop the resource alerts
            self.stop_resource_alerts()

    def toggle_villager_creation(self, state):
        """Toggle the villager creation feature"""
        if state == Qt.CheckState.Checked.value:
            GameActions.enable_villager_creation()
            api_client.create_action("enable_villager_creation", "User enabled auto villager creation")
        else:
            GameActions.disable_villager_creation()
            api_client.create_action("disable_villager_creation", "User disabled auto villager creation")
        self.setup_hotkeys()

    def toggle_civ_counters_hotkey(self, state):
        """Toggle the civilization counters hotkey"""
        if state == Qt.CheckState.Checked.value:
            try:
                keyboard.add_hotkey('ctrl+.', self.show_civ_counters)
                logger.info("Civ counters hotkey enabled")
                api_client.create_action("enable_civ_counters_hotkey", "User enabled civ counters hotkey")
            except Exception as e:
                logger.error(f"Failed to add civ counters hotkey: {str(e)}")
        else:
            try:
                keyboard.remove_hotkey('ctrl+.')
                logger.info("Civ counters hotkey disabled")
                api_client.create_action("disable_civ_counters_hotkey", "User disabled civ counters hotkey")
            except Exception as e:
                logger.error(f"Failed to remove civ counters hotkey: {str(e)}")

    def show_civ_counters(self):
        logger.info("Civ counters hotkey pressed")
        GameActions.show_civs_counters(
            self.your_username_input.text(),
            self.teammates_usernames_input.text()
        )

    def setup_hotkeys(self):
        """Set up the application hotkeys"""
        try:
            # Remove all existing hotkeys
            keyboard.unhook_all()
            
            # Set up the villager creation hotkey
            if self.villager_checkbox.isChecked():
                keyboard.add_hotkey(self.villager_hotkey, GameActions.select_all_tcs_create_one_villager)
            
            # Set up the castle unit creation hotkey
            if self.castle_checkbox.isChecked():
                keyboard.add_hotkey(self.castle_hotkey, GameActions.select_all_castles_create_unique_unit)
            
            # Set up the civ counters hotkey
            if self.civ_counters_checkbox.isChecked():
                keyboard.add_hotkey('ctrl+.', lambda: GameActions.show_civs_counters(
                    self.your_username_input.text(),
                    self.teammates_usernames_input.text()
                ))
            
            logger.info(f"Hotkeys set up successfully. Villager hotkey: {self.villager_hotkey}, Castle hotkey: {self.castle_hotkey}")
        except Exception as e:
            logger.error(f"Error setting up hotkeys: {str(e)}")

    def save_user_info(self):
        """Save user information to a JSON file"""
        user_info = {
            "your_username": self.your_username_input.text(),
            "teammates_usernames": self.teammates_usernames_input.text(),
            "api_key": self.api_key_input.text(),
            "audio_alerts_enabled": self.audio_alerts_checkbox.isChecked(),
            "idle_villager_audio_enabled": self.idle_villager_audio_checkbox.isChecked(),
            "villager_hotkey": self.villager_hotkey,
            "castle_hotkey": self.castle_hotkey
        }
        with open("user_info.json", "w") as f:
            json.dump(user_info, f)
        
        # Show a popup message to confirm the save
        show_popup_message("User Info Saved", "Your settings have been saved.")

    def load_user_info(self, show_popups=True):
        """Load user information from a JSON file"""
        try:
            with open("user_info.json", "r") as f:
                user_info = json.load(f)
                self.your_username_input.setText(user_info.get("your_username", ""))
                self.teammates_usernames_input.setText(user_info.get("teammates_usernames", ""))
                api_key = user_info.get("api_key", "")
                self.api_key_input.setText(api_key)
                
                # Load checkbox states
                self.audio_alerts_checkbox.setChecked(user_info.get("audio_alerts_enabled", True))
                self.idle_villager_audio_checkbox.setChecked(user_info.get("idle_villager_audio_enabled", True))
                
                # Load hotkeys
                self.villager_hotkey = user_info.get("villager_hotkey", "1")
                self.villager_hotkey_input.setText(self.villager_hotkey)
                self.castle_hotkey = user_info.get("castle_hotkey", "2")
                self.castle_hotkey_input.setText(self.castle_hotkey)
                
                # Don't validate the API key automatically
                self.api_key_validated = False
                self.update_api_key_status(False)
                self.update_llm_api_status(False)
                # self.update_start_button_text() # This will be called by check_ollama_status
                
            self.setup_hotkeys()
        except FileNotFoundError:
            logger.warning("user_info.json not found")

    def verify_and_update_api_key(self, api_key):
        """Verify the API key and update its status"""
        is_valid, message = AIAnalysis.test_google_api_key(api_key)
        if is_valid:
            set_api_key(api_key)
            self.update_api_key_status(True)
            self.update_llm_api_status(True)
            if self.resource_alerts_thread:
                self.resource_alerts_thread.api_key = api_key
            show_popup_message("API Key Verified", "Your Google API key has been verified successfully.")
            self.start_button.setEnabled(True)
            self.api_key_validated = True
            self.update_start_button_text()
            self.api_key_status_icon.show()  # Show the icon after successful validation
        else:
            self.update_api_key_status(False)
            self.update_llm_api_status(False)
            show_popup_message("API Key Error", f"Failed to verify API key: {message}")
            # self.start_button.setEnabled(False) # Managed by update_start_button_text
            self.stop_button.setEnabled(False)
            self.api_key_validated = False
            self.update_start_button_text() # This will consider Ollama status too
            self.api_key_status_icon.hide()  # Hide the icon if validation fails

    def update_api_key_status(self, is_valid):
        """Update the API key status icon"""
        if is_valid:
            icon_path = resource_path("images/check.png")
            icon = QIcon(icon_path)
            self.api_key_status_icon.setStyleSheet("background-color: #90EE90;")
            self.api_key_status_icon.show()
        else:
            icon_path = resource_path("images/x.png")
            icon = QIcon(icon_path)
            self.api_key_status_icon.setStyleSheet("background-color: #FFB6C1;")
            self.api_key_status_icon.hide()

        if icon.isNull():
            print(f"Failed to load icon from: {icon_path}")
        else:
            pixmap = icon.pixmap(16, 16)
            self.api_key_status_icon.setPixmap(pixmap)

    def update_llm_api_status(self, is_valid):
        """Update the LLM API status indicator"""
        if is_valid:
            self.llm_api_status_indicator.setStyleSheet("background-color: #90EE90; border-radius: 8px;")
            self.llm_api_status_indicator.setToolTip("LLM API is online")
        else:
            self.llm_api_status_indicator.setStyleSheet("background-color: #FFB6C1; border-radius: 8px;")
            self.llm_api_status_indicator.setToolTip("LLM API is offline")

    def toggle_color_flash_alerts(self, state):
        """Toggle the color flash alerts feature"""
        if state == Qt.CheckState.Checked.value:
            if self.resource_alerts_thread:
                self.resource_alerts_thread.enable_color_flash()
            api_client.create_action("enable_color_flash_alerts", "User enabled color flash alerts")
        else:
            if self.resource_alerts_thread:
                self.resource_alerts_thread.disable_color_flash()
            api_client.create_action("disable_color_flash_alerts", "User disabled color flash alerts")

    def show_color_flash(self, color, duration, location, size, opacity, text):
        """Show color flash alert"""
        logger.debug(f"show_color_flash called with: {color}, {duration}, {location}, {size}, {opacity}, {text}")
        flash_window = color_flash(color, duration, location, size, opacity, text)
        self.color_flash_windows.append(flash_window)

    def create_server_status_layout(self):
        """Create the server status indicator layout"""
        server_status_layout = QHBoxLayout()
        self.server_status_label = QLabel("API Server Status:")
        self.server_status_indicator = QLabel()
        self.server_status_indicator.setFixedSize(16, 16)
        
        server_status_layout.addWidget(self.server_status_label)
        server_status_layout.addWidget(self.server_status_indicator)
        server_status_layout.addStretch()
        
        return server_status_layout

    def setup_server_status_check(self):
        """Set up periodic server status checks"""
        self.check_server_status()
        self.server_status_timer = QTimer(self)
        self.server_status_timer.timeout.connect(self.check_server_status)
        self.server_status_timer.start(60000)  # Check every minute

    def check_server_status(self):
        """Check the API server status and update the indicator"""
        is_live = api_client.check_server_status()
        if is_live:
            self.server_status_indicator.setStyleSheet("background-color: #90EE90; border-radius: 8px;")
            self.server_status_indicator.setToolTip("API Server is live")
        else:
            self.server_status_indicator.setStyleSheet("background-color: #FFB6C1; border-radius: 8px;")
            self.server_status_indicator.setToolTip("API Server is not responding")

    def closeEvent(self, event):
        """Handle application close event"""
        self.stop_activity_check_timer()
        if self.server_status_timer:
            self.server_status_timer.stop()
        for window in self.color_flash_windows:
            if window.winfo_exists():
                window.destroy()
        api_client.create_action("close_application", "User closed the application")
        event.accept()

    def save_your_username(self):
        """Save the user's username"""
        username = self.your_username_input.text()
        self.save_user_info()
        show_popup_message("Username Saved", "Your username has been saved.")
        api_client.create_action("save_username", f"User saved username: {username}")

    def save_teammates_usernames(self):
        """Save the teammates' usernames"""
        teammates = self.teammates_usernames_input.text()
        self.save_user_info()
        show_popup_message("Teammates Saved", "Your teammates' usernames have been saved.")
        api_client.create_action("save_teammates", f"User saved teammates: {teammates}")

    def create_save_buttons_layout(self):
        """Create the save buttons layout for username and teammates"""
        save_buttons_layout = QHBoxLayout()
        
        self.your_username_save_button = QPushButton("Save Username")
        self.your_username_save_button.clicked.connect(self.save_your_username)
        
        self.teammates_usernames_save_button = QPushButton("Save Teammates")
        self.teammates_usernames_save_button.clicked.connect(self.save_teammates_usernames)
        
        save_buttons_layout.addWidget(self.your_username_save_button)
        save_buttons_layout.addWidget(self.teammates_usernames_save_button)
        
        return save_buttons_layout

    def toggle_audio_alerts(self, state):
        """Toggle all audio alerts"""
        enabled = state == Qt.CheckState.Checked.value
        if self.resource_alerts_thread:
            self.resource_alerts_thread.enable_audio_alerts(enabled)
        api_client.create_action("toggle_audio_alerts", f"User {'enabled' if enabled else 'disabled'} audio alerts")

    def toggle_idle_villager_audio(self, state):
        """Toggle idle villager audio alert"""
        enabled = state == Qt.CheckState.Checked.value
        if self.resource_alerts_thread:
            self.resource_alerts_thread.enable_idle_villager_audio(enabled)
        api_client.create_action("toggle_idle_villager_audio", f"User {'enabled' if enabled else 'disabled'} idle villager audio alert")

    def test_api_key(self):
        """Test the API key"""
        api_key = self.api_key_input.text()
        self.verify_and_update_api_key(api_key)
        self.save_user_info()

    def update_villager_hotkey(self, new_hotkey):
        if new_hotkey:
            old_hotkey = self.villager_hotkey
            self.villager_hotkey = new_hotkey
            self.setup_hotkeys()
            self.save_user_info()
            logger.info(f"Villager hotkey updated from {old_hotkey} to: {self.villager_hotkey}")
        else:
            # If the input is empty, don't update the hotkey
            self.villager_hotkey_input.setText(self.villager_hotkey)
            logger.warning("Empty villager hotkey input")

    def update_castle_hotkey(self, new_hotkey):
        """Update the castle unit creation hotkey"""
        if new_hotkey:
            old_hotkey = self.castle_hotkey
            self.castle_hotkey = new_hotkey
            self.setup_hotkeys()
            self.save_user_info()
            logger.info(f"Castle hotkey updated from {old_hotkey} to: {self.castle_hotkey}")
        else:
            # If the input is empty, don't update the hotkey
            self.castle_hotkey_input.setText(self.castle_hotkey)
            logger.warning("Empty castle hotkey input")

    def eventFilter(self, obj, event):
        if (obj == self.villager_hotkey_input or obj == self.castle_hotkey_input) and event.type() == QKeyEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Backspace or event.key() == Qt.Key.Key_Delete:
                # Allow backspace and delete keys to function normally
                return False
            key = event.text()
            if key:
                if obj == self.villager_hotkey_input:
                    self.villager_hotkey_input.setText(key)
                    self.update_villager_hotkey(key)
                else:  # castle_hotkey_input
                    self.castle_hotkey_input.setText(key)
                    self.update_castle_hotkey(key)
            return True
        return super().eventFilter(obj, event)

    def update_start_button_text(self):
        ollama_ok = hasattr(self, 'ollama_status_indicator') and self.ollama_status_indicator.toolTip() == "Ollama Connected"
        
        if self.api_key_validated and ollama_ok:
            self.start_button.setText("Start Resource Alerts")
            self.start_button.setEnabled(True)
        elif not self.api_key_validated:
            self.start_button.setText("Activate API Key First")
            self.start_button.setEnabled(False)
        elif not ollama_ok:
            self.start_button.setText("Check Ollama Status")
            self.start_button.setEnabled(False)
        else: # Default fallback
            self.start_button.setText("Waiting for API and Ollama...")
            self.start_button.setEnabled(False)

    def create_ollama_status_layout(self):
        ollama_status_layout = QHBoxLayout()
        self.ollama_status_label_text = QLabel("Ollama Status:") # Static text label
        self.ollama_status_indicator = QLabel() # For the colored circle
        self.ollama_status_indicator.setFixedSize(16, 16)
        self.ollama_status_message_label = QLabel("Checking...") # For dynamic messages
        
        ollama_status_layout.addWidget(self.ollama_status_label_text)
        ollama_status_layout.addWidget(self.ollama_status_indicator)
        ollama_status_layout.addWidget(self.ollama_status_message_label)
        ollama_status_layout.addStretch()
        return ollama_status_layout

    def check_ollama_status(self):
       success, message = AIAnalysis.test_ollama_connection()

       if success:
           self.ollama_status_indicator.setStyleSheet("background-color: #90EE90; border-radius: 8px;")
           self.ollama_status_indicator.setToolTip("Ollama Connected")
           # Display only the main part of the success message, not the full details unless hovered.
           short_message = message.split('.')[0] if '.' in message else message
           self.ollama_status_message_label.setText(short_message)
           self.ollama_status_message_label.setToolTip(message) # Full message on hover
       else:
           self.ollama_status_indicator.setStyleSheet("background-color: #FFB6C1; border-radius: 8px;")
           self.ollama_status_indicator.setToolTip("Ollama Connection Error")
           # Display a concise error message, full details in popup and hover.
           short_error_message = message.split('.')[0] if '.' in message else message
           self.ollama_status_message_label.setText(f"Error: {short_error_message}")
           self.ollama_status_message_label.setToolTip(message) # Full message on hover
           QMessageBox.warning(self, "Ollama Connection Error", message)
       self.update_start_button_text()

    def toggle_castle_unit_creation(self, state):
        """Toggle the castle unit creation feature"""
        if state == Qt.CheckState.Checked.value:
            GameActions.enable_castle_unit_creation()
            api_client.create_action("enable_castle_unit_creation", "User enabled auto castle unit creation")
        else:
            GameActions.disable_castle_unit_creation()
            api_client.create_action("disable_castle_unit_creation", "User disabled auto castle unit creation")
        self.setup_hotkeys()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def exception_hook(exctype, value, tb):
    """
    Global function to catch unhandled exceptions.
    """
    traceback_formated = traceback.format_exception(exctype, value, tb)
    traceback_string = "".join(traceback_formated)
    
    # Print to stderr (as before)
    print(f"Unhandled Exception: {exctype.__name__}: {str(value)}\n{traceback_string}", file=sys.stderr)

    # Log to local file using the logger from utils.py
    log_message = f"Unhandled global exception caught by exception_hook:\nType: {exctype.__name__}\nValue: {str(value)}\nTraceback:\n{traceback_string}"
    logger.critical(log_message)

    # Then, attempt to log via API client
    api_error_message = f"Unhandled exception: {exctype.__name__}: {str(value)}\n{traceback_string}"
    try:
        api_client.create_action("crash", api_error_message)
        logger.info("Successfully reported crash to API.")
    except Exception as api_e:
        logger.error(f"Failed to report crash to API: {api_e}")
    
    sys.exit(1) # Consider if sys.exit is always appropriate, but for now, keep it.

def main():
    """Main function to run the application"""
    # Set the exception hook
    sys.excepthook = exception_hook

    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if not is_admin():
            # If not running as admin, show a message box and restart with admin rights
            ctypes.windll.user32.MessageBoxW(0, "WololoGPT requires administrator privileges to use keyboard shortcuts. Please click 'Yes' in the next prompt to run as administrator.", "Administrator Rights Required", 0x30)
            run_as_admin()
            sys.exit()
    
    app = QApplication([])
    window = MainWindow()
    
    # Set the application icon
    icon_path = resource_path("images/logo.jpg")
    app.setWindowIcon(QIcon(icon_path))
    window.setWindowIcon(QIcon(icon_path))
    
    if window.windowIcon().isNull():
        logger.error(f"Failed to load window icon from: {icon_path}")
    window.show()

    # Create a timer to process color flashes
    timer = QTimer()
    timer.timeout.connect(process_color_flashes)
    timer.start(100)  # Process every 100ms

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
