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
ADMIN_LIMIT = 50000
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

def remove_duplicates(messages):
    unique_messages = list(dict.fromkeys(messages))
    duplicates_removed = len(messages) - len(unique_messages)
    return unique_messages, duplicates_removed

async def scrape_messages(client, channel_identifier, limit, start_number=None):
    messages = []
    count = 0
    
    patterns = [
        r'(\d{16})\D*(\d{2})\D*(\d{2,4})\D*(\d{3,4})',
        r'(\d{15})\D*(\d{2})\D*(\d{2,4})\D*(\d{4})',
    ]
    
    try:
        chat = await client.get_chat(channel_identifier)
        
        async for message in client.search_messages(
            chat_id=chat.id,
            limit=limit * 2
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

def get_main_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton("📢 𝘾𝙝𝙖𝙣𝙣𝙚𝙡", url="https://t.me/froxtbackup")],
        [InlineKeyboardButton("👥 𝙎𝙘𝙧𝙖𝙥𝙚𝙧 𝙂𝙧𝙤𝙪𝙥", url="https://t.me/your_scraper_group")],
        [InlineKeyboardButton("📋 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨", callback_data="show_commands")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton("👑 𝘼𝙙𝙢𝙞𝙣 𝙋𝙖𝙣𝙚𝙡", callback_data="admin_panel")])
    buttons.append([InlineKeyboardButton("❓ 𝙃𝙚𝙡𝙥", callback_data="help")])
    return InlineKeyboardMarkup(buttons)

def get_commands_menu():
    buttons = [
        [InlineKeyboardButton("📖 𝙑𝙞𝙚𝙬 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨", callback_data="view_commands")],
        [InlineKeyboardButton("🔙 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙈𝙚𝙣𝙪", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_admin_menu():
    buttons = [
        [InlineKeyboardButton("📊 𝘽𝙤𝙩 𝙎𝙩𝙖𝙩𝙨", callback_data="bot_stats")],
        [InlineKeyboardButton("👥 𝙐𝙨𝙚𝙧 𝙇𝙞𝙨𝙩", callback_data="user_list")],
        [InlineKeyboardButton("⚙️ 𝙎𝙚𝙩𝙩𝙞𝙣𝙜𝙨", callback_data="settings")],
        [InlineKeyboardButton("🔙 𝘽𝙖𝙘𝙠 𝙩𝙤 𝙈𝙚𝙣𝙪", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

@bot.on_message(filters.command(["scr"]))
async def scr_cmd(client, message):
    args = message.text.split()[1:]
    if len(args) < 2 or len(args) > 3:
        await message.reply_text(
            "⚠️ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙐𝙨𝙖𝙜𝙚!\n\n"
            "𝙐𝙨𝙖𝙜𝙚: `/𝙨𝙘𝙧 [𝙘𝙝𝙖𝙣𝙣𝙚𝙡_𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚] [𝙖𝙢𝙤𝙪𝙣𝙩] [𝙤𝙥𝙩𝙞𝙤𝙣𝙖𝙡: 𝙨𝙩𝙖𝙧𝙩𝙞𝙣𝙜_𝙣𝙪𝙢𝙗𝙚𝙧]`\n\n"
            "𝙀𝙭𝙖𝙢𝙥𝙡𝙚𝙨:\n"
            "`/𝙨𝙘𝙧 @𝙘𝙝𝙖𝙣𝙣𝙚𝙡_𝙣𝙖𝙢𝙚 100`\n"
            "`/𝙨𝙘𝙧 @𝙘𝙝𝙖𝙣𝙣𝙚𝙡_𝙣𝙖𝙢𝙚 50 4` → 𝘾𝙖𝙧𝙙𝙨 𝙨𝙩𝙖𝙧𝙩𝙞𝙣𝙜 𝙬𝙞𝙩𝙝 4",
            reply_markup=get_commands_menu()
        )
        return
    
    channel_identifier = args[0]
    limit = int(args[1])
    max_lim = ADMIN_LIMIT if message.from_user.id in ADMIN_IDS else DEFAULT_LIMIT
    
    if limit > max_lim:
        await message.reply_text(f"❌ 𝘼𝙢𝙤𝙪𝙣𝙩 𝙚𝙭𝙘𝙚𝙚𝙙𝙨 𝙢𝙖𝙭 𝙡𝙞𝙢𝙞𝙩!\n𝙈𝙖𝙭 𝙡𝙞𝙢𝙞𝙩: `{max_lim}`")
        return
    
    start_number = args[2] if len(args) == 3 else None
    
    if "t.me/" in channel_identifier:
        channel_identifier = channel_identifier.split("t.me/")[-1]
    channel_username = channel_identifier.lstrip('@')
    
    progress_msg = await message.reply_text(
        "🔄 𝙎𝙘𝙧𝙖𝙥𝙞𝙣𝙜 𝙞𝙣 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨...\n\n"
        f"📢 𝘾𝙝𝙖𝙣𝙣𝙚𝙡: {channel_username}\n"
        f"🔢 𝙇𝙞𝙢𝙞𝙩: {limit}\n"
        "⏳ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩..."
    )
    
    scrapped_results = await scrape_messages(user, channel_username, limit, start_number)
    unique_messages, duplicates_removed = remove_duplicates(scrapped_results)
    
    if unique_messages:
        file_name = f"scraped_{len(unique_messages)}_{channel_username.replace(' ', '_')}.txt"
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("\n".join(unique_messages))
        
        caption = (
            f"✅ 𝘾𝘾 𝙎𝙘𝙧𝙖𝙥𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮!\n\n"
            f"📢 𝙎𝙤𝙪𝙧𝙘𝙚: {channel_username}\n"
            f"💳 𝘼𝙢𝙤𝙪𝙣𝙩: {len(unique_messages)}\n"
            f"🔄 𝘿𝙪𝙥𝙡𝙞𝙘𝙖𝙩𝙚𝙨 𝙍𝙚𝙢𝙤𝙫𝙚𝙙: {duplicates_removed}\n"
            f"👤 𝙍𝙚𝙦𝙪𝙚𝙨𝙩𝙚𝙙 𝙗𝙮: {message.from_user.mention}"
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
            "❌ 𝙉𝙤 𝘾𝙧𝙚𝙙𝙞𝙩 𝘾𝙖𝙧𝙙𝙨 𝙁𝙤𝙪𝙣𝙙!", 
            reply_markup=get_main_menu(message.from_user.id in ADMIN_IDS)
        )

@bot.on_message(filters.command(["start"]))
async def start_cmd(client, message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS
    
    max_limit = ADMIN_LIMIT if is_admin else DEFAULT_LIMIT
    
    start_text = (
        f"🎉 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 {user_name}!\n\n"
        f"🤖 𝙄'𝙢 𝙖 𝘾𝙧𝙚𝙙𝙞𝙩 𝘾𝙖𝙧𝙙 𝙎𝙘𝙧𝙖𝙥𝙚𝙧 𝘽𝙤𝙩\n"
        f"💎 𝙋𝙤𝙬𝙚𝙧𝙛𝙪𝙡 & 𝙁𝙖𝙨𝙩 𝙎𝙘𝙧𝙖𝙥𝙞𝙣𝙜\n\n"
        f"⚙️ 𝘾𝙪𝙧𝙧𝙚𝙣𝙩 𝙎𝙚𝙩𝙩𝙞𝙣𝙜𝙨:\n"
        f"• 𝙈𝙖𝙭 𝙇𝙞𝙢𝙞𝙩: {max_limit}\n"
        f"• 𝙔𝙤𝙪𝙧 𝙍𝙤𝙡𝙚: {'𝘼𝙙𝙢𝙞𝙣 👑' if is_admin else '𝙐𝙨𝙚𝙧 👤'}`\n\n"
        f"🔽 𝙐𝙨𝙚 𝙗𝙪𝙩𝙩𝙤𝙣𝙨 𝙗𝙚𝙡𝙤𝙬 𝙩𝙤 𝙣𝙖𝙫𝙞𝙜𝙖𝙩𝙚!"
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
    
    if data == "show_commands":
        commands_text = (
            "📋 𝘼𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨\n\n"
            "𝙈𝙖𝙞𝙣 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨:\n"
            "`/𝙨𝙩𝙖𝙧𝙩` - 𝙎𝙩𝙖𝙧𝙩 𝙩𝙝𝙚 𝙗𝙤𝙩 & 𝙨𝙝𝙤𝙬 𝙢𝙚𝙣𝙪\n"
            "`/𝙨𝙘𝙧` - 𝙎𝙘𝙧𝙖𝙥𝙚 𝙘𝙧𝙚𝙙𝙞𝙩 𝙘𝙖𝙧𝙙𝙨\n\n"
            "𝙎𝙘𝙧𝙖𝙥𝙞𝙣𝙜 𝙁𝙤𝙧𝙢𝙖𝙩:\n"
            "`/𝙨𝙘𝙧 [𝙘𝙝𝙖𝙣𝙣𝙚𝙡] [𝙖𝙢𝙤𝙪𝙣𝙩]`\n"
            "`/𝙨𝙘𝙧 [𝙘𝙝𝙖𝙣𝙣𝙚𝙡] [𝙖𝙢𝙤𝙪𝙣𝙩] [𝙥𝙧𝙚𝙛𝙞𝙭]`\n\n"
            "𝙀𝙭𝙖𝙢𝙥𝙡𝙚𝙨:\n"
            "`/𝙨𝙘𝙧 @𝙚𝙭𝙖𝙢𝙥𝙡𝙚 100`\n"
            "`/𝙨𝙘𝙧 @𝙚𝙭𝙖𝙢𝙥𝙡𝙚 50 4`\n\n"
            "𝙎𝙪𝙥𝙥𝙤𝙧𝙩: @froxtbackup"
        )
        await callback_query.message.edit_text(commands_text, reply_markup=get_commands_menu())
    
    elif data == "view_commands":
        await callback_query.answer("𝙃𝙚𝙧𝙚 𝙖𝙧𝙚 𝙩𝙝𝙚 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨!", show_alert=True)
    
    elif data == "back_to_menu":
        user_name = callback_query.from_user.first_name
        start_text = f"🎉 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙗𝙖𝙘𝙠 {user_name}!\n\n🤖 𝘾𝙝𝙤𝙤𝙨𝙚 𝙖𝙣 𝙤𝙥𝙩𝙞𝙤𝙣 𝙗𝙚𝙡𝙤𝙬 👇"
        await callback_query.message.edit_text(start_text, reply_markup=get_main_menu(is_admin))
    
    elif data == "admin_panel" and is_admin:
        admin_text = "👑 𝘼𝙙𝙢𝙞𝙣 𝙋𝙖𝙣𝙚𝙡\n\n𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙖𝙙𝙢𝙞𝙣 𝙘𝙤𝙣𝙩𝙧𝙤𝙡 𝙘𝙚𝙣𝙩𝙚𝙧!\n𝙎𝙚𝙡𝙚𝙘𝙩 𝙖𝙣 𝙤𝙥𝙩𝙞𝙤𝙣 𝙗𝙚𝙡𝙤𝙬:"
        await callback_query.message.edit_text(admin_text, reply_markup=get_admin_menu())
    
    elif data == "bot_stats" and is_admin:
        stats_text = (
            "📊 𝘽𝙤𝙩 𝙎𝙩𝙖𝙩𝙞𝙨𝙩𝙞𝙘𝙨\n\n"
            "𝘾𝙤𝙢𝙞𝙣𝙜 𝙎𝙤𝙤𝙣!\n"
            "𝙏𝙝𝙞𝙨 𝙛𝙚𝙖𝙩𝙪𝙧𝙚 𝙬𝙞𝙡𝙡 𝙨𝙝𝙤𝙬:\n"
            "• 𝙏𝙤𝙩𝙖𝙡 𝙪𝙨𝙚𝙧𝙨\n"
            "• 𝙏𝙤𝙩𝙖𝙡 𝙨𝙘𝙧𝙖𝙥𝙚𝙨\n"
            "• 𝘽𝙤𝙩 𝙪𝙥𝙩𝙞𝙢𝙚\n"
            "• 𝘼𝙣𝙙 𝙢𝙤𝙧𝙚..."
        )
        await callback_query.message.edit_text(stats_text, reply_markup=get_admin_menu())
    
    elif data == "user_list" and is_admin:
        users_text = (
            "👥 𝙐𝙨𝙚𝙧 𝙇𝙞𝙨𝙩\n\n"
            f"𝘼𝙙𝙢𝙞𝙣 𝙐𝙨𝙚𝙧𝙨: {len(ADMIN_IDS)}\n"
            "𝘾𝙤𝙢𝙞𝙣𝙜 𝙎𝙤𝙤𝙣!\n"
            "𝙁𝙪𝙡𝙡 𝙪𝙨𝙚𝙧 𝙢𝙖𝙣𝙖𝙜𝙚𝙢𝙚𝙣𝙩 𝙨𝙮𝙨𝙩𝙚𝙢"
        )
        await callback_query.message.edit_text(users_text, reply_markup=get_admin_menu())
    
    elif data == "settings" and is_admin:
        settings_text = (
            "⚙️ 𝘽𝙤𝙩 𝙎𝙚𝙩𝙩𝙞𝙣𝙜𝙨\n\n"
            f"𝘿𝙚𝙛𝙖𝙪𝙡𝙩 𝙇𝙞𝙢𝙞𝙩: `{DEFAULT_LIMIT}`\n"
            f"𝘼𝙙𝙢𝙞𝙣 𝙇𝙞𝙢𝙞𝙩: `{ADMIN_LIMIT}`\n"
            f"𝘼𝙙𝙢𝙞𝙣𝙨: `{len(ADMIN_IDS)}`\n\n"
            "𝙈𝙤𝙙𝙞𝙛𝙮 𝙨𝙚𝙩𝙩𝙞𝙣𝙜𝙨 𝙞𝙣 𝙘𝙤𝙣𝙛𝙞𝙜.𝙥𝙮"
        )
        await callback_query.message.edit_text(settings_text, reply_markup=get_admin_menu())
    
    elif data == "help":
        help_text = (
            "❓ 𝙃𝙚𝙡𝙥 & 𝙎𝙪𝙥𝙥𝙤𝙧𝙩\n\n"
            "𝙃𝙤𝙬 𝙩𝙤 𝙪𝙨𝙚:\n"
            "1️⃣ 𝙐𝙨𝙚 `/𝙨𝙘𝙧` 𝙘𝙤𝙢𝙢𝙖𝙣𝙙\n"
            "2️⃣ 𝙋𝙧𝙤𝙫𝙞𝙙𝙚 𝙘𝙝𝙖𝙣𝙣𝙚𝙡 𝙪𝙨𝙚𝙧𝙣𝙖𝙢𝙚\n"
            "3️⃣ 𝙎𝙥𝙚𝙘𝙞𝙛𝙮 𝙖𝙢𝙤𝙪𝙣𝙩 𝙩𝙤 𝙨𝙘𝙧𝙖𝙥𝙚\n\n"
            "𝙉𝙚𝙚𝙙 𝙝𝙚𝙡𝙥?\n"
            "𝘾𝙤𝙣𝙩𝙖𝙘𝙩 @DARK_FROXT_73 AAH \n\n"
            "𝘾𝙝𝙖𝙣𝙣𝙚𝙡: @froxtbackup"
        )
        await callback_query.message.edit_text(help_text, reply_markup=get_main_menu(is_admin))
    
    await callback_query.answer()

if __name__ == "__main__":
    print("🤖 𝙎𝙩𝙖𝙧𝙩𝙞𝙣𝙜 𝙁𝙧𝙤𝙭𝙩 𝙎𝙘𝙧𝙖𝙥𝙚𝙧 𝘽𝙤𝙩...")
    print("✅ 𝘽𝙤𝙩 𝙞𝙨 𝙧𝙪𝙣𝙣𝙞𝙣𝙜 𝙬𝙞𝙩𝙝 𝙨𝙩𝙮𝙡𝙞𝙨𝙝 𝙛𝙤𝙣𝙩...")
    
    user.start()
    bot.run()
