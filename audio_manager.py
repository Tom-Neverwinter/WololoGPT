import pygame
from config import AUDIO_VOLUME
from utils import resource_path, logger
import os

class AudioManager:
    @staticmethod
    def play_audio(file_path, volume=None):
        try:
            pygame.mixer.init()
            full_path = resource_path(file_path)
            if not os.path.exists(full_path):
                logger.error(f"Audio file not found: {full_path}")
                return
            pygame.mixer.music.load(full_path)
            if volume is not None:
                pygame.mixer.music.set_volume(volume)
            else:
                pygame.mixer.music.set_volume(AUDIO_VOLUME)
            pygame.mixer.music.play()
            logger.info(f"Playing audio: {full_path}")
        except Exception as e:
            logger.error(f"Error playing audio {file_path}: {str(e)}")

    @staticmethod
    def stop_audio():
        try:
            pygame.mixer.music.stop()
            logger.info("Audio stopped")
        except Exception as e:
            logger.error(f"Error stopping audio: {str(e)}")

if __name__ == "__main__":
    # Test the AudioManager
    test_file = 'audio/warnings/maison.mp3'  # Adjust this path as needed
    
    print("Playing test audio...")
    AudioManager.play_audio(test_file)
    
    # Wait for a few seconds
    import time
    time.sleep(3)
    
    print("Stopping audio...")
    AudioManager.stop_audio()
    
    print("Audio test complete.")
