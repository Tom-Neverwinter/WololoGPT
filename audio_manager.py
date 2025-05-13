import pygame
from config import AUDIO_VOLUME, AI_CONFIG
from utils import resource_path, logger
import os
import datetime
import tempfile

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
    
    @staticmethod
    def record_audio(duration=5, sample_rate=16000):
        """Record audio using PyAudio for a specified duration"""
        try:
            import pyaudio
            import wave
            
            # Create directory for recordings if it doesn't exist
            recordings_dir = os.path.join("recordings")
            os.makedirs(recordings_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(recordings_dir, f"recording_{timestamp}.wav")
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # Open stream
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=sample_rate,
                            input=True,
                            frames_per_buffer=1024)
            
            logger.info(f"Recording audio for {duration} seconds...")
            frames = []
            
            # Record for specified duration
            for i in range(0, int(sample_rate / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save the recorded audio to WAV file
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_format_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            logger.info(f"Audio recording saved to {filepath}")
            return filepath
            
        except ImportError:
            logger.error("PyAudio is not installed. Cannot record audio.")
            return None
        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            return None
    
    @staticmethod
    def transcribe_audio(audio_path):
        """Transcribe audio using Ollama's whisper model"""
        try:
            from ai_analysis import AIAnalysis
            
            # Use the default audio model from config
            model_name = AI_CONFIG["default_models"]["audio"]
            
            logger.info(f"Transcribing audio using {model_name}...")
            result = AIAnalysis.transcribe_audio(audio_path, model_name)
            
            return result
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return f"Transcription failed: {str(e)}"

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
    
    # Uncomment to test recording and transcription
    # print("\nRecording audio (5 seconds)...")
    # recording = AudioManager.record_audio(5)
    # if recording:
    #     print(f"Audio recorded to: {recording}")
    #     print("\nTranscribing recorded audio...")
    #     transcription = AudioManager.transcribe_audio(recording)
    #     print(f"Transcription: {transcription}")
