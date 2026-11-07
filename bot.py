import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# --- CONFIGURATION ---
BOT_TOKEN = "9028198172:AAFd0mqwylwQHZNkr-CeTf6bS_KDbp68QDg" 
API_BASE = "https://ft-simdb.ftshehryar10044.workers.dev/ft/api?num="
CHANNEL_URL = "https://t.me/Nawab_Zada_Hacker"
GROUP_URL = "https://t.me/Nawab_otpGroup"
DEVELOPER_SIGNATURE = "👨‍💻 Developer: <b>Nawab Zada Hacker</b> 🦅☠️"

verified_users = set()

def is_verified(user_id):
    return user_id in verified_users

def verify_user(user_id):
    verified_users.add(user_id)

async def start(update: Update, context: Application):
    """Sends the welcome message and verification buttons."""
    chat = update.effective_chat
    user = update.effective_user
    
    if is_verified(user.id):
        await send_search_prompt(update)
        return

    text = (
        f"👋 <b>Welcome {user.first_name}!</b>\n\n"
        f"To use the <b>Nawab Sim Database</b>, you must join our community first.\n\n"
        f"📢 <b>Channel:</b> {CHANNEL_URL}\n"
        f"👥 <b>Group:</b> {GROUP_URL}\n\n"
        f"👇 Click <b>Verify</b> below to continue."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Verify Now", callback_data="verify"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await chat.send_message(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def handle_verification(update: Update, context: Application):
    """Checks if user is member of channel/group and verifies them."""
    query = update.callback_query
    user = query.from_user
    chat = update.effective_chat
    
    # Get chat IDs for the channel and group (Admin ID or Link)
    # Note: For 'is_member' check, we need the chat IDs. 
    # Since we have links, we resolve them or use the username check via bot API if possible.
    # However, standard practice is to use chat IDs. 
    # For this script, we will assume the bot is admin of both or we use the 'chat_member' API.
    
    # Let's fetch the chat IDs dynamically if not stored, or use a simplified check.
    # To make this robust without hardcoding IDs, we can ask the bot to check membership 
    # by sending a test or checking the 'is_member' status if the bot is admin.
    # Since I don't have the specific Chat IDs (just links), I will use a common trick:
    # The user must click the buttons. We will verify by checking if the user 
    # is actually in those chats using the Bot API.
    
    # We need the numeric chat IDs for Channel and Group.
    # You should get these from @userinfobot or by adding your bot as admin there.
    # Let's assume you will add these constants. 
    # If you don't have IDs, the check below will fail. 
    # I will add placeholders for CHAT_ID_CHANNEL and CHAT_ID_GROUP.
    
    # IMPORTANT: Replace these with the actual numeric Chat IDs of your Channel and Group.
    # You can get them by forwarding a message from the channel to @userinfobot.
    CHANNEL_ID = -1001234567890  # <--- REPLACE WITH YOUR CHANNEL ID
    GROUP_ID = -1009876543210    # <--- REPLACE WITH YOUR GROUP ID

    try:
        # Check Channel Membership
        channel_status = await context.bot.get_chat_member(CHANNEL_ID, user.id)
        is_in_channel = channel_status.status in ['member', 'administrator', 'creator']
        
        # Check Group Membership
        group_status = await context.bot.get_chat_member(GROUP_ID, user.id)
        is_in_group = group_status.status in ['member', 'administrator', 'creator']
        
    except telegram.error.BadRequest as e:
        await query.answer(f"Error checking status: {e}")
        return

    if is_in_channel and is_in_group:
        verify_user(user.id)
        await query.answer("Verification Successful!")
        
        success_text = (
            f"✅ <b>Verified!</b>\n\n"
            f"Welcome to <b>Nawab Sim Database</b>.\n"
            f"You can now search for SIM details.\n\n"
            f"🔍 <i>Send a phone number to search (e.g., 03001234567)</i>"
        )
        await chat.send_message(success_text, parse_mode=ParseMode.HTML)
    else:
        missing = []
        if not is_in_channel: missing.append("Channel")
        if not is_in_group: missing.append("Group")
        
        error_text = (
            f"❌ <b>Verification Failed.</b>\n\n"
            f"You are not a member of the required {', '.join(missing)}.\n\n"
            f"Please join them and click <b>Verify</b> again."
        )
        await query.answer("You need to join both!", show_alert=True)
        # Re-send the main menu or just inform
        await chat.send_message(error_text, parse_mode=ParseMode.HTML)

async def send_search_prompt(update: Update):
    """Sends a prompt asking for a number."""
    chat = update.effective_chat
    text = (
        f"🔍 <b>Search Ready</b>\n\n"
        f"Please send a phone number to look up.\n"
        f"Example: <code>03001234567</code>"
    )
    await chat.send_message(text, parse_mode=ParseMode.HTML)

async def handle_text(update: Update, context: Application):
    """Handles the number input and queries the API."""
    chat = update.effective_chat
    user = update.effective_user
    text = update.message.text
    
    # Basic validation: ensure it looks like a number
    if not text.replace(" ", "").isdigit():
        await chat.send_message("❌ Please enter a valid phone number consisting only of digits.")
        return

    # Clean the number (remove spaces, keep digits)
    clean_num = "".join(filter(str.isdigit, text))
    
    # Optional: Ensure it's a reasonable length (e.g., 10-15 digits)
    if len(clean_num) < 9:
        await chat.send_message("⚠️ That number seems too short. Please try again.")
        return

    await chat.send_chat_action(chat.id, action="typing")
    
    try:
        # Call the API
        import requests
        url = f"{API_BASE}{clean_num}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            await chat.send_message(f"⚠️ API returned status {response.status_code}. Please try again.")
            return
            
        data = response.json()
        
        # Format the output
        # Assuming the API returns a JSON object with fields like 'name', 'operator', etc.
        # I will format it generically. If the structure is specific, adjust the keys below.
        
        result_text = f"📊 <b>Result for {clean_num}</b>\n\n"
        
        # Common fields in SIM DB APIs. Adjust these keys based on your API's actual JSON response.
        # Example keys: 'name', 'operator', 'status', 'imsi', 'iccid', 'date'
        
        for key, value in data.items():
            if value is not None:
                # Capitalize first letter of key for display
                display_key = key.capitalize().replace('_', ' ')
                result_text += f"🔹 <b>{display_key}:</b> {value}\n"
        
        result_text += f"\n\n{DEVELOPER_SIGNATURE}"
        
        await chat.send_message(result_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        
    except requests.exceptions.RequestException as e:
        await chat.send_message(f"❌ Network Error: {e}")
    except ValueError:
        await chat.send_message("❌ Invalid response from API.")

def main():
    """Runs the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CallbackQueryHandler(handle_verification))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
