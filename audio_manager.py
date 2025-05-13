# Add this method to AudioManager class

@staticmethod
def transcribe_audio(audio_path):
    """Transcribe audio using Ollama's whisper model"""
    try:
        from ai_analysis import AIAnalysis
        from config import AI_CONFIG
        
        # Use the default audio model from config
        model_name = AI_CONFIG["default_models"]["audio"]
        
        logger.info(f"Transcribing audio using {model_name}...")
        result = AIAnalysis.transcribe_audio(audio_path, model_name)
        
        return result
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return f"Transcription failed: {str(e)}"
