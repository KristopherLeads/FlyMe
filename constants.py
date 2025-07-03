"""
Application-wide constants
"""

# Bot configuration
BOT_CONFIG = {
    "model": "gpt-4o",
    "max_turns": 10,
    "max_conversation_history": 5,
    "response_timeout": 30,
}

# Error messages
ERROR_MESSAGES = {
    "rate_limit": "I'm receiving too many requests right now. Please try again in a moment.",
    "no_results": "I couldn't find any flights matching your criteria. Try being more flexible with dates or airports.",
    "generic": "I encountered an error while searching for flights. Please try again.",
}
