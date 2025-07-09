import os
import re
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

def create_slack_app():
    """Create and configure the Slack app"""
    return AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))


def setup_slack_handlers(app, bot):
    """Set up all Slack event handlers"""
    
    @app.event("message")
    async def handle_message_events(event, say, logger):
        """Handle DM messages"""
        logger.info(f"Message event received: {event}")
        
        if event.get("bot_id"):
            return
        
        channel_type = event.get("channel_type")
        
        if channel_type == "im":
            user_message = event.get("text", "").lower()
            user_id = event.get("user", "")
            original_message = event.get("text", "")
            
            # Get user location from profile
            user_location = await bot.get_user_location(user_id)
            
            # Send typing indicator
            await say("I'm thinking...")
            
            # Determine if this is a hotel search request
            hotel_keywords = ["hotel", "hotels", "accommodation", "stay", "booking", "room", "lodge", "resort"]
            is_hotel_request = any(keyword in user_message for keyword in hotel_keywords)
            
            if is_hotel_request:
                # Search hotels
                result = await bot.search_hotels(original_message, user_id, user_location)
            else:
                # Search flights (existing functionality)
                result = await bot.search_flights(original_message, user_id, user_location)
            
            # Send results
            await say(result)

    @app.event("app_mention")
    async def handle_app_mention(event, say, logger):
        """Handle @mentions in channels"""
        user_message = event.get("text", "")
        user_id = event.get("user", "")
        user_message_clean = re.sub(r'<@[A-Z0-9]+>', '', user_message).strip()
        
        # Get user location from profile
        user_location = await bot.get_user_location(user_id)
        
        await say("I'm thinking...")
        
        # Determine if this is a hotel search request
        hotel_keywords = ["hotel", "hotels", "accommodation", "stay", "booking", "room", "lodge", "resort"]
        is_hotel_request = any(keyword in user_message_clean.lower() for keyword in hotel_keywords)
        
        if is_hotel_request:
            result = await bot.search_hotels(user_message_clean, user_id, user_location)
        else:
            result = await bot.search_flights(user_message_clean, user_id, user_location)
        
        await say(result)

    # Handle app_home_opened events to prevent warnings
    @app.event("app_home_opened")
    async def handle_app_home_opened_events(body, logger):
        """Handle app home opened events"""
        logger.info("App home opened")

    # Catch-all for unhandled events
    @app.event("message")
    async def handle_message_events_fallback(event, logger):
        """Log unhandled message subtypes"""
        pass


async def create_socket_handler(app):
    """Create and configure Socket Mode handler"""
    handler = AsyncSocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    
    # Add connection handler to confirm Socket Mode is working
    @handler.client.socket_mode_request_listeners.append
    async def handle_socket_mode_request(client, request):
        if request.type == "events_api":
            print(f"Event received: {request.payload.get('event', {}).get('type', 'unknown')}")
    
    return handler
    