import asyncio
from typing import Optional

from bot import FlyMeBot
from slack import create_slack_app, setup_slack_handlers, create_socket_handler
from graceful import GracefulShutdown
from config import Config, setup_logging

class FlyMeApp:
    """Main application class that orchestrates all components"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logging(config.log_level)
        self.bot: Optional[FlyMeBot] = None
        self.slack_app = None
        self.handler = None
        self.shutdown = GracefulShutdown()
        
    async def initialize(self):
        """Initialize all application components"""
        self.logger.info("Initializing FlyMe application...")
        
        # Create Slack app
        self.slack_app = create_slack_app()
        
        # Initialize bot with Slack client
        self.bot = FlyMeBot(slack_client=self.slack_app.client)
        await self.bot.initialize()
        
        # Set up Slack handlers
        setup_slack_handlers(self.slack_app, self.bot)
        
        # Create Socket Mode handler
        self.handler = await create_socket_handler(self.slack_app)
        
        # Set up graceful shutdown
        self.shutdown.add_handler(self.cleanup)
        self.shutdown.setup_signal_handlers()
        
        self.logger.info("FlyMe application initialized successfully")
        
    async def cleanup(self):
        """Clean up resources during shutdown"""
        if self.handler:
            await self.handler.close_async()
            
    async def run(self):
        """Run the application"""
        self.print_banner()
        
        try:
            # Create tasks for both the handler and shutdown wait
            handler_task = asyncio.create_task(self.handler.start_async())
            shutdown_task = asyncio.create_task(self.shutdown.wait_for_shutdown())
            
            # Wait for either the handler to stop or shutdown signal
            done, pending = await asyncio.wait(
                [handler_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel any pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
        finally:
            await self.shutdown.shutdown()
            
    def print_banner(self):
        """Print application banner"""
        print("\n" + "="*50)
        print("🚀 FlyMe - Find Flights in Slack!")
        print("="*50)
        print("Bot is listening for messages... (Press Ctrl+C to stop)")
        print("="*50 + "\n")
        
