import requests
import time
import os
import json
import base64
from PIL import Image
import io
from utils import show_popup_message, logger, resource_path
import psutil  # For monitoring system resources

class AIAnalysis:
    # Payload options to optimize for game running
    optimization_options = {
        "temperature": 0.1,  # Lower temperature for more consistent outputs
        "num_gpu": 1,       # Use 1 GPU
        "num_thread": 4,    # Limit threads to not impact game performance
        "rope_frequency_base": 10000,  # Standard RoPE settings
        "rope_frequency_scale": 1.0,
    }
    @staticmethod
    def analyze_civ_screenshot(image_path, model_name="gemma3:4b-it-qat", prompt=None):
        """Analyze a civilization screenshot using Ollama's multimodal capabilities"""
        return AIAnalysis.analyze_image_ollama(image_path, prompt, model_name)

    @staticmethod
    def transcribe_audio(audio_path, model_name="whisper"):
        """Transcribe audio using Ollama's audio model"""
        try:
            # Convert audio to base64
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Create Ollama API request
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": model_name,
                "prompt": "Transcribe this audio accurately:",
                "stream": False,
                "options": {
                    "audio_data": base64.b64encode(audio_data).decode('utf-8')
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            return f"Transcription failed: {str(e)}"

    @staticmethod
    def analyze_image_ollama(image_path, prompt, model_name="gemma3:4b-it-qat"):
        """
        Analyze an image using Ollama's multimodal capabilities
        
        Args:
            image_path (str): Path to the image file
            prompt (str): System prompt for image analysis
            model_name (str): The Ollama model to use (default: gemma3:4b-it-qat)
            
        Returns:
            str: Analysis result in the requested format
        """
        try:
            # Check if Ollama is running first
            try:
                check_url = "http://localhost:11434/api/tags"
                check_response = requests.get(check_url, timeout=5)
                check_response.raise_for_status()
            except Exception as e:
                logger.error(f"Ollama server is not accessible: {str(e)}")
                return "Error: Ollama is not running or accessible. Please start Ollama service."
                
            # Check if image exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found at {image_path}")
            
            # Optimize image if needed
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Resize if too large (Gemma models work well with images up to 1024px)
                max_size = 1024
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.LANCZOS)
                
                # Save to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                img_byte_arr = img_byte_arr.getvalue()
                
                # Encode to base64
                base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
            
            # Create Ollama API request
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": model_name,
                "prompt": f"{prompt}\n\nAnalyze this image and provide the results in the requested JSON format:",
                "stream": False,
                "images": [base64_image],
                "options": AIAnalysis.optimization_options
            }
            
            # Make the request
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Sending image analysis request to Ollama, attempt {attempt + 1}")
                    
                    try:
                        response = requests.post(url, json=payload, timeout=60)
                        if response.status_code == 404:
                            # Try alternative endpoint - Ollama may have changed API structure
                            url_alt = "http://localhost:11434/api/chat"
                            chat_payload = {
                                "model": model_name,
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": f"{prompt}\n\nAnalyze this image and provide the results in the requested JSON format:",
                                        "images": [base64_image]
                                    }
                                ],
                                "stream": False,
                                "options": AIAnalysis.optimization_options
                            }
                            logger.info(f"Trying alternative chat endpoint after 404")
                            response = requests.post(url_alt, json=chat_payload, timeout=60)
                        response.raise_for_status()
                        
                        result = response.json()
                        
                        # Handle different response formats
                        if "message" in result and "content" in result["message"]:
                            # /api/chat endpoint
                            return result["message"]["content"]
                        else:
                            # /api/generate endpoint
                            return result.get("response", "")
                    except requests.exceptions.RequestException as req_err:
                        logger.error(f"Request error: {str(req_err)}")
                        raise req_err
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
                        return f"Image analysis failed after {max_retries} attempts: {str(e)}"
                        
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return f"Image analysis failed: {str(e)}"

    @staticmethod
    def test_ollama_connection(model_name="gemma3:4b-it-qat"):
        """Test if Ollama is running and the specified model is available"""
        try:
            # First check if Ollama server is running
            url = "http://localhost:11434/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Then check if the requested model is available
            models = response.json().get("models", [])
            available_models = [model["name"] for model in models]
            
            if model_name in available_models:
                logger.info(f"Model {model_name} is available")
                
                # Test model with a simple prompt
                test_url = "http://localhost:11434/api/generate"
                test_payload = {
                    "model": model_name,
                    "prompt": "Respond with 'OK' if you can read this message.",
                    "stream": False,
                    "options": AIAnalysis.optimization_options
                }
                
                test_response = requests.post(test_url, json=test_payload, timeout=30)
                test_response.raise_for_status()
                result = test_response.json()
                
                if "OK" in result.get("response", ""):
                    return True, f"Ollama is running and model '{model_name}' is working correctly."
                else:
                    return True, f"Ollama is running and model '{model_name}' is available, but response validation failed."
            else:
                available_str = ", ".join(available_models) if available_models else "No models found"
                return False, f"Model '{model_name}' is not available. Available models: {available_str}"
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to Ollama. Make sure Ollama is running on localhost:11434."
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

    @staticmethod
    def list_available_ollama_models():
        """Get a list of available Ollama models with size estimates"""
        try:
            url = "http://localhost:11434/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            result = []
            
            for model in models:
                name = model.get("name", "Unknown")
                size = "Unknown"
                
                # Try to infer model size from name
                if "1b" in name.lower():
                    size = "1B"
                elif "2b" in name.lower():
                    size = "2B"
                elif "4b" in name.lower():
                    size = "4B"
                elif "7b" in name.lower():
                    size = "7B"
                elif "8b" in name.lower():
                    size = "8B"
                elif "12b" in name.lower():
                    size = "12B"
                elif "34b" in name.lower():
                    size = "34B"
                elif "70b" in name.lower():
                    size = "70B"
                
                result.append((name, size))
            
            return result
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {str(e)}")
            return None

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
    
    @staticmethod
    def get_system_resource_info():
        """Get current system resource usage information"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Try to get GPU info if available
            gpu_info = {}
            gpu_memory_gb = None
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Assuming primary GPU
                    gpu_memory_gb = round(gpu.memoryTotal / 1024)  # Convert MB to GB and round
                    gpu_info = {
                        "name": gpu.name,
                        "memory_total_gb": gpu_memory_gb,
                        "memory_used_gb": round(gpu.memoryUsed / 1024, 1),
                        "memory_percent": round(gpu.memoryUtil * 100, 1),
                        "load_percent": round(gpu.load * 100, 1)
                    }
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to get GPU info: {str(e)}")
                
            return {
                "cpu_percent": cpu_percent,
                "ram_percent": memory.percent,
                "ram_used_gb": round(memory.used / (1024**3), 1),
                "ram_total_gb": round(memory.total / (1024**3), 1),
                "gpu_info": gpu_info,
                "gpu_memory_gb": gpu_memory_gb
            }
        except Exception as e:
            logger.error(f"Error getting system resources: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Create an instance of AIAnalysis
    ai_analyzer = AIAnalysis()
    
    # Define some default models
    default_model = "gemma3:4b-it-qat"  # 4B quantized multimodal model that handles both text and vision
    default_audio_model = "whisper"  # Keep whisper for audio as it's specialized

    while True:
        print("\nWhat would you like to test?")
        print("1. Resource analysis")
        print("2. Civilization analysis")
        print("3. Test Ollama connection")
        print("4. List available Ollama models")
        print("5. Check system resources")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            resource_test_image_path = "images/test_resource.jpg"
            if os.path.exists(resource_test_image_path):
                with open(resource_path('prompts/resource_check_prompt.txt'), 'r') as f:
                    resource_test_prompt = f.read()
                
                try:
                    # Allow user to select model if desired
                    use_default = input(f"Use default model ({default_model})? (Y/n): ").strip().lower() != 'n'
                    model_name = default_model if use_default else input("Enter model name: ").strip()
                    
                    print(f"Analyzing resource image with {model_name}...")
                    resource_result = ai_analyzer.analyze_image_ollama(resource_test_image_path, resource_test_prompt, model_name)
                    print("Resource analysis result:")
                    print(resource_result)
                except Exception as e:
                    print(f"An error occurred during resource testing: {e}")
            else:
                print(f"Resource test image not found at {resource_test_image_path}. Please ensure a test image is available.")

        elif choice == '2':
            civ_test_image_path = "images/test_civ.jpg"
            if os.path.exists(civ_test_image_path):
                with open(resource_path('prompts/civ_counter_prompt.txt'), 'r') as f:
                    civ_test_prompt = f.read()
                
                try:
                    # Allow user to select model if desired
                    use_default = input(f"Use default model ({default_model})? (Y/n): ").strip().lower() != 'n'
                    model_name = default_model if use_default else input("Enter model name: ").strip()
                    
                    print(f"Analyzing civilization image with {model_name}...")
                    civ_result = ai_analyzer.analyze_civ_screenshot(civ_test_image_path, model_name, civ_test_prompt)
                    print("\nCiv analysis result:")
                    print(civ_result)
                    
                    try:
                        counters = ai_analyzer.get_counters_for_civs(civ_result)
                        print("\nCiv counters result:")
                        print(counters)
                    except Exception as e:
                        print(f"Could not process counters: {e}")
                        
                except Exception as e:
                    print(f"An error occurred during civ analysis: {e}")
            else:
                print(f"Civ test image not found at {civ_test_image_path}. Please ensure a test image is available.")

        elif choice == '3':
            print("Testing Ollama connection...")
            model_to_test = input(f"Enter model name to test (default: {default_model}): ").strip() or default_model
            success, message = ai_analyzer.test_ollama_connection(model_to_test)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")

        elif choice == '4':
            print("Retrieving available Ollama models...")
            models = ai_analyzer.list_available_ollama_models()
            if models:
                print("\nAvailable models:")
                print("-----------------")
                for i, (name, size) in enumerate(models, 1):
                    print(f"{i}. {name} ({size} parameters)")
            else:
                print("No models found or couldn't connect to Ollama")

        elif choice == '5':
            print("\nChecking system resources...")
            resources = ai_analyzer.get_system_resource_info()
            
            if "error" in resources:
                print(f"Error getting system resources: {resources['error']}")
                continue
                
            print("\n===== System Resources =====")
            print(f"CPU Usage: {resources.get('cpu_percent')}%")
            print(f"RAM: {resources.get('ram_used_gb')}GB / {resources.get('ram_total_gb')}GB ({resources.get('ram_percent')}%)")
            
            gpu_info = resources.get('gpu_info', {})
            if gpu_info:
                print(f"GPU: {gpu_info.get('name')}")
                print(f"GPU Memory: {gpu_info.get('memory_used_gb')}GB / {gpu_info.get('memory_total_gb')}GB ({gpu_info.get('memory_percent')}%)")
                print(f"GPU Load: {gpu_info.get('load_percent')}%")
            else:
                print("GPU: Information not available")
                
            print("============================")
            
            # Make recommendations based on available GPU memory
            gpu_memory_gb = resources.get('gpu_memory_gb')
            ram_total_gb = resources.get('ram_total_gb')
            
            print("\nRecommended model based on your resources:")
            
            if gpu_memory_gb is not None:
                if gpu_memory_gb >= 12:
                    print("✅ Your GPU has significant VRAM (12GB+)")
                    print("   - Can handle gemma3:12b-it-qat for improved analysis")
                    print("   - Can run the model alongside resource-intensive games")
                elif gpu_memory_gb >= 8:
                    print("✅ Your GPU has good VRAM (8GB+)")
                    print("   - Recommended: gemma3:4b-it-qat for balanced performance while gaming")
                elif gpu_memory_gb >= 6:
                    print("✅ Your GPU has moderate VRAM (6GB)")
                    print("   - Recommended: gemma3:4b-it-qat but expect some performance impact while gaming")
                    print("   - Consider gemma3:1b-it-qat if you need more gaming performance")
                elif gpu_memory_gb >= 4:
                    print("✅ Your GPU has limited VRAM (4GB)")
                    print("   - Recommended: gemma3:1b-it-qat for minimal gaming impact")
                    print("   - Only use 4B models when not gaming")
                else:
                    print("⚠️ Your GPU has very limited VRAM (<4GB)")
                    print("   - Recommended: Run CPU-only models or smallest available models")
                    print("   - Consider using CPU-only mode for Ollama when gaming")
            elif ram_total_gb >= 32:
                print("⚠️ No GPU info available, but you have substantial RAM")
                print("   - Consider CPU-only mode with gemma3:4b-it-qat")
            elif ram_total_gb >= 16:
                print("⚠️ No GPU info available, but you have moderate RAM")
                print("   - Consider CPU-only mode with gemma3:1b-it-qat")
            else:
                print("⚠️ Limited system resources detected")
                print("   - Consider using the smallest available models (1B) or external API services")
                
            print("\nTo switch models, use:")
            print("ollama pull gemma3:1b-it-qat  # Smallest multimodal model (1B)")
            print("ollama pull gemma3:4b-it-qat  # Balanced model (4B)")
            print("ollama pull gemma3:12b-it-qat # Higher quality, needs more resources (12B)")
            
        elif choice == '6':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
