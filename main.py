#!/usr/bin/env python3
"""
FlyMe Bot - A Real-Time Slack Bot for Flights
Main entry point for the application
"""
import asyncio
import sys
from dotenv import load_dotenv

from config import Config
from app import FlyMeApp

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Load and validate configuration
    config = Config.from_env()
    missing = config.validate()
    
    if missing:
        print(f"[ERROR] Missing required environment variables: {', '.join(missing)}")
        print("\nPlease ensure all required variables are set in your .env file:")
        print("  - ARCADE_API_KEY")
        print("  - OPENAI_API_KEY")
        print("  - SLACK_BOT_TOKEN")
        print("  - SLACK_APP_TOKEN")
        sys.exit(1)
    
    # Create and run application
    app = FlyMeApp(config)
    
    try:
        asyncio.run(run_app(app))
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


async def run_app(app: FlyMeApp):
    """Run the application with proper initialization"""
    await app.initialize()
    await app.run()


if __name__ == "__main__":
    main()
