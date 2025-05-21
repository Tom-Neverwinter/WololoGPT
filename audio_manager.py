import pygame
from utils import logger
from ai_analysis import AIAnalysis
from config import AI_CONFIG

class AudioManager:
    """Manages audio playback and transcription."""
    _mixer_initialized = False

    @staticmethod
    def init_mixer():
        """Initializes the pygame mixer if not already initialized."""
        if not AudioManager._mixer_initialized:
            try:
                pygame.mixer.init()
                AudioManager._mixer_initialized = True
                logger.info("Pygame mixer initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing pygame mixer: {e}")
                # We might want to raise an error here or handle it in play_audio
                # For now, just logging the error. play_audio will fail if not initialized.
                AudioManager._mixer_initialized = False # Ensure it's marked as not initialized

    @staticmethod
    def play_audio(audio_file_path: str, volume: float = 0.35):
        """
        Plays an audio file using pygame mixer.

        Args:
            audio_file_path (str): The path to the audio file.
            volume (float, optional): The volume for playback (0.0 to 1.0). Defaults to 0.35.
        """
        AudioManager.init_mixer()

        if not AudioManager._mixer_initialized:
            logger.error("Cannot play audio: Pygame mixer failed to initialize.")
            return

        try:
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
            logger.info(f"Playing audio: {audio_file_path} at volume {volume}")
        except pygame.error as e: # More specific exception for pygame errors
            logger.error(f"Error playing audio file '{audio_file_path}': {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while trying to play audio '{audio_file_path}': {e}")

    @staticmethod
    def transcribe_audio(audio_path):
        """
        Transcribe audio using AI Analysis (e.g., Ollama's whisper model).
        """
        if not audio_path:
            logger.error("No audio path provided for transcription.")
            return "Transcription failed: No audio path provided."
            
        try:
            # Use the default audio model from config
            model_name = AI_CONFIG["default_models"]["audio"]
            
            logger.info(f"Transcribing audio from '{audio_path}' using {model_name}...")
            result = AIAnalysis.transcribe_audio(audio_path, model_name)
            
            return result
        except KeyError:
            logger.error("AI_CONFIG is missing 'default_models' or 'audio' key for transcription.")
            return "Transcription failed: AI configuration error."
        except Exception as e:
            logger.error(f"Error transcribing audio from '{audio_path}': {str(e)}")
            return f"Transcription failed: {str(e)}"

if __name__ == '__main__':
    # This section is for example usage and testing.
    # It requires:
    # 1. utils.py with a logger object
    # 2. ai_analysis.py with a class AIAnalysis and static method transcribe_audio
    # 3. config.py with AI_CONFIG dictionary
    # 4. A dummy audio file (e.g., "dummy_audio.wav") for play_audio testing.

    # Create dummy utils.py if not present
    try:
        from utils import logger
    except ImportError:
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info("Created dummy logger for audio_manager.py example.")

    # Create dummy config.py if not present
    try:
        from config import AI_CONFIG
    except ImportError:
        AI_CONFIG = {
            "default_models": {
                "audio": "dummy_whisper_model"
            }
        }
        logger.info("Created dummy AI_CONFIG for audio_manager.py example.")

    # Create dummy ai_analysis.py if not present
    try:
        from ai_analysis import AIAnalysis
    except ImportError:
        class AIAnalysis:
            @staticmethod
            def transcribe_audio(path, model):
                logger.info(f"DUMMY AI: Transcribing {path} with {model}")
                return f"Dummy transcription for {path}"
        logger.info("Created dummy AIAnalysis for audio_manager.py example.")

    # Example for play_audio:
    # You would need a real .wav or .mp3 file for this to work.
    # For now, we'll just call init_mixer to test that part.
    logger.info("Testing AudioManager...")
    AudioManager.init_mixer() # Should print initialization log

    # To test play_audio, create a dummy sound file or use a known one.
    # e.g. if you have a "test.wav":
    # AudioManager.play_audio("test.wav") 
    # For now, let's simulate a call that might fail if file not found:
    # AudioManager.play_audio("non_existent_audio_file.wav")

    # Example for transcribe_audio:
    dummy_audio_file = "dummy_transcribe_me.wav"
    # Create a dummy file for transcription test
    with open(dummy_audio_file, "w") as f:
        f.write("dummy audio data")
    
    transcription_result = AudioManager.transcribe_audio(dummy_audio_file)
    logger.info(f"Transcription result: {transcription_result}")

    # Clean up dummy file
    try:
        import os
        os.remove(dummy_audio_file)
    except Exception:
        pass

    logger.info("AudioManager test finished.")
