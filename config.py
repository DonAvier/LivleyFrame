"""
Configuration for the Cornice AI + Gemini prototype.
Fill in GEMINI_API_KEY with your own key from Google AI Studio:
https://aistudio.google.com
"""

GEMINI_API_KEY = "AIzaSyC-OWjUU0USyjezyXdTwx8yHTn0c8g1ZVE"

# Gemini 1.5 Flash model name (can be changed to 1.5 Pro later)
GEMINI_MODEL = "gemini-1.5-flash"

# Base URL for the Generative Language API (v1beta)
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Duration of generated video in seconds (Gemini may adjust this)
VIDEO_DURATION_SECONDS = 4
