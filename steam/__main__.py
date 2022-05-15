import base64
import hmac
import json
import struct
from hashlib import sha1
import time
import sys
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

sys.path.append('.')
import config


# Simple function that generates steam codes by passing shared secret key
def getTwoFactorCode(shared_secret: str) -> str:
    timestamp = int(time.time())
    time_buffer = struct.pack('>Q', timestamp // 30)
    time_hmac = hmac.new(base64.b64decode(shared_secret), time_buffer, digestmod=sha1).digest()
    begin = ord(time_hmac[19:20]) & 0xf
    full_code = struct.unpack('>I', time_hmac[begin:begin + 4])[0] & 0x7fffffff
    chars = '23456789BCDFGHJKMNPQRTVWXY'
    code = ''
    for _ in range(5):
        full_code, i = divmod(full_code, len(chars))
        code += chars[i]
    return code

# Loading accounts from the list
def loadAccounts() -> list:
    try:
        with open(config.ACCOUNTS_FILE_NAME, 'r') as file:
            return json.load(file)
    except Exception as err:
        print("loadAccounts() error: ", err)
        return []

def generateOptions():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2

    accounts = loadAccounts()

    for username in accounts:
        if "shared_secret" in accounts[username]:
            markup.add(InlineKeyboardButton(username, callback_data=f"steam_account_{username}"))
    return markup

def processCallbackQuery(send, call):
    username = call.data[14:]
    send(call.from_user.id, generateCode(username))

def generateCode(username) -> str:
    try:
        accounts = loadAccounts()
        return getTwoFactorCode(accounts[username]['shared_secret'])
    except Exception as e:
        print("Error: ", e)
        return f"Could not generate code: {e}"