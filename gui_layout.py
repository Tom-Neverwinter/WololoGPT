from PyQt6.QtWidgets import (QVBoxLayout, QPushButton, QLineEdit, 
                             QLabel, QCheckBox, QHBoxLayout, QComboBox)
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
    layout = QVBoxLayout()

    # Logo
    logo_label = QLabel(window)
    logo_path = resource_path("images/logo.jpg")
    logo_pixmap = QPixmap(logo_path)
    if not logo_pixmap.isNull():
        logo_label.setPixmap(logo_pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
    else:
        logger.error(f"Failed to load logo from: {logo_path}")
        logo_label.setText("Logo not available")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

    # Instructions link (moved above API key input)
    instructions_link = QLabel('Welcome to <b>WololoGPT!</b> <a href="https://wolologpt.com/?utm_source=program&utm_medium=app_link">Click Here for Instructions</a>')
    instructions_link.setOpenExternalLinks(True)
    instructions_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(instructions_link)

    # Google LLM API Key input
    api_key_layout = QHBoxLayout()
    api_key_label = QLabel("Google LLM API Key:", window)
    window.api_key_input = QLineEdit(window)
    window.api_key_test_button = QPushButton("Activate API Now", window)
    api_key_layout.addWidget(api_key_label)
    api_key_layout.addWidget(window.api_key_input)
    api_key_layout.addWidget(window.api_key_test_button)
    layout.addLayout(api_key_layout)
    
    # Separation line
    separator = QLabel()
    separator.setFrameShape(QLabel.Shape.HLine)
    separator.setFrameShadow(QLabel.Shadow.Sunken)
    layout.addWidget(separator)

    # Your username input with save button
    username_layout = QHBoxLayout()
    username_label = QLabel("Your Username:", window)
    username_label.setFixedWidth(120)  # Set a fixed width for the label
    window.your_username_input = QLineEdit(window)
    window.your_username_input.setPlaceholderText("Your Username")
    window.your_username_save_button = QPushButton("Save", window)
    window.your_username_save_button.setFixedWidth(60)  # Set a fixed width for the button
    username_layout.addWidget(username_label)
    username_layout.addWidget(window.your_username_input)
    username_layout.addWidget(window.your_username_save_button)
    layout.addLayout(username_layout)

    # Teammates' usernames input with save button
    teammates_layout = QHBoxLayout()
    teammates_label = QLabel("Teammates' Usernames:", window)
    teammates_label.setFixedWidth(120)  # Set a fixed width for the label
    window.teammates_usernames_input = QLineEdit(window)
    window.teammates_usernames_input.setPlaceholderText("Teammates' Usernames (comma-separated)")
    window.teammates_usernames_save_button = QPushButton("Save", window)
    window.teammates_usernames_save_button.setFixedWidth(60)  # Set a fixed width for the button
    teammates_layout.addWidget(teammates_label)
    teammates_layout.addWidget(window.teammates_usernames_input)
    teammates_layout.addWidget(window.teammates_usernames_save_button)
    layout.addLayout(teammates_layout)
    
    # Separation line
    separator = QLabel()
    separator.setFrameShape(QLabel.Shape.HLine)
    separator.setFrameShadow(QLabel.Shadow.Sunken)
    layout.addWidget(separator)

    # Resource alerts buttons
    window.start_button = QPushButton("Start Resource Alerts", window)
    layout.addWidget(window.start_button)

    window.stop_button = QPushButton("Stop Resource Alerts", window)
    window.stop_button.setEnabled(False)
    layout.addWidget(window.stop_button)

    # Villager creation checkbox and hotkey input
    villager_layout = QHBoxLayout()
    window.villager_checkbox = QCheckBox("Enable Auto Villager Creation", window)
    window.villager_checkbox.setChecked(True)
    villager_layout.addWidget(window.villager_checkbox)

    window.villager_hotkey_label = QLabel("Hotkey:", window)
    window.villager_hotkey_input = QLineEdit(window)
    window.villager_hotkey_input.setFixedWidth(50)  # Increased width to accommodate longer keys
    window.villager_hotkey_input.setMaxLength(10)  # Increased max length for combination keys
    villager_layout.addWidget(window.villager_hotkey_label)
    villager_layout.addWidget(window.villager_hotkey_input)

    layout.addLayout(villager_layout)

    # Civ counters hotkey checkbox
    window.civ_counters_checkbox = QCheckBox("Enable Civ Counters Hotkey (ctrl+.)", window)
    window.civ_counters_checkbox.setChecked(True)
    layout.addWidget(window.civ_counters_checkbox)

    # Color flash alerts checkbox
    window.color_flash_checkbox = QCheckBox("Enable Color Flash Alerts", window)
    window.color_flash_checkbox.setChecked(True)
    layout.addWidget(window.color_flash_checkbox)

    # Add audio alerts checkbox
    window.audio_alerts_checkbox = QCheckBox("Enable Resource & House Audio Alerts", window)
    window.audio_alerts_checkbox.setChecked(True)  # Enable by default
    layout.addWidget(window.audio_alerts_checkbox)

    # Add idle villager audio alert checkbox
    window.idle_villager_audio_checkbox = QCheckBox("Enable Idle Villager Audio Alert", window)
    window.idle_villager_audio_checkbox.setChecked(True)  # Enable by default
    layout.addWidget(window.idle_villager_audio_checkbox)


    return layout
