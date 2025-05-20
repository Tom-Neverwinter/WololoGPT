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

1. Python 3.9, 3.10, or 3.11. This is crucial for compatibility.
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

This project requires **Python 3.9, 3.10, or 3.11**.

1.  **Ensure you have a compatible Python version installed.**
    You can check your version with `python --version` or `py --version` (on Windows). If `python` points to an older version (like Python 2), try `python3 --version`. If you don't have a compatible version (3.9, 3.10, or 3.11), install one (e.g., from [python.org](https://www.python.org/downloads/) or using a version manager like `pyenv` - see "Development Environment Setup with `pyenv`" section).

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/tony-png/WololoGPT-1.0.0---Github-Official.git
    cd WololoGPT-1.0.0---Github-Official
    ```

3.  **Create a virtual environment (Recommended):**
    Using a virtual environment is highly recommended. Choose **one** of the following methods based on your operating system and installed Python version. Replace `3.10` with your chosen compatible version (e.g., `3.9`, `3.11`).

    *   **Windows (using the Python Launcher `py.exe`):**
        ```bash
        py -3.10 -m venv .venv
        ```
        This command explicitly uses Python 3.10. If you have it installed, `py.exe` should find it.

    *   **macOS / Linux (using version-specific command):**
        ```bash
        python3.10 -m venv .venv
        ```
        This command assumes `python3.10` (or `python3.9`, `python3.11`) is available in your PATH.

    *   **macOS / Linux (if `python3` points to a compatible version):**
        If your `python3` command already points to a compatible version (3.9, 3.10, or 3.11), you can use:
        ```bash
        python3 -m venv .venv
        ```
            
            *A Note on these Commands:*
            *   On **Windows**, `py -3.10` utilizes the Python Launcher (`py.exe`), which is typically installed with Python for Windows. If you have multiple Python versions (e.g., 3.9, 3.10, 3.11) installed, this command helps select the specific version (e.g., 3.10 in the command) for creating the environment. If the specified version isn't found, `py.exe` will usually report an error.
            *   On **macOS and Linux**, commands like `python3.10` require that the specific Python version's executable is installed and available in your system's PATH. This is often the case with standard installations (e.g., from source, via package managers like `apt` or `Homebrew`, or by tools like `pyenv`). If a command like `python3.10` is not found, it means either that specific Python version is not installed, or it's not correctly added to the PATH.
            
            *Remember to replace `3.10` in the example commands with your chosen compatible version (3.9, 3.10, or 3.11) based on the project's requirements and your installed Python versions.*

    *Note: If the version-specific command isn't found, ensure you've installed that Python version and it's added to your system's PATH. Using these specific commands helps ensure the virtual environment is created with the correct Python version, especially if you have multiple Python versions installed and are not using `pyenv` for this step.*

4.  **Activate the virtual environment:**
    -   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    -   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

5.  **Upgrade pip (inside the activated environment):**
    Once the virtual environment is activated, `python` will refer to the correct interpreter.
    ```bash
    python -m pip install --upgrade pip
    ```

6.  **Install dependencies (inside the activated environment):**
    ```bash
    pip install -r requirements.txt 
    ```
    *(Using `python -m pip install -r requirements.txt` is also a good practice).*

7.  **Install Ollama and Gemma 3:**
    WololoGPT uses Ollama with the Gemma 3 model (4B it-qat preferred) for its AI features.
    - Download and install Ollama from [ollama.com](https://ollama.com/).
    - Ensure Ollama is running.
    - Pull the Gemma 3 model: `ollama pull gemma2:2b-instruct-q4_0` (or your preferred Gemma 3 variant like `gemma:7b-instruct-q4_0` if your hardware supports it). The `gemma3:4b-it-qat` model mentioned in earlier docs might be a specific version you are using, adjust pull command as needed.

8.  **Install the required mods in Age of Empires II: Definitive Edition** (See "Required Mods" section above).

9.  **Run the application:**
    ```bash
    python main.py
    ```

## Development Environment Setup with `pyenv`

For developers, using `pyenv` helps manage specific Python versions (3.9, 3.10, or 3.11 as required by this project) and maintain a clean development environment.

### 1. Install `pyenv`
If you don't have `pyenv` installed, follow the official installation instructions for your operating system from the [pyenv GitHub repository](https://github.com/pyenv/pyenv#installation).

### 2. Pre-install Python Build Dependencies
Before installing a Python version with `pyenv`, install necessary build dependencies.

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

### 3. Install Required Python Version
Install a compatible Python version (e.g., 3.10.x, ensuring it's within the 3.9-3.11 range).
```bash
pyenv install 3.10.11 # Or another 3.9.x, 3.10.x, 3.11.x version
```

### 4. Create and Activate Virtual Environment
Set your local Python version for the project and create a virtual environment.
```bash
cd path/to/WololoGPT-1.0.0---Github-Official 
pyenv local 3.10.11 # Sets the version for this project directory
```
Create the virtual environment (choose one method):
   - Using `pyenv-virtualenv` (if installed as a `pyenv` plugin):
    ```bash
    pyenv virtualenv 3.10.11 wolologpt-env
    pyenv activate wolologpt-env 
    # or pyenv local wolologpt-env (to auto-activate when entering directory)
    ```
   - Using Python's built-in `venv` module (after `pyenv local`):
    ```bash
    python -m venv .venv 
    source .venv/bin/activate # On Linux/macOS
    # .venv\Scripts\activate # On Windows
    ```
    *Note: After setting your local Python version with `pyenv local 3.10.x` or activating a pyenv virtual environment (e.g., `pyenv activate wolologpt-env`), the `python` command within your shell will correctly refer to the version managed by `pyenv`. You can then proceed with `python -m venv .venv` (if you prefer an additional venv layer on top of the pyenv-selected Python version) and subsequent `python -m pip ...` commands.*

### 5. Upgrade Pip
Once the virtual environment is activated (either the one created by `pyenv virtualenv` or the one created via `python -m venv .venv`):
```bash
python -m pip install --upgrade pip
```

### 6. Install Dependencies
With the virtual environment activated and pip upgraded:
```bash
pip install -r requirements.txt
```
*(Using `python -m pip install -r requirements.txt` is also a good practice).*

### 7. Ensuring Ollama Accessibility
WololoGPT relies on Ollama for its AI capabilities.
*   **Ollama Installation**: Ensure Ollama is installed and running as a separate service on your system. You can download it from [ollama.com](https://ollama.com/).
    *   After installing Ollama, pull the required model: `ollama pull gemma2:2b-instruct-q4_0` (or your preferred Gemma 3 variant).
*   **Default Connection**: The application connects to Ollama by default at `http://localhost:11434`.
*   **Firewall**: If you experience connection issues with Ollama, ensure your firewall is not blocking this local connection.

### 8. Troubleshooting GUI Issues

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
