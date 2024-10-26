from groq import Groq
from config import API_KEYS, RESOURCE_CHECK_PROMPT, CIV_COUNTER_PROMPT
import google.generativeai as genai
import time
import os
import json
from utils import show_popup_message, logger, resource_path

class AIAnalysis:
    @staticmethod
    def analyze_civ_screenshot(image_path, api_key, prompt):
        return AIAnalysis.analyze_image_gemini(image_path, prompt, api_key)

    @staticmethod
    def transcribe_audio(audio_path, api_key):
        client = Groq(api_key=api_key)
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3"
            )
        return transcription.text

    @staticmethod
    def analyze_image_gemini(filename, prompt, api_key):
        genai.configure(api_key=api_key)

        generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=prompt,
        )

        file = AIAnalysis.upload_to_gemini(filename, mime_type="image/png")

        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                chat_session = model.start_chat(
                    history=[
                        {
                            "role": "user",
                            "parts": [file],
                        }
                    ]
                )

                response = chat_session.send_message("go.")
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"All {max_retries} attempts failed. Last error: {str(e)}")
                    return None

    #test the api key
    @staticmethod
    def test_google_api_key(api_key):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Ping.")
            if response.text:
                logger.info("API key test successful")
                return True, "API key is valid and working correctly."
            else:
                logger.warning("API key test failed: No response received")
                return False, "API key test failed: No response received from the API."
        except Exception as e:
            logger.error(f"API key test failed: {str(e)}")
            return False, f"API key test failed: {str(e)}"

    @staticmethod
    def upload_to_gemini(path, mime_type=None, api_key=None):
        """Uploads the given file to Gemini.

        See https://ai.google.dev/gemini-api/docs/prompting_with_media
        """
        if api_key:
            genai.configure(api_key=api_key)
        while True:
            try:
                start_time = time.time()
                file = genai.upload_file(path, mime_type=mime_type)
                upload_time = time.time() - start_time
                if upload_time > 10:
                    print(f"Upload took {upload_time:.2f} seconds. Retrying...")
                    continue
                print(f"Uploaded file '{file.display_name}' as: {file.uri}")
                return file
            except Exception as e:
                print(f"Upload failed: {e}. Retrying...")
            time.sleep(1)

    @staticmethod
    def get_counters_for_civs(civ_analysis_output):
        """
        Takes the output from analyze_civ_screenshot and finds appropriate counters
        for each civilization's unique units.

        Args:
        civ_analysis_output (str): A JSON string containing civilization information.

        Returns:
        str: A formatted string containing counter information for each civilization.
        """
        try:
            # Parse the JSON string into a Python dictionary
            civ_analysis = json.loads(civ_analysis_output)
            
            counter_data_path = resource_path('counters_data/aoe2_counter_unique_gemini.json')
            with open(counter_data_path, 'r') as f:
                counter_data = json.load(f)
                #print(counter_data)
        except FileNotFoundError:
            return "Error: Counter data file not found."
        except json.JSONDecodeError:
            return "Error: Invalid JSON in counter data file or civ analysis output."

        counter_info = []

        for civ in civ_analysis.values():
            if civ in counter_data:
                civ_info = counter_data[civ]
                unique_units = civ_info.get('unique_units', [])
                counters = civ_info.get('counters', {})
                units_to_avoid = civ_info.get('units_to_avoid', {})
                tips = civ_info.get('tips', '')

                civ_counter_info = f"<h2>{civ}</h2>"
                civ_counter_info += f"<p><strong>Unique Units:</strong> {', '.join(unique_units)}</p>"

                if isinstance(counters, dict):
                    civ_counter_info += "<ul>"
                    for unit, unit_counters in counters.items():
                        civ_counter_info += f"<li><strong>{unit}:</strong> {', '.join(unit_counters)}</li>"
                    civ_counter_info += "</ul>"
                else:
                    civ_counter_info += f"<p><strong>Counters:</strong> {', '.join(counters)}</p>"

                if isinstance(units_to_avoid, dict):
                    civ_counter_info += "<ul>"
                    for unit, avoid_units in units_to_avoid.items():
                        civ_counter_info += f"<li><strong>Units to avoid for {unit}:</strong> {', '.join(avoid_units)}</li>"
                    civ_counter_info += "</ul>"
                else:
                    civ_counter_info += f"<p><strong>Units to avoid:</strong> {', '.join(units_to_avoid)}</p>"

                civ_counter_info += f"<p><strong>Tips:</strong> {tips}</p>"
                counter_info.append(civ_counter_info)
            else:
                counter_info.append(f"<p>No counter information available for {civ}.</p>")

        return "\n".join(counter_info)
    
if __name__ == "__main__":
    # Load default API key from user_info.json
    with open('user_info.json', 'r') as f:
        user_info = json.load(f)
        default_api_key = user_info.get('api_key', '')

    # Ask for user input for API key
    api_key = input(f"Enter API key to test (press Enter to use default: {default_api_key}): ").strip() or default_api_key

    # Create an instance of AIAnalysis
    ai_analyzer = AIAnalysis()

    while True:
        print("\nWhat would you like to test?")
        print("1. Resource analysis")
        print("2. Civilization analysis")
        print("3. API key")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            resource_test_image_path = "images/test_resource.jpg"
            if os.path.exists(resource_test_image_path):
                resource_test_prompt = RESOURCE_CHECK_PROMPT
                try:
                    resource_result = ai_analyzer.analyze_image_gemini(resource_test_image_path, resource_test_prompt, api_key)
                    print("Resource analysis result:")
                    print(resource_result)
                except Exception as e:
                    print(f"An error occurred during resource testing: {e}")
            else:
                print(f"Resource test image not found at {resource_test_image_path}. Please ensure a test image is available.")

        elif choice == '2':
            civ_test_image_path = "images/test_civ.jpg"
            if os.path.exists(civ_test_image_path):
                try:
                    civ_result = ai_analyzer.analyze_civ_screenshot(civ_test_image_path, api_key, CIV_COUNTER_PROMPT)
                    print("\nCiv analysis result:")
                    print(civ_result)
                    counters = ai_analyzer.get_counters_for_civs(civ_result)
                    print("\nCiv counters result:")
                    print(counters)
                    
                except Exception as e:
                    print(f"An error occurred during civ counters check: {e}")
            else:
                print(f"Civ test image not found at {civ_test_image_path}. Please ensure a test image is available.")

        elif choice == '3':
            print("Testing API key...")
            success, message = AIAnalysis.test_google_api_key(api_key)
            if success:
                print("API key test successful.")
            else:
                print(f"API key test failed: {message}")

        elif choice == '4':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
