import pyautogui
import json

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

API_KEYS = {
    "GROQ": "",
    "GOOGLE": ""  # This will be set by the user
}

def set_api_key(key):
    API_KEYS["GOOGLE"] = key

AUDIO_VOLUME = 0.35

RESOURCE_SCREENSHOT_REGION, CIV_SCREENSHOT_REGION = get_screenshot_regions()

RESOURCE_CHECK_PROMPT = """
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

def get_civ_counter_prompt(username, teammates):
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
CIV_COUNTER_PROMPT = get_civ_counter_prompt(username, teammates)

# Existing constants
# DEFAULT_USERNAME = "vincent@wololo.gpt"
# DEFAULT_PASSWORD = "test"

# New constants
RESOURCE_CHECK_INTERVAL = 15  # seconds
VILLAGER_WARNING_INTERVAL = 50  # seconds

# You may want to add or adjust other constants as needed

API_BASE_URL = "http://api.wolologpt.com"
