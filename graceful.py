import signal
import sys
import asyncio

class GracefulShutdown:
    """Handle graceful shutdown of the application"""
    
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.handlers = []
        
    def add_handler(self, handler):
        """Add a handler to be called during shutdown"""
        self.handlers.append(handler)
        
    async def shutdown(self):
        """Execute all shutdown handlers"""
        print("\n\nShutting down FlyMe Bot...")
        
        # Suppress Slack SDK logging during shutdown
        import logging
        logging.getLogger("slack_bolt").setLevel(logging.ERROR)
        logging.getLogger("slack_sdk").setLevel(logging.ERROR)
        logging.getLogger("slack_bolt.AsyncApp").setLevel(logging.ERROR)
        
        for handler in self.handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                print(f"Error during shutdown: {e}")
                
        print("Goodbye!")
        
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            print("\n\nReceived shutdown signal...")
            # Set the event in a thread-safe way
            asyncio.get_event_loop().call_soon_threadsafe(self.shutdown_event.set)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self.shutdown_event.wait()
