# db.py 

# Connect to
import aiosqlite
import os 
import datetime
import math
import pytz
import asyncio

# Works for mac Catalina
home = os.environ['HOME']
db_path = f'{home}/Library/Messages/chat.db'

db = None

async def open():
    global db
    if db:
        return db
    # Read only mode
    db = await aiosqlite.connect(db_path, uri=True)
    return db

async def clean_up():
    global db
    if db:
        await db.close()
        db = None

DATE_OFFSET = 978307200

def apple_time_now():
     return math.floor(datetime.datetime.now() / 1000) - DATE_OFFSET

def from_apple_time(ts):
    if ts==0:
        return None

    if unpack_time(ts) != 0:
        ts = unpack_time(ts)
    
    return datetime.datetime.fromtimestamp((ts + DATE_OFFSET), tz=pytz.timezone('US/Pacific'))

def unpack_time(ts):
    return math.floor(ts / (10**9))

def pack_time_conditionally(ts):
    return ts * 10**9

async def get_most_recently_sent_text():
    cursor = await db.execute("""SELECT guid, id as handle, text, date, date_read, date_delivered
    FROM message
    LEFT OUTER JOIN handle ON message.handle_id=handle.ROWID
    WHERE is_from_me = 1 
    ORDER BY date DESC
    LIMIT 1""")
    result = await cursor.fetchone()
    return result[0]

async def get_message(guid): 
    cursor = await db.execute(f"""SELECT guid, date, date_read, date_delivered
    FROM message
    LEFT OUTER JOIN handle ON message.handle_id=handle.ROWID
    WHERE is_from_me = 1 and guid="{guid}"
    LIMIT 1""")
    message = await cursor.fetchone()

    return {
        'guid': message[0],
        'date': from_apple_time(message[1]),
        'date_read': from_apple_time(message[2]),
        'date_delivered': from_apple_time(message[3])
        }