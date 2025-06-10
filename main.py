import asyncio
import os
import re
from datetime import datetime, timedelta

from dotenv import load_dotenv
from agents import Agent, Runner
from arcadepy import AsyncArcade
from agents_arcade import get_arcade_tools
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

load_dotenv()

# Initialize Slack app
app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))

# Global bot instance
bot = None

class FlyMeBot:
    def __init__(self):
        self.arcade_client = AsyncArcade(api_key=os.getenv("ARCADE_API_KEY"))
        self.agent = None
        self.user_id = "flyme_slack_user"
        self.slack_client = None
        
    async def get_user_location(self, user_id):
        """Get user's timezone from Slack profile"""
        if not self.slack_client:
            self.slack_client = app.client
            
        try:
            user_info = await self.slack_client.users_info(user=user_id)
            user_data = user_info.get("user", {})
            tz = user_data.get("tz", "")
            tz_label = user_data.get("tz_label", "")
            
            if tz:
                return f"{tz_label} (timezone: {tz})"
            return None
                
        except Exception as e:
            return None
        
    async def initialize(self):
        """Initialize the flight search agent"""
        tools = await get_arcade_tools(
            self.arcade_client,
            toolkits=["search"],
            user_id=self.user_id
        )
        
        # Load instructions from file
        with open('instructions.md', 'r') as f:
            instructions_template = f.read()
        
        instructions = instructions_template.replace(
            '{current_date}', 
            datetime.now().strftime("%Y-%m-%d")
        )
        
        self.agent = Agent(
            name="FlyMe Assistant",
            model="gpt-4o",
            instructions=instructions,
            tools=tools
        )
        
        return True
    
    async def search_flights(self, query, conversation_history=""):
        """Search for flights based on user query"""
        try:
            # Include conversation context if available
            full_context = query
            if conversation_history:
                full_context = f"Previous context: {conversation_history}\n\nCurrent request: {query}"
            
            result = await Runner.run(
                starting_agent=self.agent,
                input=f"Search for flights based on this request: {full_context}\n\nIMPORTANT: Use the actual dates requested by the user. Show only top 5 results.",
                context={"user_id": self.user_id},
                max_turns=5
            )
            return result.final_output
        except Exception as e:
            error_str = str(e)
            if "rate_limit_exceeded" in error_str:
                return "Too many results - please be more specific."
            elif "429" in error_str:
                return "Rate limit reached."
            else:
                return f"Sorry, I encountered an error. Please try again."

# Slack event handlers
@app.event("message")
async def handle_message_events(event, say, logger):
    """Handle DM messages"""
    logger.info(f"Message event received: {event}")
    
    if event.get("bot_id"):
        return
    
    channel_type = event.get("channel_type")
    
    if channel_type == "im":
        user_message = event.get("text", "")
        user_id = event.get("user", "")
        
        # Get user location from profile
        user_location = await bot.get_user_location(user_id)
        
        # Send typing indicator
        await say("🔍 Searching for flights...")
        
        # Search flights with location context
        context = f"User is likely in/near: {user_location}. " if user_location else ""
        result = await bot.search_flights(context + user_message)
        
        # Send results
        await say(result)

@app.event("app_mention")
async def handle_app_mention(event, say, logger):
    """Handle @mentions in channels"""
    user_message = event.get("text", "")
    user_message = re.sub(r'<@[A-Z0-9]+>', '', user_message).strip()
    
    await say("🔍 Searching for flights...")
    result = await bot.search_flights(user_message)
    await say(result)

# Catch-all for unhandled events
@app.event("message")
async def handle_message_events_fallback(event, logger):
    """Log unhandled message subtypes"""
    pass

async def main():
    """Main function to run the bot"""
    global bot
    
    print("🚀 FlyMe - Find Flights in Slack!")
    print("=" * 50)
    
    # Check environment
    required_vars = ["ARCADE_API_KEY", "OPENAI_API_KEY", "SLACK_BOT_TOKEN", "SLACK_APP_TOKEN"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        return
    
    # Initialize bot
    bot = FlyMeBot()
    await bot.initialize()
    
    # Configure app with debug logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Start Socket Mode handler
    handler = AsyncSocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    
    print("\n" + "="*50)
    print("FlyMe Bot is listening for messages... (Press Ctrl+C to stop)")
    print("="*50)
    
    # Add connection handler to confirm Socket Mode is working
    @handler.client.socket_mode_request_listeners.append
    async def handle_socket_mode_request(client, request):
        if request.type == "events_api":
            print(f"Event received: {request.payload.get('event', {}).get('type', 'unknown')}")
    
    await handler.start_async()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutting down FlyMe Bot...")
        print("Goodbye!")
        