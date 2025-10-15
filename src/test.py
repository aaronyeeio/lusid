import asyncio
from lusid import create_simple_message_client

async def handle_message(from_number, body):
    print(f"Handling the message [{body}] from [{from_number}]")
    return "Some funny autoreply here"  # Or None to not reply at all

async def start_client():
    await create_simple_message_client(
        message_handler=handle_message,
    )

if __name__ == "__main__":
    asyncio.run(start_client())