from datetime import datetime
import asyncio

from .imessage_reader import fetch_data
from .py_imessage import imessage

from .mac_db import get_db_path


class MessageClient:
    IMESSAGE_CREATION = '2011-01-01 00:00:00'

    def __init__(self, *args, **kwargs):
        # A time filter to ensure messages being read come after a certain date
        self.time_filter = kwargs.get("time_filter") or self.IMESSAGE_CREATION
        if type(self.time_filter) is str:
            self.time_filter = self._parse_time(self.time_filter)

        # The location of the chat.db file used by iMessage
        self.db_path = kwargs.get("db_path", get_db_path())

        # The function invoked to handle new messages
        if "handle_message" in kwargs:
            self.handle_message = kwargs["handle_message"]

        if "handle_post_read" in kwargs and kwargs["handle_post_read"] is not None:
            self.post_read_and_handle = kwargs["handle_post_read"]

        self.read_messages_cache = dict()

    def _hash_message_for_cache(self, message):
        return hash(f"{message[0]} :: {message[1]} :: {message[2]}")

    def _parse_time(self, dt):
        return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")

    async def _get_messages(self, no_filter=False):
        fd = fetch_data.FetchData(self.db_path)
        my_data = await fd.get_messages()

        if no_filter:
            return my_data

        return [m for m in my_data if self._parse_time(m[2]) > self.time_filter]

    async def _get_inbound_messages(self, no_filter=False):
        messages = await self._get_messages(no_filter)
        return [m for m in messages if m[-1] != 1]

    async def _number_requested_stop(self, number):
        messages = await self._get_inbound_messages(no_filter=True)
        return any(number in m[0] and m[1] == "STOP" for m in messages)

    async def send_message(self, to, content, ignore_stop=True, use_applescript=True, create_contact=True):
        if not ignore_stop and await self._number_requested_stop(to):
            # To comply with US law, you'll need to stop when the user requests. 
            return

        await imessage.send(to, content, use_applescript, create_contact)

    async def handle_message(self, from_number, body):
        # Optional, can be overwritten by kwargs["handle_message"]
        pass

    async def post_read_and_handle(self, *args, **kwargs):
        # Optional, can be overwritten by kwargs["handle_post_read"]
        pass

    async def read_and_handle(self):
        messages = await self._get_inbound_messages()
        for m in messages:
            h = self._hash_message_for_cache(m)
            if h not in self.read_messages_cache:
                self.read_messages_cache[h] = True
                from_number = m[0]
                body = m[1]
                possible_reply = await self.handle_message(from_number, body)
                print(f"Sending message to {from_number} with body {possible_reply}")
                if possible_reply is not None:
                    await self.send_message(from_number, possible_reply)

        await self.post_read_and_handle(self)
