from . import db_conn
import os
import asyncio
import platform
from shlex import quote

import sys
if sys.version_info[0] < 3:
    print("Must be using Python 3")

# print(platform.mac_ver())

def _check_mac_ver():
    mac_ver, _, _ = platform.mac_ver()
    mac_ver = float('.'.join(mac_ver.split('.')[:2]))
    if mac_ver >= 10.16:
        print(mac_ver)
    else:
        print("outdated OS")
    return mac_ver
        

async def send(phone, message, use_applescript=True, create_contact=True):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    relative_path = 'osascript/send_imessage.applescript' if use_applescript else 'osascript/send_message.js'
    path = f'{dir_path}/{relative_path}'
    if use_applescript:
        cmd = f'osascript {path} {quote(phone)} {quote(message)} {"true" if create_contact else "false"}'
    else:
        cmd = f'osascript -l JavaScript {path} {quote(phone)} {quote(message)}'
    
    # Run subprocess asynchronously
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.wait()


async def status(guid):
    await db_conn.open()
    message = await db_conn.get_message(guid)
    return message


async def check_compatibility(phone):
    mac_ver = _check_mac_ver()
    is_imessage = False
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    relative_path = 'osascript/check_imessage.js'
    path = f'{dir_path}/{relative_path}'
    cmd = f'osascript -l JavaScript {path} {phone} {mac_ver}'
    
    # Run subprocess asynchronously
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if 'true' in stdout.decode('utf-8'):
        is_imessage = True

    return is_imessage
