import asyncio
import json
import random
import aiohttp
import re
import os
from dotenv import load_dotenv

load_dotenv()

AUTH = os.getenv("AUTH", "")
CHANNEL = os.getenv("CHANNEL", "")
GUILD_ID = os.getenv("GUILD_ID", "")
APPLICATION_ID = os.getenv("APPLICATION_ID", "")
X_INSTALLATION_ID = os.getenv("X_INSTALLATION_ID", "")
X_CONTEXT_PROPERTIES = os.getenv("X_CONTEXT_PROPERTIES", "")
X_SUPER_PROPERTIES = os.getenv("X_SUPER_PROPERTIES", "")

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
session_id = None  
active_messages = set() 

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": AUTH,
    "content-type": "application/json",
    "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-context-properties": X_CONTEXT_PROPERTIES,
    "x-debug-options": "bugReporterEnabled",
    "x-discord-locale": "en-GB",
    "x-discord-timezone": "Asia/Calcutta",
    "x-installation-id": X_INSTALLATION_ID,
    "x-super-properties": X_SUPER_PROPERTIES,
}

URL_MESSAGES = f"https://discord.com/api/v9/channels/{CHANNEL}/messages"
URL_INTERACTIONS = "https://discord.com/api/v9/interactions"
URL_TYPING = f"https://discord.com/api/v9/channels/{CHANNEL}/typing"

def make_body(content):
    return {
        "mobile_network_type": "cellular",
        "content": content,
        "nonce": str(random.getrandbits(64)),
        "tts": False,
        "flags": 0
    }

def find_buttons(item):
    buttons = {}
    if isinstance(item, dict):
        if item.get("type") == 2 and "custom_id" in item:
            label = item.get("label", "").lower().strip()
            buttons[label] = item["custom_id"]
        for key, value in item.items():
            if isinstance(value, (dict, list)):
                buttons.update(find_buttons(value))
    elif isinstance(item, list):
        for sub_item in item:
            buttons.update(find_buttons(sub_item))
    return buttons

def extract_v2_content(components):
    text_pieces = []
    if isinstance(components, dict):
        if components.get("type") == 10 and "content" in components:
            text_pieces.append(components["content"])
        for key, value in components.items():
            if isinstance(value, (dict, list)):
                text_pieces.extend(extract_v2_content(value))
    elif isinstance(components, list):
        for item in components:
            text_pieces.extend(extract_v2_content(item))
    return " ".join(text_pieces)

def parse_hl_number(text):
    clean_text = re.sub(r'[\*\_\`\~\u200b\u200c\u200d\u200e\u200f\u202a-\u202e]', '', text)
    clean_text = re.sub(r'(?<=[\d])\s+(?=[\d])', '', clean_text)
    match = re.search(r'(?:than\s*|is\s*|number:?\s*)(\d+)', clean_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    digits = re.findall(r'\d+', clean_text)
    if digits:
        return int(digits[-1])
    return None

async def fire_interaction(session, message_id, custom_id, flags=0, label_hint=""):
    global session_id, active_messages
    if not session_id:
        active_messages.discard(message_id)
        return

    payload = {
        "type": 3,
        "nonce": str(random.getrandbits(64)),
        "guild_id": GUILD_ID,
        "channel_id": CHANNEL,
        "message_flags": flags,
        "message_id": message_id,
        "application_id": APPLICATION_ID,
        "session_id": session_id,
        "data": {
            "component_type": 2,
            "custom_id": custom_id
        }
    }

    await asyncio.sleep(random.uniform(1.8, 3.2))

    async with session.post(URL_INTERACTIONS, json=payload) as response:
        if response.status in (200, 204):
            print(f"[BUTTON] SUCCESS | Target: '{label_hint or custom_id}'")
        else:
            err_text = await response.text()
            print(f"[BUTTON] FAILED | Status: {response.status} | {err_text}")
            
    await asyncio.sleep(5)
    active_messages.discard(message_id)

async def command_sender_loop(session):
    await asyncio.sleep(5)
    while True:
        await send_command(session, "pls hunt")
        await asyncio.sleep(random.uniform(2.5, 4.5))
        
        await send_command(session, "pls dig")
        await asyncio.sleep(random.uniform(2.5, 4.5))
        
        await send_command(session, "pls beg")
        await asyncio.sleep(random.uniform(2.5, 4.5))

        await send_command(session, "pls hl")
        await asyncio.sleep(random.uniform(6.0, 8.0)) 

        await send_command(session, "pls search")
        await asyncio.sleep(random.uniform(6.0, 8.0))

        await send_command(session, "pls crime")
        
        await asyncio.sleep(random.uniform(22.0, 26.0))

async def send_command(session, command_text):
    async with session.post(URL_TYPING) as typ_resp:
        if typ_resp.status not in (200, 204):
            print(f"WARNING | Typing event failed status: {typ_resp.status}")
    
    await asyncio.sleep(random.uniform(0.8, 1.8))
    
    body = make_body(command_text)
    async with session.post(URL_MESSAGES, json=body) as response:
        if not (200 <= response.status < 300):
            err_text = await response.text()
            print(f"ERROR | {command_text.upper()} failed: {err_text}")

async def send_heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await ws.send_json({"op": 1, "d": None})

async def gateway_listener_loop(session, ws):
    global session_id, active_messages
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            payload = json.loads(msg.data)
            event_type = payload.get("t")
            
            if event_type == "READY":
                session_id = payload["d"]["session_id"]
                print(f"[GATEWAY] Active Session Stored: {session_id}")
                
            elif event_type in ("MESSAGE_CREATE", "MESSAGE_UPDATE"):
                data = payload["d"]
                if data.get("channel_id") != CHANNEL:
                    continue
                
                message_id = data.get("id")
                
                if message_id in active_messages:
                    continue
                
                if "components" in data and data["components"]:
                    buttons_map = find_buttons(data["components"])
                    if not buttons_map:
                        continue
                        
                    flags = data.get("flags", 0)
                    
                    content = data.get("content", "")
                    if (flags & 32768) == 32768:
                        content = extract_v2_content(data["components"])
                    
                    if "higher" in buttons_map or "lower" in buttons_map:
                        current_num = parse_hl_number(content)
                        
                        if current_num is not None:
                            active_messages.add(message_id)
                            print(f"[DECISION-HL] Baseline number evaluated: {current_num}")
                            target_choice = "higher" if current_num <= 50 else "lower"
                                
                            if target_choice in buttons_map:
                                print(f"[DECISION-HL] CURRENT NUM: {current_num} | Selecting interaction path: '{target_choice}'")
                                asyncio.create_task(fire_interaction(session, message_id, buttons_map[target_choice], flags, target_choice))
                                continue
                    
                    active_messages.add(message_id)
                    fallback_label, fallback_id = random.choice(list(buttons_map.items()))
                    print(f"[DECISION-RANDOM] Fallback target chosen: '{fallback_label}'")
                    asyncio.create_task(fire_interaction(session, message_id, fallback_id, flags, fallback_label))

async def main():
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.ws_connect(GATEWAY_URL) as ws:
            
            first_msg = await ws.receive()
            hello_data = json.loads(first_msg.data)
            heartbeat_interval = hello_data['d']['heartbeat_interval']
            asyncio.create_task(send_heartbeat(ws, heartbeat_interval))
            
            identify_payload = {
                "op": 2,
                "d": {
                    "token": AUTH,
                    "capabilities": 16381,
                    "properties": {"os": "windows", "browser": "chrome", "device": ""},
                    "presence": {"status": "online", "since": 0, "activities": [], "afk": False},
                    "compress": False
                }
            }
            await ws.send_json(identify_payload)
            
            await asyncio.gather(
                command_sender_loop(session),
                gateway_listener_loop(session, ws)
            )

asyncio.run(main())
