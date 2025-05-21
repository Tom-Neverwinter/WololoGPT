from PyQt6.QtWidgets import (QVBoxLayout, QPushButton, QLineEdit, 
                             QLabel, QCheckBox, QHBoxLayout, QComboBox,
                             QTabWidget, QWidget) # Added QTabWidget, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from game_actions import GameActions
import os
import sys
from utils import logger  # Import the logger from utils

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_main_layout(window):
    # This is the overall layout for the window.
    # It will contain elements common to all views (like logo, instructions)
    # and then the tab widget for specific sections.
    overall_layout = QVBoxLayout() 

    # Logo
    logo_label = QLabel(window)
    logo_path = resource_path("images/logo.jpg")
    logo_pixmap = QPixmap(logo_path)
    if not logo_pixmap.isNull():
        logo_label.setPixmap(logo_pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overall_layout.addWidget(logo_label)
    else:
        logger.error(f"Failed to load logo from: {logo_path}")
        logo_label.setText("Logo not available")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overall_layout.addWidget(logo_label)

    # Instructions link
    instructions_link = QLabel('Welcome to <b>WololoGPT!</b> <a href="https://wolologpt.com/?utm_source=program&utm_medium=app_link">Click Here for Instructions</a>')
    instructions_link.setOpenExternalLinks(True)
    instructions_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
    overall_layout.addWidget(instructions_link)

    # --- Create Tab structure ---
    tab_widget = QTabWidget(window)

    general_tab = QWidget()
    alerts_tab = QWidget()
    automation_tab = QWidget()

    # Store tab layouts on the window object for access in subsequent steps
    window.general_tab_layout = QVBoxLayout()
    general_tab.setLayout(window.general_tab_layout)
    
    window.alerts_tab_layout = QVBoxLayout()
    alerts_tab.setLayout(window.alerts_tab_layout)
    
    window.automation_tab_layout = QVBoxLayout()
    automation_tab.setLayout(window.automation_tab_layout)

    tab_widget.addTab(general_tab, "General")
    tab_widget.addTab(alerts_tab, "Alerts")
    tab_widget.addTab(automation_tab, "Automation")

    overall_layout.addWidget(tab_widget) # Add the tab widget to the main layout

    # --- Existing widget CREATION (attributes on `window`) ---
    # These are created as attributes on `window`.
    # Their `overall_layout.addWidget/addLayout` calls are NOT removed in this step.
    # They will be moved to the tab layouts in subsequent steps.
    # This means they will temporarily appear above or within the first tab by default.

    # Google LLM API Key input (REMOVED)
    # api_key_layout = QHBoxLayout() 
    # api_key_label = QLabel("Google LLM API Key:", window)
    # window.api_key_input = QLineEdit(window)
    # window.api_key_test_button = QPushButton("Activate API Now", window)
    # api_key_layout.addWidget(api_key_label)
    # api_key_layout.addWidget(window.api_key_input)
    # api_key_layout.addWidget(window.api_key_test_button)
    # window.general_tab_layout.addLayout(api_key_layout) 
    
    # Separation line (REMOVED as it was for the API key section)
    # separator1 = QLabel() 
    # separator1.setFrameShape(QLabel.Shape.HLine)
    # separator1.setFrameShadow(QLabel.Shadow.Sunken)
    # window.general_tab_layout.addWidget(separator1)

    # Your username input with save button
    username_layout = QHBoxLayout() 
    username_label = QLabel("Your Username:", window)
    username_label.setFixedWidth(120)
    window.your_username_input = QLineEdit(window)
    window.your_username_input.setPlaceholderText("Your Username")
    window.your_username_save_button = QPushButton("Save", window)
    window.your_username_save_button.setFixedWidth(60)
    username_layout.addWidget(username_label)
    username_layout.addWidget(window.your_username_input)
    username_layout.addWidget(window.your_username_save_button)
    window.general_tab_layout.addLayout(username_layout) # Moved to general_tab_layout

    # Teammates' usernames input with save button
    teammates_layout = QHBoxLayout() 
    teammates_label = QLabel("Teammates' Usernames:", window)
    teammates_label.setFixedWidth(120)
    window.teammates_usernames_input = QLineEdit(window)
    window.teammates_usernames_input.setPlaceholderText("Teammates' Usernames (comma-separated)")
    window.teammates_usernames_save_button = QPushButton("Save", window)
    window.teammates_usernames_save_button.setFixedWidth(60)
    teammates_layout.addWidget(teammates_label)
    teammates_layout.addWidget(window.teammates_usernames_input)
    teammates_layout.addWidget(window.teammates_usernames_save_button)
    window.general_tab_layout.addLayout(teammates_layout) # Moved to general_tab_layout
    
    # Separation line
    separator2 = QLabel() 
    separator2.setFrameShape(QLabel.Shape.HLine)
    separator2.setFrameShadow(QLabel.Shadow.Sunken)
    window.general_tab_layout.addWidget(separator2) # Moved to general_tab_layout

    # Resource alerts buttons
    window.start_button = QPushButton("Start Resource Alerts", window)
    window.general_tab_layout.addWidget(window.start_button) # Moved to general_tab_layout
    window.stop_button = QPushButton("Stop Resource Alerts", window)
    window.stop_button.setEnabled(False)
    window.general_tab_layout.addWidget(window.stop_button) # Moved to general_tab_layout

    # Villager creation checkbox and hotkey input
    villager_layout = QHBoxLayout() 
    window.villager_checkbox = QCheckBox("Enable Auto Villager Creation", window)
    window.villager_checkbox.setChecked(True)
    villager_layout.addWidget(window.villager_checkbox)
    window.villager_hotkey_label = QLabel("Hotkey:", window)
    window.villager_hotkey_input = QLineEdit(window)
    window.villager_hotkey_input.setFixedWidth(50)
    window.villager_hotkey_input.setMaxLength(10)
    villager_layout.addWidget(window.villager_hotkey_label)
    villager_layout.addWidget(window.villager_hotkey_input)
    window.automation_tab_layout.addLayout(villager_layout) # Moved to automation_tab_layout
    
    # Automatic Villager Boost checkbox
    window.auto_villager_boost_checkbox = QCheckBox("Enable Automatic Villager Boost (Periodic Check)", window)
    window.auto_villager_boost_checkbox.setChecked(False)
    window.auto_villager_boost_checkbox.setToolTip("If checked, periodically checks and queues villagers to meet age-based targets automatically.")
    window.automation_tab_layout.addWidget(window.auto_villager_boost_checkbox) # Moved to automation_tab_layout

    # Castle unit creation checkbox and hotkey input
    castle_layout = QHBoxLayout() 
    window.castle_checkbox = QCheckBox("Enable Auto Castle Unit Creation", window)
    window.castle_checkbox.setChecked(True)
    castle_layout.addWidget(window.castle_checkbox)
    window.castle_hotkey_label = QLabel("Hotkey:", window)
    window.castle_hotkey_input = QLineEdit(window)
    window.castle_hotkey_input.setFixedWidth(50)
    window.castle_hotkey_input.setMaxLength(10)
    castle_layout.addWidget(window.castle_hotkey_label)
    castle_layout.addWidget(window.castle_hotkey_input)
    window.automation_tab_layout.addLayout(castle_layout) # Moved to automation_tab_layout

    # Civ counters hotkey checkbox
    window.civ_counters_checkbox = QCheckBox("Enable Civ Counters Hotkey (ctrl+.)", window)
    window.civ_counters_checkbox.setChecked(True)
    window.automation_tab_layout.addWidget(window.civ_counters_checkbox) # Moved to automation_tab_layout

    # Color flash alerts checkbox
    window.color_flash_checkbox = QCheckBox("Enable Color Flash Alerts", window)
    window.color_flash_checkbox.setChecked(True)
    window.alerts_tab_layout.addWidget(window.color_flash_checkbox) # Moved to alerts_tab_layout

    # Add audio alerts checkbox
    window.audio_alerts_checkbox = QCheckBox("Enable Resource & House Audio Alerts", window)
    window.audio_alerts_checkbox.setChecked(True)
    window.alerts_tab_layout.addWidget(window.audio_alerts_checkbox) # Moved to alerts_tab_layout

    # Add idle villager audio alert checkbox
    window.idle_villager_audio_checkbox = QCheckBox("Enable Idle Villager Audio Alert", window)
    window.idle_villager_audio_checkbox.setChecked(True)
    window.alerts_tab_layout.addWidget(window.idle_villager_audio_checkbox) # Moved to alerts_tab_layout
    
    return overall_layout
