from .message_client import MessageClient


async def send_message(to, body, ignore_stop=False, use_applescript=True):
    mc = MessageClient()
    await mc.send_message(to, body, ignore_stop, use_applescript)
