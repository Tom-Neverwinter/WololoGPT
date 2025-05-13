@staticmethod
def analyze_resource_screenshot(screenshot_path):
    """Analyze a resource screenshot using AI Analysis"""
    try:
        from ai_analysis import AIAnalysis
        from config import AI_CONFIG, RESOURCE_CHECK_PROMPT
        
        # Use default image model from config
        model_name = AI_CONFIG["default_models"]["image"]
        
        logger.info(f"Analyzing resource screenshot with {model_name}...")
        result = AIAnalysis.analyze_image_ollama(screenshot_path, RESOURCE_CHECK_PROMPT, model_name)
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing resource screenshot: {str(e)}")
        return None

@staticmethod
def analyze_civ_screenshot(screenshot_path):
    """Analyze a civilization screenshot using AI Analysis"""
    try:
        from ai_analysis import AIAnalysis
        from config import AI_CONFIG, CIV_COUNTER_PROMPT
        
        # Use default image model from config
        model_name = AI_CONFIG["default_models"]["image"]
        
        logger.info(f"Analyzing civilization screenshot with {model_name}...")
        result = AIAnalysis.analyze_civ_screenshot(screenshot_path, model_name, CIV_COUNTER_PROMPT)
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing civilization screenshot: {str(e)}")
        return None
