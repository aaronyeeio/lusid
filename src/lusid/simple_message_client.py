from datetime import datetime
import asyncio

from .message_client import MessageClient


async def create_simple_message_client(message_handler, interval=0.1, handle_post_read=None):
    time_of_run = datetime.now()
    
    mc = MessageClient(
        handle_message=message_handler,
        time_filter=time_of_run,
        handle_post_read=handle_post_read
    )

    while True:
        await asyncio.sleep(interval)

        try:
            await mc.read_and_handle()
        except Exception as e: # Very failure tolerant
            print("Exception!")
            print(e)
