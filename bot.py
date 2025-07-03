import os
from datetime import datetime
from collections import defaultdict
from agents import Agent, Runner
from arcadepy import AsyncArcade
from agents_arcade import get_arcade_tools
from constants import BOT_CONFIG, ERROR_MESSAGES

class FlyMeBot:
    def __init__(self, slack_client=None):
        self.arcade_client = AsyncArcade(api_key=os.getenv("ARCADE_API_KEY"))
        self.agent = None
        self.user_id = "flyme_slack_user"
        self.slack_client = slack_client
        # Add conversation memory
        self.conversation_history = defaultdict(list)
        
    async def get_user_location(self, user_id):
        """Get user's timezone from Slack profile"""
        if not self.slack_client:
            return None
            
        try:
            user_info = await self.slack_client.users_info(user=user_id)
            user_data = user_info.get("user", {})
            tz = user_data.get("tz", "")
            tz_label = user_data.get("tz_label", "")
            
            # Returns the timezone for agent interpretation
            if tz_label:
                return f"{tz_label} timezone"
            elif tz:
                return f"{tz} timezone"
            
            return None
                
        except Exception as e:
            return None
    
    async def initialize(self):
        """Initialize the flight search agent"""
        try:
            print("\n" + "="*50)
            print("Initializing service...")
            print(f"ARCADE_API_KEY present: {bool(os.getenv('ARCADE_API_KEY'))}")
            print(f"OPENAI_API_KEY present: {bool(os.getenv('OPENAI_API_KEY'))}")
            print(f"SLACK_BOT_TOKEN present: {bool(os.getenv('SLACK_BOT_TOKEN'))}")
            print(f"SLACK_APP_TOKEN present: {bool(os.getenv('SLACK_APP_TOKEN'))}")
            
            tools = await get_arcade_tools(
                self.arcade_client,
                toolkits=["search"],
                user_id=self.user_id
            )
            
            print(f"Loaded {len(tools)} tools")
            for tool in tools:
                print(f"Tool available: {tool.name if hasattr(tool, 'name') else str(tool)}")
            
            # Load agent instructions
            with open('instructions.md', 'r') as f:
                instructions_template = f.read()
            
            instructions = instructions_template.replace(
                '{current_date}', 
                datetime.now().strftime("%Y-%m-%d")
            )
            
            print(f"Instructions loaded, length: {len(instructions)}")
            
            self.agent = Agent(
                name="FlyMe Assistant",
                model=BOT_CONFIG["model"],
                instructions=instructions,
                tools=tools
            )
            
            print("Agent initialized successfully")
            print("="*50)
            return True
            
        except Exception as e:
            print(f"[ERROR] Detected in initialize: {str(e)}")
            print("\n" + "="*50)
            import traceback
            traceback.print_exc()
            return False
    
    async def search_flights(self, query, user_id, user_location=None):
        """Search for flights based on user query with conversation memory"""
        try:
            print(f"[Agent] Starting search_flights for user {user_id}")
            print(f"[Agent] Query: {query}")
            print(f"[Agent] User location: {user_location}")
            
            # Check if agent is initialized
            if not self.agent:
                print("[ERROR] Agent not initialized!")
                return "Sorry, the bot is not properly initialized. Please try again later."
            
            # Update conversation history
            self.conversation_history[user_id].append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now()
            })
            
            # Build conversation context for the agent
            conversation_summary = ""
            if len(self.conversation_history[user_id]) > 1:
                recent_messages = self.conversation_history[user_id][-5:]  # Last 5 messages
                conversation_summary = "Previous conversation:\n"
                for msg in recent_messages[:-1]:  # Exclude current message
                    role = msg['role'].capitalize()
                    conversation_summary += f"{role}: {msg['content']}\n"
            
            # Add user location if available
            location_context = ""
            if user_location:
                location_context = f"User's timezone: {user_location}. Use this to infer their likely departure location if they don't specify one. "
            
            # Combine all context
            full_context = f"""{location_context}{conversation_summary}

Current request: {query}

IMPORTANT REMINDERS:
1. When responding to gather information, use natural conversational language, NOT bullet points or structured lists.
2. Extract all relevant information from the conversation history to understand what the user needs.
3. If you have enough information to search for flights, use the Search tools immediately.
4. If you need more information, ask for it conversationally.
5. If the user says they're flexible with dates, DO NOT ask for specific dates. Instead, search across multiple dates in their timeframe.
6. If you see timezone information, use it to intelligently guess the user's location but ask for confirmation if needed."""
            
            print(f"[AGENT] Sending to agent:\n{full_context}")
            
            try:
                result = await Runner.run(
                    starting_agent=self.agent,
                    input=full_context,
                    context={"user_id": self.user_id},
                    max_turns=BOT_CONFIG["max_turns"]
                )
                
                print(f"[AGENT] Response: {result.final_output[:200]}...")
                
                # Store the response
                self.conversation_history[user_id].append({
                    "role": "assistant",
                    "content": result.final_output,
                    "timestamp": datetime.now()
                })
                
                return result.final_output
            
            except Exception as agent_error:
                print(f"[ERROR] Detected in Runner.run: {str(agent_error)}")
                import traceback
                traceback.print_exc()
                raise
            
        except Exception as e:
            print(f"[ERROR] Detected in search_flights: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_str = str(e)
            if "rate_limit_exceeded" in error_str or "429" in error_str:
                return ERROR_MESSAGES["rate_limit"]
            else:
                return ERROR_MESSAGES["generic"]
