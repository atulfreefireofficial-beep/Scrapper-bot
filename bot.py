import re
import os
import asyncio
from urllib.parse import urlparse
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ================= CONFIG =================
API_ID = 35384207
API_HASH = "09c4bc9de62a417ccdd0c69b33912515"
BOT_TOKEN = "8442090009:AAEqBxqodGpGM1cG_iFJVdqS_IUdXMksUsI"
SESSION_STRING = "BQIb648AcZVCB2SIHsovZtCss8OA6ahgEJH9vyAhTa8Jyas81UYO-yOT_8-rClwRKi1S1dCYAC0QU6_5GC674ZByGSO9m6yln7d7_LXWHkDKDj6k-aABOlNy-J4R11Ws0MTxMAsAnY7_7XdV0mdWPjSI8so-sPgovc6tC9vu6tP9s4XYiDKH6l6_5OHC_F6IS6ttRnYMnbcHLHvryjVWuYAg5qapy_ts-IR0OGJdtSMNuAqo4Jw2gx41bq4CQ65IJf2IKPcJNjxzIpgXpMh_Y9O9Zj3jDZKwKNhli_x3YVmiLIyg84FpYug1n2zwCpI7CFQUag6yTcqGnzCQrgrSyVF03Ujt7gAAAAHowfzxAA"
ADMIN_IDS = [8199994609]
DEFAULT_LIMIT = 10000
ADMIN_LIMIT = 100000

# Live Emoji IDs (Telegram Premium Emojis)
# Replace these IDs with your actual custom emoji IDs from @getidsbot
LIVE_EMOJIS = {
    "scrape": '<tg-emoji emoji-id="6136204644625423818">🔄</tg-emoji>',
    "success": '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji>',
    "error": '<tg-emoji emoji-id="6325599637088503604">❌</tg-emoji>',
    "warning": '<tg-emoji emoji-id="5462882007451185227">⚠️</tg-emoji>',
    "channel": '<tg-emoji emoji-id="5224450179368767019">📢</tg-emoji>',
    "card": '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji>',
    "bin": '<tg-emoji emoji-id="5854784287013867183">🔢</tg-emoji>',
    "country": '<tg-emoji emoji-id="5042334757040423886">🌍</tg-emoji>',
    "type": '<tg-emoji emoji-id="5983292843836314861">💳</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5278394972901492572">👑</tg-emoji>',
    "user": '<tg-emoji emoji-id="5958417144877160497">👤</tg-emoji>',
    "stats": '<tg-emoji emoji-id="5226656353744862682">📊</tg-emoji>',
    "settings": '<tg-emoji emoji-id="5041975203853239332">⚙️</tg-emoji>',
    "help": '<tg-emoji emoji-id="6100619775426173201">❓</tg-emoji>',
    "back": '<tg-emoji emoji-id="5253997076169115797">🔙</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5195033767969839232">🚀</tg-emoji>',
    "fire": '<tg-emoji emoji-id="5983168105101135589">🔥</tg-emoji>',
    "star": '<tg-emoji emoji-id="5983292843836314861">⭐</tg-emoji>',
    "clock": '<tg-emoji emoji-id="6179440452601647526">⏱️</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5429405838345265327">🔒</tg-emoji>',
    "unlock": '<tg-emoji emoji-id="5372957680174384345">🔓</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5372825386591732174">🗑️</tg-emoji>',
    "add": '<tg-emoji emoji-id="5980797575211520457">➕</tg-emoji>',
    "remove": '<tg-emoji emoji-id="5463121572137022242">➖</tg-emoji>',
    "check": '<tg-emoji emoji-id="5278622189556354905">✔️</tg-emoji>',
    "info": '<tg-emoji emoji-id="6100619775426173201">ℹ️</tg-emoji>',
}

# Country BIN ranges (first 6 digits)
COUNTRY_BINS = {
    "🇺🇸 USA": ["4", "5", "6", "2", "3"],
    "🇬🇧 UK": ["4", "5"],
    "🇨🇦 Canada": ["4", "5"],
    "🇦🇺 Australia": ["4", "5"],
    "🇮🇳 India": ["4", "5"],
    "🇪🇺 Europe": ["4", "5"],
}

# Card type BIN ranges
CARD_TYPE_BINS = {
    "💳 VISA": ["4"],
    "💳 MASTERCARD": ["5"],
    "💳 AMEX": ["3"],
    "💳 DISCOVER": ["6"],
    "💳 RUPAY": ["6"],
}

# ==========================================

# Initialize Clients
bot = Client(
    "bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=1000,
    parse_mode=ParseMode.HTML
)

user = Client(
    "user_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workers=1000
)

START_VIDEO = "https://files.catbox.moe/fevwxk.mp4"

# ============ HELPER FUNCTIONS ============
def get_live_emoji(key):
    """Get live emoji HTML tag"""
    return LIVE_EMOJIS.get(key, "")

def get_colored_button(text, callback_data, color="blue"):
    """Create colored button with emoji"""
    colors = {
        "red": "🔴",
        "green": "🟢", 
        "blue": "🔵",
        "yellow": "🟡",
        "purple": "🟣",
        "orange": "🟠",
        "pink": "🌸",
        "white": "⚪"
    }
    return InlineKeyboardButton(f"{colors.get(color, '🔵')} {text}", callback_data=callback_data)

def remove_duplicates(messages):
    unique_messages = list(dict.fromkeys(messages))
    duplicates_removed = len(messages) - len(unique_messages)
    return unique_messages, duplicates_removed

async def get_bin_info(bin_number):
    """Get BIN information from API"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://binlist.io/lookup/{bin_number}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "brand": data.get("scheme", "Unknown"),
                        "type": data.get("type", "Unknown"),
                        "level": data.get("level", "Unknown"),
                        "bank": data.get("bank", {}).get("name", "Unknown"),
                        "country": data.get("country", {}).get("name", "Unknown"),
                        "country_code": data.get("country", {}).get("alpha2", "UN"),
                        "flag": data.get("country", {}).get("emoji", "🏳️")
                    }
    except:
        pass
    return {"brand": "Unknown", "type": "Unknown", "level": "Unknown", "bank": "Unknown", "country": "Unknown", "flag": "🏳️"}

async def scrape_messages(client, channel_identifier, limit, start_number=None, bin_filter=None, country_filter=None):
    messages = []
    count = 0
    
    patterns = [
        r'(\d{16})\D*(\d{2})\D*(\d{2,4})\D*(\d{3,4})',
        r'(\d{15})\D*(\d{2})\D*(\d{2,4})\D*(\d{4})',
        r'(\d{16})\D*(\d{2})\D*(\d{2,4})\D*(\d{3})',
    ]
    
    try:
        chat = await client.get_chat(channel_identifier)
        
        async for message in client.search_messages(
            chat_id=chat.id,
            limit=limit * 3
        ):
            if count >= limit:
                break
                
            text = message.text or message.caption or ""
            if not text:
                continue
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) == 4:
                        card_number, mo, year, cvv = match
                        if len(year) == 4:
                            year = year[-2:]
                        
                        # Apply BIN filter
                        if bin_filter:
                            if not card_number.startswith(bin_filter):
                                continue
                        
                        # Apply country filter (check BIN)
                        if country_filter:
                            bin_info = await get_bin_info(card_number[:6])
                            if bin_info.get("country_code", "").upper() != country_filter.upper():
                                continue
                        
                        formatted = f"{card_number}|{mo}|{year}|{cvv}"
                        
                        if start_number:
                            if not card_number.startswith(start_number):
                                continue
                        
                        messages.append(formatted)
                        count += 1
                        
                        if count >= limit:
                            break
                if count >= limit:
                    break
                    
    except Exception as e:
        print(f"Scraping error: {e}")
        return []
    
    return messages[:limit]

# ============ MENU FUNCTIONS WITH LIVE EMOJIS ============
def get_main_menu(is_admin=False):
    buttons = [
        [get_colored_button(f"{get_live_emoji('scrape')} 𝙎𝙘𝙧𝙖𝙥𝙚 𝘾𝙝𝙖𝙣𝙣𝙚𝙡", "scrape_channel", "blue")],
        [get_colored_button(f"{get_live_emoji('bin')} 𝙎𝙘𝙧𝙖𝙥𝙚 𝙗𝙮 𝘽𝙄𝙉", "scrape_bin", "green")],
        [get_colored_button(f"{get_live_emoji('country')} 𝙎𝙘𝙧𝙖𝙥𝙚 𝙗𝙮 𝘾𝙤𝙪𝙣𝙩𝙧𝙮", "scrape_country", "purple")],
        [get_colored_button(f"{get_live_emoji('type')} 𝙎𝙘𝙧𝙖𝙥𝙚 𝘽𝙮 𝙏𝙮𝙥𝙚", "scrape_type", "orange")],
        [InlineKeyboardButton(f"{get_live_emoji('channel')} 𝘾𝙝𝙖𝙣𝙣𝙚𝙡", url="https://t.me/froxtbackup")],
        [InlineKeyboardButton(f"{get_live_emoji('user')} 𝙎𝙪𝙥𝙥𝙤𝙧𝙩", url="https://t.me/DARK_FROXT_73")],
    ]
    if is_admin:
        buttons.append([get_colored_button(f"{get_live_emoji('admin')} 𝘼𝙙𝙢𝙞𝙣 𝙋𝙖𝙣𝙚𝙡", "admin_panel", "red")])
    buttons.append([get_colored_button(f"{get_live_emoji('help')} 𝙃𝙚𝙡𝙥", "help", "yellow")])
    return InlineKeyboardMarkup(buttons)

def get_country_menu():
    buttons = []
    countries = ["🇺🇸 USA", "🇬🇧 UK", "🇨🇦 Canada", "🇦🇺 Australia", "🇮🇳 India", "🇪🇺 Europe"]
    row = []
    for i, country in enumerate(countries):
        row.append(InlineKeyboardButton(country, callback_data=f"country_{country.split()[1]}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([get_colored_button(f"{get_live_emoji('back')} 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙈𝙚𝙣𝙪", "back_to_menu", "white")])
    return InlineKeyboardMarkup(buttons)

def get_card_type_menu():
    buttons = [
        [InlineKeyboardButton(f"{get_live_emoji('card')} 𝙑𝙄𝙎𝘼", callback_data="type_visa")],
        [InlineKeyboardButton(f"{get_live_emoji('card')} 𝙈𝘼𝙎𝙏𝙀𝙍𝘾𝘼𝙍𝘿", callback_data="type_mastercard")],
        [InlineKeyboardButton(f"{get_live_emoji('card')} 𝘼𝙈𝙀𝙓", callback_data="type_amex")],
        [InlineKeyboardButton(f"{get_live_emoji('card')} 𝘿𝙄𝙎𝘾𝙊𝙑𝙀𝙍", callback_data="type_discover")],
        [InlineKeyboardButton(f"{get_live_emoji('card')} 𝙍𝙐𝙋𝘼𝙔", callback_data="type_rupay")],
        [get_colored_button(f"{get_live_emoji('back')} 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙈𝙚𝙣𝙪", "back_to_menu", "white")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_bin_menu():
    buttons = [
        [InlineKeyboardButton(f"{get_live_emoji('bin')} 𝙀𝙣𝙩𝙚𝙧 6-𝘿𝙞𝙜𝙞𝙩 𝘽𝙄𝙉", callback_data="enter_bin")],
        [get_colored_button(f"{get_live_emoji('back')} 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙈𝙚𝙣𝙪", "back_to_menu", "white")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_commands_menu():
    buttons = [
        [get_colored_button(f"{get_live_emoji('info')} 𝙑𝙞𝙚𝙬 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨", "view_commands", "blue")],
        [get_colored_button(f"{get_live_emoji('back')} 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙈𝙚𝙣𝙪", "back_to_menu", "white")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_admin_menu():
    buttons = [
        [get_colored_button(f"{get_live_emoji('stats')} 𝘽𝙤𝙩 𝙎𝙩𝙖𝙩𝙨", "bot_stats", "green")],
        [get_colored_button(f"{get_live_emoji('user')} 𝙐𝙨𝙚𝙧 𝙇𝙞𝙨𝙩", "user_list", "blue")],
        [get_colored_button(f"{get_live_emoji('settings')} 𝙎𝙚𝙩𝙩𝙞𝙣𝙜𝙨", "settings", "orange")],
        [get_colored_button(f"{get_live_emoji('back')} 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙈𝙚𝙣𝙪", "back_to_menu", "white")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_scraping_progress_menu(current, total):
    progress = int((current / total) * 20)
    bar = "▓" * progress + "░" * (20 - progress)
    buttons = [
        [InlineKeyboardButton(f"📊 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨: [{current}/{total}] {bar}", callback_data="progress")],
        [get_colored_button(f"{get_live_emoji('back')} 𝘾𝙖𝙣𝙘𝙚𝙡", "cancel_scrape", "red")]
    ]
    return InlineKeyboardMarkup(buttons)

# ============ SESSION STORAGE ============
user_sessions = {}

@bot.on_message(filters.command(["scr"]))
async def scr_cmd(client, message):
    args = message.text.split()[1:]
    if len(args) < 2 or len(args) > 3:
        await message.reply_text(
            f"{get_live_emoji('warning')} 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙐𝙨𝙖𝙜𝙚!\n\n"
            f"𝙐𝙨𝙖𝙜𝙚: `/𝙨𝙘𝙧 [𝙘𝙝𝙖𝙣𝙣𝙚𝙡] [𝙖𝙢𝙤𝙪𝙣𝙩] [𝙤𝙥𝙩𝙞𝙤𝙣𝙖𝙡: 𝙥𝙧𝙚𝙛𝙞𝙭]`\n\n"
            f"𝙀𝙭𝙖𝙢𝙥𝙡𝙚𝙨:\n"
            f"`/𝙨𝙘𝙧 @𝙘𝙝𝙖𝙣𝙣𝙚𝙡 100`\n"
            f"`/𝙨𝙘𝙧 @𝙘𝙝𝙖𝙣𝙣𝙚𝙡 50 4`\n\n"
            f"{get_live_emoji('info')} 𝙐𝙨𝙚 𝙢𝙚𝙣𝙪 𝙛𝙤𝙧 𝙖𝙙𝙫𝙖𝙣𝙘𝙚𝙙 𝙨𝙘𝙧𝙖𝙥𝙞𝙣𝙜!",
            reply_markup=get_commands_menu()
        )
        return
    
    channel_identifier = args[0]
    limit = int(args[1])
    max_lim = ADMIN_LIMIT if message.from_user.id in ADMIN_IDS else DEFAULT_LIMIT
    
    if limit > max_lim:
        await message.reply_text(f"{get_live_emoji('error')} 𝘼𝙢𝙤𝙪𝙣𝙩 𝙚𝙭𝙘𝙚𝙚𝙙𝙨 𝙢𝙖𝙭 𝙡𝙞𝙢𝙞𝙩!\n𝙈𝙖𝙭 𝙡𝙞𝙢𝙞𝙩: `{max_lim}`")
        return
    
    start_number = args[2] if len(args) == 3 else None
    
    if "t.me/" in channel_identifier:
        channel_identifier = channel_identifier.split("t.me/")[-1]
    channel_username = channel_identifier.lstrip('@')
    
    progress_msg = await message.reply_text(
        f"{get_live_emoji('scrape')} 𝙎𝙘𝙧𝙖𝙥𝙞𝙣𝙜 𝙞𝙣 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨...\n\n"
        f"{get_live_emoji('channel')} 𝘾𝙝𝙖𝙣𝙣𝙚𝙡: `{channel_username}`\n"
        f"{get_live_emoji('card')} 𝙇𝙞𝙢𝙞𝙩: `{limit}`\n"
        f"{get_live_emoji('clock')} 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩..."
    )
    
    scrapped_results = await scrape_messages(user, channel_username, limit, start_number)
    unique_messages, duplicates_removed = remove_duplicates(scrapped_results)
    
    if unique_messages:
        file_name = f"scraped_{len(unique_messages)}_{channel_username.replace(' ', '_')}.txt"
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("\n".join(unique_messages))
        
        caption = (
            f"{get_live_emoji('success')} 𝘾𝘾 𝙎𝙘𝙧𝙖𝙥𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮!\n\n"
            f"{get_live_emoji('channel')} 𝙎𝙤𝙪𝙧𝙘𝙚: `{channel_username}`\n"
            f"{get_live_emoji('card')} 𝘼𝙢𝙤𝙪𝙣𝙩: `{len(unique_messages)}`\n"
            f"{get_live_emoji('scrape')} 𝘿𝙪𝙥𝙡𝙞𝙘𝙖𝙩𝙚𝙨 𝙍𝙚𝙢𝙤𝙫𝙚𝙙: `{duplicates_removed}`\n"
            f"{get_live_emoji('user')} 𝙍𝙚𝙦𝙪𝙚𝙨𝙩𝙚𝙙 𝙗𝙮: {message.from_user.mention}"
        )
        
        await progress_msg.delete()
        await client.send_document(
            message.chat.id, 
            file_name, 
            caption=caption, 
            reply_markup=get_main_menu(message.from_user.id in ADMIN_IDS)
        )
        os.remove(file_name)
    else:
        await progress_msg.delete()
        await client.send_message(
            message.chat.id, 
            f"{get_live_emoji('error')} 𝙉𝙤 𝘾𝙧𝙚𝙙𝙞𝙩 𝘾𝙖𝙧𝙙𝙨 𝙁𝙤𝙪𝙣𝙙!", 
            reply_markup=get_main_menu(message.from_user.id in ADMIN_IDS)
        )

@bot.on_message(filters.command(["start"]))
async def start_cmd(client, message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS
    
    max_limit = ADMIN_LIMIT if is_admin else DEFAULT_LIMIT
    
    start_text = (
        f"{get_live_emoji('rocket')} 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 {user_name}!\n\n"
        f"{get_live_emoji('fire')} 𝙄'𝙢 𝙖 𝘾𝙧𝙚𝙙𝙞𝙩 𝘾𝙖𝙧𝙙 𝙎𝙘𝙧𝙖𝙥𝙚𝙧 𝘽𝙤𝙩\n"
        f"{get_live_emoji('star')} 𝙋𝙤𝙬𝙚𝙧𝙛𝙪𝙡 & 𝙁𝙖𝙨𝙩 𝙎𝙘𝙧𝙖𝙥𝙞𝙣𝙜\n\n"
        f"{get_live_emoji('settings')} 𝘾𝙪𝙧𝙧𝙚𝙣𝙩 𝙎𝙚𝙩𝙩𝙞𝙣𝙜𝙨:\n"
        f"• 𝙈𝙖𝙭 𝙇𝙞𝙢𝙞𝙩: `{max_limit}`\n"
        f"• 𝙔𝙤𝙪𝙧 𝙍𝙤𝙡𝙚: `{'𝘼𝙙𝙢𝙞𝙣 👑' if is_admin else '𝙐𝙨𝙚𝙧 👤'}`\n\n"
        f"{get_live_emoji('info')} 𝙐𝙨𝙚 𝙗𝙪𝙩𝙩𝙤𝙣𝙨 𝙗𝙚𝙡𝙤𝙬 𝙩𝙤 𝙣𝙖𝙫𝙞𝙜𝙖𝙩𝙚!"
    )
    
    try:
        await client.send_video(
            message.chat.id,
            START_VIDEO,
            caption=start_text,
            reply_markup=get_main_menu(is_admin)
        )
    except Exception:
        await message.reply_text(start_text, reply_markup=get_main_menu(is_admin))

@bot.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    is_admin = user_id in ADMIN_IDS
    data = callback_query.data
    
    # Store user session for scraping
    if data == "scrape_channel":
        user_sessions[user_id] = {"type": "channel"}
        await callback_query.message.edit_text(
            f"{get_live_emoji('channel')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚:\n\n"
            f"𝙀𝙭𝙖𝙢𝙥𝙡𝙚: `@channel_name`\n\n"
            f"{get_live_emoji('info')} 𝙏𝙝𝙚𝙣 𝙨𝙚𝙣𝙙 𝙩𝙝𝙚 𝙖𝙢𝙤𝙪𝙣𝙩 𝙞𝙣 𝙩𝙝𝙚 𝙣𝙚𝙭𝙩 𝙢𝙚𝙨𝙨𝙖𝙜𝙚.",
            reply_markup=InlineKeyboardMarkup([[get_colored_button(f"{get_live_emoji('back')} 𝘾𝙖𝙣𝙘𝙚𝙡", "back_to_menu", "red")]])
        )
    
    elif data == "scrape_bin":
        user_sessions[user_id] = {"type": "bin", "step": "bin"}
        await callback_query.message.edit_text(
            f"{get_live_emoji('bin')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 6-𝙙𝙞𝙜𝙞𝙩 𝘽𝙄𝙉 𝙣𝙪𝙢𝙗𝙚𝙧:\n\n"
            f"𝙀𝙭𝙖𝙢𝙥𝙡𝙚: `414720`\n\n"
            f"{get_live_emoji('info')} 𝙏𝙝𝙚𝙣 𝙨𝙚𝙣𝙙 𝙩𝙝𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙖𝙣𝙙 𝙖𝙢𝙤𝙪𝙣𝙩.",
            reply_markup=InlineKeyboardMarkup([[get_colored_button(f"{get_live_emoji('back')} 𝘾𝙖𝙣𝙘𝙚𝙡", "back_to_menu", "red")]])
        )
    
    elif data == "scrape_country":
        await callback_query.message.edit_text(
            f"{get_live_emoji('country')} 𝙎𝙚𝙡𝙚𝙘𝙩 𝙖 𝙘𝙤𝙪𝙣𝙩𝙧𝙮:",
            reply_markup=get_country_menu()
        )
    
    elif data.startswith("country_"):
        country_code = data.split("_")[1]
        user_sessions[user_id] = {"type": "country", "filter": country_code, "step": "channel"}
        await callback_query.message.edit_text(
            f"{get_live_emoji('country')} 𝙎𝙚𝙡𝙚𝙘𝙩𝙚𝙙 𝙘𝙤𝙪𝙣𝙩𝙧𝙮: `{country_code}`\n\n"
            f"{get_live_emoji('channel')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚:\n"
            f"𝙀𝙭𝙖𝙢𝙥𝙡𝙚: `@channel_name`\n\n"
            f"{get_live_emoji('info')} 𝙏𝙝𝙚𝙣 𝙨𝙚𝙣𝙙 𝙩𝙝𝙚 𝙖𝙢𝙤𝙪𝙣𝙩.",
            reply_markup=InlineKeyboardMarkup([[get_colored_button(f"{get_live_emoji('back')} 𝘾𝙖𝙣𝙘𝙚𝙡", "back_to_menu", "red")]])
        )
    
    elif data == "scrape_type":
        await callback_query.message.edit_text(
            f"{get_live_emoji('type')} 𝙎𝙚𝙡𝙚𝙘𝙩 𝙘𝙖𝙧𝙙 𝙩𝙮𝙥𝙚:",
            reply_markup=get_card_type_menu()
        )
    
    elif data.startswith("type_"):
        card_type = data.split("_")[1]
        user_sessions[user_id] = {"type": "card_type", "filter": card_type, "step": "channel"}
        await callback_query.message.edit_text(
            f"{get_live_emoji('type')} 𝙎𝙚𝙡𝙚𝙘𝙩𝙚𝙙 𝙘𝙖𝙧𝙙 𝙩𝙮𝙥𝙚: `{card_type.upper()}`\n\n"
            f"{get_live_emoji('channel')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚:\n"
            f"𝙀𝙭𝙖𝙢𝙥𝙡𝙚: `@channel_name`\n\n"
            f"{get_live_emoji('info')} 𝙏𝙝𝙚𝙣 𝙨𝙚𝙣𝙙 𝙩𝙝𝙚 𝙖𝙢𝙤𝙪𝙣𝙩.",
            reply_markup=InlineKeyboardMarkup([[get_colored_button(f"{get_live_emoji('back')} 𝘾𝙖𝙣𝙘𝙚𝙡", "back_to_menu", "red")]])
        )
    
    elif data == "show_commands":
        commands_text = (
            f"{get_live_emoji('info')} 𝘼𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨\n\n"
            f"🔹 **𝙈𝙖𝙞𝙣 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨:**\n"
            f"• `/start` - 𝙎𝙩𝙖𝙧𝙩 𝙩𝙝𝙚 𝙗𝙤𝙩 & 𝙨𝙝𝙤𝙬 𝙢𝙚𝙣𝙪\n"
            f"• `/scr` - 𝙎𝙘𝙧𝙖𝙥𝙚 𝙘𝙧𝙚𝙙𝙞𝙩 𝙘𝙖𝙧𝙙𝙨\n\n"
            f"🔹 **𝘼𝙙𝙫𝙖𝙣𝙘𝙚𝙙 𝙎𝙘𝙧𝙖𝙥𝙞𝙣𝙜:**\n"
            f"• 𝘽𝙮 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 - `/scr @channel 100`\n"
            f"• 𝘽𝙮 𝘽𝙄𝙉 - 𝙐𝙨𝙚 𝙢𝙚𝙣𝙪 𝙗𝙪𝙩𝙩𝙤𝙣\n"
            f"• 𝘽𝙮 𝘾𝙤𝙪𝙣𝙩𝙧𝙮 - 𝙐𝙨𝙚 𝙢𝙚𝙣𝙪 𝙗𝙪𝙩𝙩𝙤𝙣\n"
            f"• 𝘽𝙮 𝘾𝙖𝙧𝙙 𝙏𝙮𝙥𝙚 - 𝙐𝙨𝙚 𝙢𝙚𝙣𝙪 𝙗𝙪𝙩𝙩𝙤𝙣\n\n"
            f"🔹 **𝙀𝙭𝙖𝙢𝙥𝙡𝙚𝙨:**\n"
            f"• `/scr @example 100`\n"
            f"• `/scr @example 50 4`\n\n"
            f"{get_live_emoji('star')} 𝙎𝙪𝙥𝙥𝙤𝙧𝙩: @froxtbackup"
        )
        await callback_query.message.edit_text(commands_text, reply_markup=get_commands_menu())
    
    elif data == "view_commands":
        await callback_query.answer(f"{get_live_emoji('info')} 𝙃𝙚𝙧𝙚 𝙖𝙧𝙚 𝙖𝙡𝙡 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨!", show_alert=True)
    
    elif data == "back_to_menu":
        user_name = callback_query.from_user.first_name
        is_admin = user_id in ADMIN_IDS
        start_text = f"{get_live_emoji('rocket')} 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙗𝙖𝙘𝙠 {user_name}!\n\n{get_live_emoji('info')} 𝘾𝙝𝙤𝙤𝙨𝙚 𝙖𝙣 𝙤𝙥𝙩𝙞𝙤𝙣 𝙗𝙚𝙡𝙤𝙬 👇"
        await callback_query.message.edit_text(start_text, reply_markup=get_main_menu(is_admin))
    
    elif data == "admin_panel" and is_admin:
        admin_text = f"{get_live_emoji('admin')} 𝘼𝙙𝙢𝙞𝙣 𝙋𝙖𝙣𝙚𝙡\n\n𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙖𝙙𝙢𝙞𝙣 𝙘𝙤𝙣𝙩𝙧𝙤𝙡 𝙘𝙚𝙣𝙩𝙚𝙧!\n𝙎𝙚𝙡𝙚𝙘𝙩 𝙖𝙣 𝙤𝙥𝙩𝙞𝙤𝙣 𝙗𝙚𝙡𝙤𝙬:"
        await callback_query.message.edit_text(admin_text, reply_markup=get_admin_menu())
    
    elif data == "bot_stats" and is_admin:
        stats_text = (
            f"{get_live_emoji('stats')} 𝘽𝙤𝙩 𝙎𝙩𝙖𝙩𝙞𝙨𝙩𝙞𝙘𝙨\n\n"
            f"• {get_live_emoji('check')} 𝙎𝙩𝙖𝙩𝙪𝙨: 🟢 𝘼𝙘𝙩𝙞𝙫𝙚\n"
            f"• {get_live_emoji('admin')} 𝘼𝙙𝙢𝙞𝙣𝙨: `{len(ADMIN_IDS)}`\n"
            f"• {get_live_emoji('card')} 𝙎𝙘𝙧𝙖𝙥𝙚 𝙇𝙞𝙢𝙞𝙩: `{DEFAULT_LIMIT:,}`\n"
            f"• {get_live_emoji('crown')} 𝘼𝙙𝙢𝙞𝙣 𝙇𝙞𝙢𝙞𝙩: `{ADMIN_LIMIT:,}`\n\n"
            f"{get_live_emoji('fire')} 𝙈𝙤𝙧𝙚 𝙨𝙩𝙖𝙩𝙨 𝙘𝙤𝙢𝙞𝙣𝙜 𝙨𝙤𝙤𝙣!"
        )
        await callback_query.message.edit_text(stats_text, reply_markup=get_admin_menu())
    
    elif data == "user_list" and is_admin:
        users_text = (
            f"{get_live_emoji('user')} 𝙐𝙨𝙚𝙧 𝙇𝙞𝙨𝙩\n\n"
            f"{get_live_emoji('admin')} 𝘼𝙙𝙢𝙞𝙣𝙨: `{len(ADMIN_IDS)}`\n"
            f"{get_live_emoji('stats')} 𝙏𝙤𝙩𝙖𝙡 𝙪𝙨𝙚𝙧𝙨 𝙩𝙧𝙖𝙘𝙠𝙞𝙣𝙜 𝙘𝙤𝙢𝙞𝙣𝙜 𝙨𝙤𝙤𝙣!\n\n"
            f"{get_live_emoji('info')} 𝙁𝙪𝙡𝙡 𝙪𝙨𝙚𝙧 𝙢𝙖𝙣𝙖𝙜𝙚𝙢𝙚𝙣𝙩 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙖𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚 𝙞𝙣 𝙛𝙪𝙩𝙪𝙧𝙚 𝙪𝙥𝙙𝙖𝙩𝙚𝙨."
        )
        await callback_query.message.edit_text(users_text, reply_markup=get_admin_menu())
    
    elif data == "settings" and is_admin:
        settings_text = (
            f"{get_live_emoji('settings')} 𝘽𝙤𝙩 𝙎𝙚𝙩𝙩𝙞𝙣𝙜𝙨\n\n"
            f"{get_live_emoji('card')} 𝘿𝙚𝙛𝙖𝙪𝙡𝙩 𝙇𝙞𝙢𝙞𝙩: `{DEFAULT_LIMIT:,}`\n"
            f"{get_live_emoji('crown')} 𝘼𝙙𝙢𝙞𝙣 𝙇𝙞𝙢𝙞𝙩: `{ADMIN_LIMIT:,}`\n"
            f"{get_live_emoji('admin')} 𝘼𝙙𝙢𝙞𝙣𝙨: `{len(ADMIN_IDS)}`\n\n"
            f"{get_live_emoji('settings')} 𝙏𝙤 𝙢𝙤𝙙𝙞𝙛𝙮 𝙨𝙚𝙩𝙩𝙞𝙣𝙜𝙨, 𝙚𝙙𝙞𝙩 `𝙘𝙤𝙣𝙛𝙞𝙜.𝙥𝙮`"
        )
        await callback_query.message.edit_text(settings_text, reply_markup=get_admin_menu())
    
    elif data == "help":
        help_text = (
            f"{get_live_emoji('help')} 𝙃𝙚𝙡𝙥 & 𝙎𝙪𝙥𝙥𝙤𝙧𝙩\n\n"
            f"🔹 **𝙃𝙤𝙬 𝙩𝙤 𝙪𝙨𝙚:**\n"
            f"1️⃣ 𝙐𝙨𝙚 `/scr` 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙤𝙧 𝙢𝙚𝙣𝙪 𝙗𝙪𝙩𝙩𝙤𝙣\n"
            f"2️⃣ 𝙋𝙧𝙤𝙫𝙞𝙙𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚\n"
            f"3️⃣ 𝙎𝙥𝙚𝙘𝙞𝙛𝙮 𝙖𝙢𝙤𝙪𝙣𝙩 𝙩𝙤 𝙨𝙘𝙧𝙖𝙥𝙚\n\n"
            f"🔹 **𝘼𝙙𝙫𝙖𝙣𝙘𝙚𝙙 𝙁𝙚𝙖𝙩𝙪𝙧𝙚𝙨:**\n"
            f"• 𝙎𝙘𝙧𝙖𝙥𝙚 𝙗𝙮 𝘽𝙄𝙉 (𝙛𝙞𝙧𝙨𝙩 6 𝙙𝙞𝙜𝙞𝙩𝙨)\n"
            f"• 𝙎𝙘𝙧𝙖𝙥𝙚 𝙗𝙮 𝘾𝙤𝙪𝙣𝙩𝙧𝙮\n"
            f"• 𝙎𝙘𝙧𝙖𝙥𝙚 𝙗𝙮 𝘾𝙖𝙧𝙙 𝙏𝙮𝙥𝙚\n\n"
            f"🔹 **𝙉𝙚𝙚𝙙 𝙝𝙚𝙡𝙥?**\n"
            f"• {get_live_emoji('user')} 𝘾𝙤𝙣𝙩𝙖𝙘𝙩: @DARK_FROXT_73\n"
            f"• {get_live_emoji('channel')} 𝘾𝙝𝙖𝙣𝙣𝙚𝙡: @froxtbackup"
        )
        await callback_query.message.edit_text(help_text, reply_markup=get_main_menu(is_admin))
    
    elif data == "cancel_scrape":
        if user_id in user_sessions:
            del user_sessions[user_id]
        await callback_query.message.edit_text(
            f"{get_live_emoji('error')} 𝙎𝙘𝙧𝙖𝙥𝙞𝙣𝙜 𝙘𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙!",
            reply_markup=get_main_menu(is_admin)
        )
    
    await callback_query.answer()

# ============ HANDLE TEXT INPUT FOR SCRAPING ============
@bot.on_message(filters.text & filters.private & ~filters.command(["start", "scr"]))
async def handle_scrape_input(client, message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        return
    
    session = user_sessions[user_id]
    session_type = session.get("type")
    
    if session_type == "channel":
        # Store channel and ask for amount
        user_sessions[user_id]["channel"] = message.text
        user_sessions[user_id]["step"] = "amount"
        await message.reply_text(
            f"{get_live_emoji('card')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙣𝙪𝙢𝙗𝙚𝙧 𝙤𝙛 𝙘𝙖𝙧𝙙𝙨 𝙩𝙤 𝙨??𝙧𝙖𝙥𝙚:\n\n"
            f"{get_live_emoji('channel')} 𝘾𝙝𝙖𝙣𝙣𝙚𝙡: `{message.text}`\n"
            f"{get_live_emoji('card')} 𝙈𝙖𝙭 𝙡𝙞𝙢𝙞𝙩: `{ADMIN_LIMIT if user_id in ADMIN_IDS else DEFAULT_LIMIT}`"
        )
    
    elif session_type == "bin" and session.get("step") == "bin":
        user_sessions[user_id]["bin"] = message.text
        user_sessions[user_id]["step"] = "channel_bin"
        await message.reply_text(
            f"{get_live_emoji('bin')} 𝘽𝙄𝙉 𝙛𝙞𝙡𝙩𝙚𝙧: `{message.text}`\n\n"
            f"{get_live_emoji('channel')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚:"
        )
    
    elif session_type == "bin" and session.get("step") == "channel_bin":
        user_sessions[user_id]["channel"] = message.text
        user_sessions[user_id]["step"] = "amount_bin"
        await message.reply_text(
            f"{get_live_emoji('channel')} 𝘾𝙝𝙖𝙣𝙣𝙚𝙡: `{message.text}`\n"
            f"{get_live_emoji('bin')} 𝘽𝙄𝙉: `{session['bin']}`\n\n"
            f"{get_live_emoji('card')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙣𝙪𝙢𝙗𝙚𝙧 𝙤𝙛 𝙘𝙖𝙧𝙙𝙨:"
        )
    
    elif session_type == "country" and session.get("step") == "channel":
        user_sessions[user_id]["channel"] = message.text
        user_sessions[user_id]["step"] = "amount_country"
        await message.reply_text(
            f"{get_live_emoji('country')} 𝘾𝙤𝙪𝙣𝙩𝙧𝙮: `{session['filter']}`\n"
            f"{get_live_emoji('channel')} 𝘾𝙝𝙖𝙣𝙣𝙚𝙡: `{message.text}`\n\n"
            f"{get_live_emoji('card')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙣𝙪𝙢𝙗𝙚𝙧 𝙤𝙛 𝙘𝙖𝙧𝙙𝙨:"
        )
    
    elif session_type == "card_type" and session.get("step") == "channel":
        user_sessions[user_id]["channel"] = message.text
        user_sessions[user_id]["step"] = "amount_type"
        await message.reply_text(
            f"{get_live_emoji('type')} 𝘾𝙖𝙧𝙙 𝙏𝙮𝙥𝙚: `{session['filter']}`\n"
            f"{get_live_emoji('channel')} 𝘾𝙝𝙖𝙣𝙣𝙚𝙡: `{message.text}`\n\n"
            f"{get_live_emoji('card')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙣𝙪𝙢𝙗𝙚𝙧 𝙤𝙛 𝙘𝙖𝙧𝙙𝙨:"
        )
    
    elif session.get("step") in ["amount", "amount_bin", "amount_country", "amount_type"]:
        try:
            amount = int(message.text)
            max_lim = ADMIN_LIMIT if user_id in ADMIN_IDS else DEFAULT_LIMIT
            
            if amount > max_lim:
                await message.reply_text(f"{get_live_emoji('error')} 𝘼𝙢𝙤𝙪𝙣𝙩 𝙚𝙭𝙘𝙚𝙚𝙙𝙨 𝙢𝙖𝙭 𝙡𝙞𝙢𝙞𝙩! `{max_lim}`")
                return
            
            channel = session.get("channel")
            bin_filter = session.get("bin")
            country_filter = session.get("filter") if session_type == "country" else None
            card_type_filter = session.get("filter") if session_type == "card_type" else None
            
            # Get bin prefix for card type
            if card_type_filter:
                card_type_map = {
                    "visa": "4",
                    "mastercard": "5",
                    "amex": "3",
                    "discover": "6",
                    "rupay": "6"
                }
                bin_filter = card_type_map.get(card_type_filter.lower())
            
            # Clean channel name
            if "t.me/" in channel:
                channel = channel.split("t.me/")[-1]
            channel_username = channel.lstrip('@')
            
            progress_msg = await message.reply_text(
                "{} 𝙎𝙘𝙧𝙖𝙥𝙞𝙣𝙜 𝙞𝙣 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨...\n\n"
                "{} 𝘾𝙝𝙖𝙣𝙣𝙚𝙡: `{}`\n"
                "{} 𝙇𝙞𝙢𝙞𝙩: `{}`\n"
                "{}{}"
                "{} 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩...".format(
                    get_live_emoji('scrape'),
                    get_live_emoji('channel'), channel_username,
                    get_live_emoji('card'), amount,
                    bin_line, country_line,
                    get_live_emoji('clock')
                )
            )
            
            scrapped_results = await scrape_messages(
                user, channel_username, amount, 
                bin_filter=bin_filter, 
                country_filter=country_filter
            )
            unique_messages, duplicates_removed = remove_duplicates(scrapped_results)
            
            if unique_messages:
                file_name = f"scraped_{len(unique_messages)}_{channel_username}.txt"
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write("\n".join(unique_messages))
                
            # Build conditional lines
            bin_line = f"{get_live_emoji('bin')} 𝘽𝙄𝙉: `{bin_filter}`\n" if bin_filter else ""
            country_line = f"{get_live_emoji('country')} 𝘾𝙤𝙪𝙣𝙩𝙧𝙮: `{country_filter}`\n" if country_filter else ""

            caption = (
                "{} 𝘾𝘾 𝙎𝙘𝙧𝙖𝙥𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮!\n\n"
                "{} 𝙎𝙤𝙪𝙧𝙘𝙚: `{}`\n"
                "{} 𝘼𝙢𝙤𝙪𝙣𝙩: `{}`\n"
                "{} 𝘿𝙪𝙥𝙡𝙞𝙘𝙖𝙩𝙚𝙨: `{}`\n"
                "{}{}"
                "{} 𝙍𝙚𝙦𝙪𝙚𝙨𝙩𝙚𝙙 𝙗𝙮: {}"
            ).format(
                get_live_emoji('success'),
                get_live_emoji('channel'), channel_username,
                get_live_emoji('card'), len(unique_messages),
                get_live_emoji('scrape'), duplicates_removed,
                bin_line, country_line,
                get_live_emoji('user'), message.from_user.mention
            )
                
            await progress_msg.delete()
            await client.send_document(
                    message.chat.id, 
                    file_name, 
                    caption=caption, 
                    reply_markup=get_main_menu(user_id in ADMIN_IDS)
                )
            os.remove(file_name)
    else:
                await progress_msg.delete()
                await message.reply_text(
                    f"{get_live_emoji('error')} 𝙉𝙤 𝘾𝙧𝙚𝙙𝙞𝙩 𝘾𝙖𝙧𝙙𝙨 𝙁𝙤𝙪𝙣𝙙!", 
                    reply_markup=get_main_menu(user_id in ADMIN_IDS)
                )
            
            # Clear session
            del user_sessions[user_id]
            
        except ValueError:
            await message.reply_text(f"{get_live_emoji('error')} 𝙋𝙡𝙚𝙖𝙨𝙚 𝙚𝙣𝙩𝙚𝙧 𝙖 𝙫𝙖𝙡𝙞𝙙 𝙣𝙪𝙢𝙗𝙚𝙧!")
    
    else:
        # For bin input
        if session_type == "bin":
            user_sessions[user_id]["bin"] = message.text
            user_sessions[user_id]["step"] = "channel_bin"
            await message.reply_text(
                f"{get_live_emoji('bin')} 𝘽𝙄𝙉 𝙛𝙞𝙡𝙩𝙚𝙧: `{message.text}`\n\n"
                f"{get_live_emoji('channel')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚:"
            )
        elif session_type == "country":
            user_sessions[user_id]["step"] = "channel"
            await message.reply_text(
                f"{get_live_emoji('country')} 𝘾𝙤𝙪𝙣𝙩𝙧𝙮: `{session['filter']}`\n\n"
                f"{get_live_emoji('channel')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚:"
            )
        elif session_type == "card_type":
            user_sessions[user_id]["step"] = "channel"
            await message.reply_text(
                f"{get_live_emoji('type')} 𝘾𝙖𝙧𝙙 𝙏𝙮𝙥𝙚: `{session['filter']}`\n\n"
                f"{get_live_emoji('channel')} 𝙀𝙣𝙩𝙚𝙧 𝙩𝙝𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚:"
            )

if __name__ == "__main__":
    print("🤖 𝙎𝙩𝙖𝙧𝙩𝙞𝙣𝙜 𝙁𝙧𝙤𝙭𝙩 𝙎𝙘𝙧𝙖𝙥𝙚𝙧 𝘽𝙤𝙩...")
    print("✅ 𝘽𝙤𝙩 𝙞𝙨 𝙧𝙪𝙣𝙣𝙞𝙣𝙜 𝙬𝙞𝙩𝙝 𝙨𝙩𝙮𝙡𝙞𝙨𝙝 𝙛𝙤𝙣𝙩...")
    print("🎨 𝙇𝙞𝙫𝙚 𝙚𝙢𝙤𝙟𝙞𝙨, 𝘾𝙤𝙡𝙤𝙧𝙚𝙙 𝙗𝙪𝙩𝙩𝙤𝙣𝙨 & 𝘼𝙙𝙫𝙖𝙣𝙘𝙚𝙙 𝙨𝙘𝙧𝙖𝙥𝙞𝙣𝙜 𝙚𝙣𝙖𝙗𝙡𝙚𝙙!")
    
    user.start()
    bot.run()                       
