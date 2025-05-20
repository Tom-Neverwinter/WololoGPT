# WololoGPT

<img src="https://github.com/tony-png/WololoGPT-1.0.0---Github-Official/blob/main/images/logo.jpg?raw=true" width="200" alt="WololoGPT Logo">

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
3. ollama and gemma 3 [4B it-qat preferred]
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
3. install ollama and gemma 3
4. Install the required mods in Age of Empires II: Definitive Edition
5. Run `python main.py` to start the application

## Development Environment Setup with `pyenv`

For developers contributing to WololoGPT or setting up a more controlled Python environment, using `pyenv` is highly recommended. This allows you to manage multiple Python versions and ensure a clean setup.

### 1. Pre-install Python Build Dependencies

Before using `pyenv install <python_version>`, it's crucial to install common Python build dependencies on your operating system. This prevents many common issues during Python compilation.

*   **For Ubuntu/Debian-based Linux:**
    ```bash
    sudo apt-get update
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
    ```
*   **For macOS (using Homebrew):**
    ```bash
    brew install openssl readline sqlite3 xz zlib tcl-tk
    ```
    *Note for macOS*: You might also need to set `CFLAGS` and `LDFLAGS` environment variables for `pyenv` to correctly find these Homebrew-installed libraries during Python compilation. Refer to `pyenv` documentation and Homebrew notes for `openssl` and `tcl-tk`.

### 2. Ensuring Ollama Accessibility

WololoGPT relies on Ollama for its AI capabilities.
*   **Ollama Installation**: Ensure Ollama is installed and running as a separate service on your system. You can download it from [ollama.com](https://ollama.com/).
*   **Default Connection**: The application connects to Ollama by default at `http://localhost:11434`.
*   **Firewall**: If you experience connection issues with Ollama, ensure your firewall is not blocking this local connection.

### 3. Virtual Environment and Dependencies

Once `pyenv` and the desired Python version (e.g., 3.9, 3.10) are set up:

1.  **Create a Virtual Environment**:
    ```bash
    pyenv virtualenv <python_version> wolologpt-env
    ```
2.  **Activate the Environment**:
    ```bash
    pyenv activate wolologpt-env
    ```
    Alternatively, you can set a local `pyenv` version for the project directory:
    ```bash
    pyenv local wolologpt-env
    ```
    Or, if you just installed a Python version (e.g., 3.10.0) and want to create a venv directly:
    ```bash
    python -m venv .venv
    source .venv/bin/activate # On Linux/macOS
    # .venv\Scripts\activate # On Windows
    ```
3.  **Install Dependencies**: With the virtual environment activated, install the project dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 4. Troubleshooting GUI Issues

*   **Tkinter Support**: If GUI elements don't appear correctly or you encounter errors related to `tkinter`, ensure that your Python version was compiled with Tkinter support. Installing the `tk-dev` (or equivalent, like `tcl-tk` via Homebrew) package *before* installing the Python version with `pyenv` is crucial (see Point 1).
*   **PyQt6 Issues**: The `PyQt6` package in `requirements.txt` bundles the necessary Qt6 libraries (`PyQt6-Qt6`). However, if you encounter persistent issues, especially on Linux, ensuring system-level Qt6 development packages (e.g., `qt6-base-dev` on Debian/Ubuntu) are installed can sometimes help, though this should ideally not be necessary. Always ensure your virtual environment is correctly activated and `pip install` commands are run within it.

## Usage

1. Start Age of Empires II: Definitive Edition
2. Launch AoE2 Resource Alerts
3. run ollama and gemma 3
4. Click "Start Resource Alerts" to begin monitoring your game

## Contributing

We welcome contributions to AoE2 Resource Alerts! Please feel free to submit pull requests or open issues for any bugs or feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to Anne_HK for the Better Resource Panel and Idle Villager Icon mod
- The Age of Empires II community for their continued support and feedback
