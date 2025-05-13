import pyautogui
import json
import os
from utils import resource_path, logger

def get_screenshot_regions():
    screen_width, screen_height = pyautogui.size()
    
    # Adjust the regions based on screen resolution
    resource_width = min(1200, screen_width)
    resource_height = int(screen_height * 0.05)  # 5% of screen height
    
    civ_width = min(500, screen_width)
    civ_height = int(screen_height * 0.25)  # 25% of screen height
    
    RESOURCE_SCREENSHOT_REGION = (0, 0, resource_width, resource_height)
    CIV_SCREENSHOT_REGION = (screen_width - civ_width, screen_height - civ_height, civ_width, civ_height)
    
    return RESOURCE_SCREENSHOT_REGION, CIV_SCREENSHOT_REGION

# AI Models Configuration
AI_CONFIG = {
    "default_models": {
        "image": "gemma3:4b-it-qat",    # 4B quantized multimodal model
        "audio": "whisper",              # Specialized audio model
        "fallback": "gemma3:1b-it-qat",  # Smaller model for low-resource systems
        "text": "gemma3:7b"              # Full-size text model for complex reasoning
    },
    "options": {
        "temperature": 0.1,              # Lower temperature for more consistent outputs
        "num_gpu": 1,                    # Use 1 GPU
        "num_thread": 4,                 # Limit threads to not impact game performance
        "rope_frequency_base": 10000,    # Standard RoPE settings
        "rope_frequency_scale": 1.0,
    }
}

# Legacy API keys (kept for backward compatibility)
API_KEYS = {
    "GROQ": "",
    "GOOGLE": ""  # This will be set by the user
}

def set_api_key(key):
    API_KEYS["GOOGLE"] = key

AUDIO_VOLUME = 0.35

RESOURCE_SCREENSHOT_REGION, CIV_SCREENSHOT_REGION = get_screenshot_regions()

# Define paths for prompt files
RESOURCE_CHECK_PROMPT_PATH = resource_path('prompts/resource_check_prompt.txt')
CIV_COUNTER_PROMPT_PATH = resource_path('prompts/civ_counter_prompt.txt')

# Ensure prompt directories exist
os.makedirs(os.path.dirname(RESOURCE_CHECK_PROMPT_PATH), exist_ok=True)
os.makedirs(os.path.dirname(CIV_COUNTER_PROMPT_PATH), exist_ok=True)

# Load prompts from files if they exist
def load_prompt_from_file(file_path, default_prompt):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Prompt file not found at {file_path}, using default prompt")
        
        # Write default prompt to file for future use
        try:
            with open(file_path, 'w') as f:
                f.write(default_prompt)
        except Exception as e:
            logger.error(f"Failed to write default prompt to file: {str(e)}")
            
        return default_prompt

# Default prompts
DEFAULT_RESOURCE_CHECK_PROMPT = """
You are a Age of empires 2 data analyst. You are given a screenshot of the resource bar of a live match. You must OCR the text correctly

        The information is how the information is presented every time: the small numbers at the bottom right of each icon represent the number of villagers working on the resource. The bigger number on the right of each icon is the resource count. Underneath the two person icon is the number_of_villagers. At the right of that, in XX/XXX format (example: 5/10) is the (number of total units / house limit), and the number of idle villagers is in red in a bell shape icon if any. Provide separate values..

        Output the variables in JSON:.

        ##Resources

        Wood, Food, Gold, Stone


        ##Villagers_on_resource
        Wood, Food, Gold, Stone

        #Villagers
        number_of_villagers
        
        #Idle Villagers
        number_of_idle_villagers

        ##Units
        number of total units, 
        Current House limit

        ##Current_age

        ##Time
        Time since beginning

        Always respect the JSON format:
        example :
        {"Resources": {"Wood": "200", "Food": "200", "Gold": "100", "Stone": "200"}, "Villagers_on_resource": {"Wood": "0", "Food": "0", "Gold": "0", "Stone": "0"}, "Villagers": "3", "Units": {"number of total units": "4", "Current House limit": "5"}, "Idle Villagers": "2", "Current_age": "Imperial Age", "Time": "00:22:44"}
        
        IMPORTANT: If you can't find any relevant information or all values are 0, always return: 0 for all values.}
"""

def get_default_civ_counter_prompt(username, teammates):
    base_prompt = """
        You are an Age of Empires 2 screenshot analyst. You are given a screenshot of the civilization selection screen of a live match. You must OCR the text correctly.

        The information is presented as follows: three letters represent the civilization. You can also identify the civilization emblem to help you. Each players name is in-line with their civilization.
        
        example:
        AZT - Aztecs
        BEN - Bengals
        BER - Berbers
        BOH - Bohemians
        BRI - Britons
        BUL - Bulgarians
        BRG - Burgundians
        BRM - Burmese
        BYZ - Byzantines
        CEL - Celts
        CHI - Chinese
        CUM - Cumans
        DRA - Dravidians
        ETI - Ethiopians
        FRA - Franks
        GOT - Goths
        GUR - Gurjaras
        HUN - Huns
        INC - Incas
        HIN - Indians
        ITA - Italians
        JAP - Japanese
        KHM - Khmer
        KOR - Koreans
        LIT - Lithuanians
        MAG - Magyars
        MLY - Malay
        MLI - Malians
        MAY - Mayans
        MON - Mongols
        PER - Persians
        POL - Poles
        POR - Portuguese
        SAR - Saracens
        SIC - Sicilians
        SLA - Slavs
        SPA - Spanish
        TAT - Tatars
        TEU - Teutons
        TUR - Turks
        VIE - Vietnamese
        VIK - Vikings
                

        Output the detected player's name and their respective civilizations in JSON format. 
        
        example: {{"Chagatai Khan": "Mongols", "King Alfonso": "Spanish", "László I": "Magyars"}}
        
        Important, return the full civilization name. NOT just the three letters.

        Do not return players with the following name: {username}, {teammates}
        """
    return base_prompt.format(username=username, teammates=teammates)

def load_user_info():
    try:
        with open("user_info.json", "r") as f:
            user_info = json.load(f)
        return user_info.get("your_username", ""), user_info.get("teammates_usernames", "")
    except FileNotFoundError:
        return "", ""

username, teammates = load_user_info()

# Load prompts from files or use defaults
RESOURCE_CHECK_PROMPT = load_prompt_from_file(RESOURCE_CHECK_PROMPT_PATH, DEFAULT_RESOURCE_CHECK_PROMPT)
CIV_COUNTER_PROMPT = load_prompt_from_file(CIV_COUNTER_PROMPT_PATH, get_default_civ_counter_prompt(username, teammates))

# Timing constants
RESOURCE_CHECK_INTERVAL = 15  # seconds
VILLAGER_WARNING_INTERVAL = 50  # seconds
OLLAMA_CONNECTION_RETRY_INTERVAL = 30  # seconds

# Paths to data files
COUNTERS_DATA_PATH = resource_path('counters_data/aoe2_counter_unique_gemini.json')

# App configuration
API_BASE_URL = "http://api.wolologpt.com"
ENABLE_API_TRACKING = True  # Can be toggled in settings

# Feature flags
USE_OLLAMA = True  # Set to False to use API-based services instead
