# WololoGPT

## About the Project
Visit our official website at [http://wolologpt.com](http://wolologpt.com) to watch the video demo.


WololoGPT is an intelligent assistant for Age of Empires II players, designed to enhance gameplay by providing real-time alerts and insights. This tool helps players manage their resources more effectively, avoid common pitfalls, and improve their overall strategy.

## Why It Was Created

As Age of Empires II players ourselves, we recognized the challenge of managing multiple aspects of the game simultaneously. It's easy to forget to create villagers, get housed, or let resources float. This tool was created to address these common issues and help players focus on strategy and decision-making rather than routine resource management.

## What It Solves

WololoGPT solves several key challenges:

1. **Resource Management**: Alerts players when resources are floating or when they need to build houses.
2. **Villager Production**: Reminds players to keep creating villagers throughout the game.
3. **Idle Villager Detection**: Notifies players when they have idle villagers.
4. **Civilization Counters**: Provides quick access to civilization-specific counter strategies.

## Features

- Real-time audio and visual alerts for resource management
- Automatic villager creation option
- Civilization counter information at the press of a hotkey
- Customizable alert settings

## Requirements

To run AoE2 Resource Alerts, you need:

1. Python 3.7 or higher
2. Required Python packages (see requirements.txt):
   - PyQt6
   - google-cloud-vision
   - google-generativeai
   - pillow
   - pygame
   - pyautogui
   - keyboard
   - And other dependencies listed in requirements.txt
3. Google Cloud Vision API key
4. Age of Empires II: Definitive Edition

## Required Mods

To get the most out of WololoGPT, you need to install the following mods:

- **Anne_HK - Better Resource Panel and Idle Villager Icon**
  This mod enhances the in-game resource panel and adds a clear idle villager icon, which our tool uses for more accurate detection and alerts.

- **TextCivEmblems**
  This mod is required for the civilization counter feature to work correctly.

## Installation

1. Clone this repository
2. Install required Python packages: `pip install -r requirements.txt`
3. Set up your Google Cloud Vision API key
4. Install the required mods in Age of Empires II: Definitive Edition
5. Run `python main.py` to start the application

## Usage

1. Start Age of Empires II: Definitive Edition
2. Launch AoE2 Resource Alerts
3. Enter your API key and customize settings
4. Click "Start Resource Alerts" to begin monitoring your game

## Contributing

We welcome contributions to AoE2 Resource Alerts! Please feel free to submit pull requests or open issues for any bugs or feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to Anne_HK for the Better Resource Panel and Idle Villager Icon mod
- The Age of Empires II community for their continued support and feedback
