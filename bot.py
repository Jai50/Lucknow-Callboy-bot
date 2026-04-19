"""
LUCKNOW GLEEDEN BOT - HINDI + ENGLISH
24x7 Timing | FULLY FIXED - WITH ADMIN REPLY SYSTEM & CANCELLATION ALERT
"""

import os
import re
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# ============================================
# FLASK APP FOR RENDER HEALTH CHECK
# ============================================
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Bot is running!", 200

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# ============================================
# BOT CONFIGURATION
# ============================================
TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 1919682117))

print("=" * 50)
print(f"🤖 TOKEN: {'✅ Loaded' if TOKEN else '❌ Missing'}")
print(f"👑 ADMIN_ID: {ADMIN_ID}")
print("=" * 50)

# Storage
user_data = {}
bookings = {}
user_active_booking = {}

# ============================================
# SHOW MAIN MENU
# ============================================

async def show_main_menu(message, user_id=None):
    has_booking = user_id and user_id in user_active_booking
    
    if has_booking:
        booking_id = user_active_booking[user_id].get("booking_id", "Unknown")
        keyboard = [
            [InlineKeyboardButton("📅 Book Now", callback_data="menu_book")],
            [InlineKeyboardButton("ℹ️ Service Info", callback_data="menu_info")],
            [InlineKeyboardButton("📞 Contact Us", callback_data="menu_contact")],
            [InlineKeyboardButton("❌ Cancel Booking", callback_data="menu_cancel_booking")]
        ]
        menu_text = f"""
🔥 *LUCKNOW GLEEDEN SERVICE* 🔥
👩 *Only for Female*

📋 *Active Booking ID:* `{booking_id}`

📌 Type "book" or "hi" for new booking
"""
    else:
        keyboard = [
            [InlineKeyboardButton("📅 Book Now", callback_data="menu_book")],
            [InlineKeyboardButton("ℹ️ Service Info", callback_data="menu_info")],
            [InlineKeyboardButton("📞 Contact Us", callback_data="menu_contact")],
            [InlineKeyboardButton("❌ Cancel Booking", callback_data="menu_cancel_booking")]
        ]
        menu_text = """
🔥 *LUCKNOW GLEEDEN SERVICE* 🔥
👩 *Only for Female*

✨ Type "book" or "hi" to start booking ✨
"""
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')

# ============================================
# FORWARD USER MESSAGE TO ADMIN
# ============================================

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text):
    """Forward any user message to admin so admin can reply"""
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name
    username = f"@{user.username}" if user.username else "No username"
    
    admin_msg = f"""
📩 *NEW MESSAGE FROM USER*

👤 Name: {user_name}
🆔 User ID: `{user_id}`
📝 Username: {username}

━━━━━━━━━━━━━━━━
💬 *Message:* 
{message_text}
━━━━━━━━━━━━━━━━

💡 *To reply:* Reply to this message with your response
"""
    
    try:
        await context.bot.send_message(
            ADMIN_ID, 
            admin_msg,
            parse_mode='Markdown'
        )
        print(f"✅ Message from {user_name} ({user_id}) forwarded to admin")
    except Exception as e:
        print(f"❌ Failed to forward to admin: {e}")

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await show_main_menu(update.message, user_id)
    
    # Notify admin that new user started the bot
    user = update.effective_user
    await context.bot.send_message(
        ADMIN_ID,
        f"🟢 *NEW USER STARTED BOT*\n\n👤 {user.first_name}\n🆔 ID: `{user.id}`\n📝 @{user.username if user.username else 'N/A'}",
        parse_mode='Markdown'
    )

async def book_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in user_data:
        del user_data[user_id]
    
    user_data[user_id] = {"step": "service"}
    
    keyboard = [
        [InlineKeyboardButton("💆‍♂️ Massage", callback_data="book_massage")],
        [InlineKeyboardButton("🤝 Casual Meet Up", callback_data="book_casual")],
        [InlineKeyboardButton("☀️ Day Service", callback_data="book_day")],
        [InlineKeyboardButton("🌙 Night Package", callback_data="book_night")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            "📅 *NEW BOOKING*\n\nSelect service:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📅 *NEW BOOKING*\n\nSelect service:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = """
ℹ️ *SERVICE INFO*

💆‍♂️ Massage - Day OR Night
🤝 Casual Meet Up - Day OR Night
☀️ Day Service - 1,2,4 Hours
🌙 Night Package - 1,2,4 Hours, Full Night

✅ 24x7 | Only for Female
"""
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        await context.bot.send_message(
            ADMIN_ID, 
            f"📞 CONTACT REQUEST\nFrom: {user.first_name} (@{user.username or 'N/A'})\nID: {user.id}"
        )
        print(f"✅ Contact request sent to admin")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    await update.message.reply_text("✅ Request sent to admin! We'll contact you shortly.", parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📌 *Available Commands*

/book - Start new booking
/info - Service information
/contact - Contact admin
/cancel - Cancel booking
/send [ID] [msg] - Send message to user (Admin only)

💡 Just type 'book' or 'hi' to start booking!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ============================================
# SEND MESSAGE TO ANY USER (ADMIN ONLY)
# ============================================

async def send_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to send message to any user by ID"""
    user_id = update.effective_user.id
    
    # Only admin can use this command
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Only admin can use this command!")
        return
    
    # Command format: /send 123456789 your message
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ Usage: /send [user_id] [message]\nExample: /send 123456789 Hello!")
        return
    
    try:
        target_id = int(args[0])
        message = " ".join(args[1:])
        
        await context.bot.send_message(chat_id=target_id, text=f"👑 *Admin:* {message}", parse_mode='Markdown')
        await update.message.reply_text(f"✅ Message sent to user `{target_id}`!", parse_mode='Markdown')
        print(f"✅ Message sent to {target_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID! Must be a number.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)[:100]}")

# ============================================
# ADMIN REPLY SYSTEM - Reply to user messages
# ============================================

async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When admin replies to a forwarded message, send that reply to the original user"""
    admin_id = update.effective_user.id
    
    # Only admin can use this
    if admin_id != ADMIN_ID:
        return
    
    # Check if this is a reply to a message
    if not update.message.reply_to_message:
        return
    
    replied_msg = update.message.reply_to_message
    reply_text = update.message.text
    
    # Try to extract user ID from the replied message
    target_id = None
    
    # Pattern 1: "🆔 User ID: `123456789`" (from forwarded message)
    match = re.search(r"🆔 User ID: `(\d+)`", replied_msg.text or "")
    if match:
        target_id = int(match.group(1))
    
    # Pattern 2: "User ID: 123456789" (plain text)
    if not target_id:
        match = re.search(r"User ID: (\d+)", replied_msg.text or "")
        if match:
            target_id = int(match.group(1))
    
    # Pattern 3: "ID: 123456789"
    if not target_id:
        match = re.search(r"ID: (\d+)", replied_msg.text or "")
        if match:
            target_id = int(match.group(1))
    
    if target_id:
        try:
            # Send the reply to the user
            await context.bot.send_message(
                chat_id=target_id,
                text=f"👑 *Admin:* {reply_text}",
                parse_mode='Markdown'
            )
            # Confirm to admin that reply was sent
            await update.message.reply_text(f"✅ Reply sent to user `{target_id}`!", parse_mode='Markdown')
            print(f"✅ Admin replied to user {target_id}")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send reply: {str(e)[:100]}")
            print(f"❌ Failed to send reply to {target_id}: {e}")
    else:
        await update.message.reply_text(
            "❌ Could not find User ID in the replied message.\n\n"
            "Make sure you are replying to a message that contains the User ID.\n"
            "Use /send [ID] [message] as an alternative."
        )

# ============================================
# CANCEL BOOKING - WITH ADMIN ALERT
# ============================================

async def cancel_booking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    
    if user_id in user_active_booking:
        booking_id = user_active_booking[user_id].get("booking_id", "Unknown")
        booking_data = user_active_booking[user_id]
        
        keyboard = [
            [InlineKeyboardButton("✅ Yes, Cancel", callback_data=f"confirm_yes_{booking_id}")],
            [InlineKeyboardButton("❌ No, Keep", callback_data="confirm_no")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"⚠️ Cancel Booking `{booking_id}`?", reply_markup=reply_markup, parse_mode='Markdown')
    else:
        keyboard = [[InlineKeyboardButton("📅 Book Now", callback_data="menu_book")]]
        await update.message.reply_text("❌ No active booking found!", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ============================================
# EASY TYPE HANDLER
# ============================================

async def easy_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    text = message.text.lower().strip()
    
    # Forward any user message to admin (so admin can reply)
    if user_id != ADMIN_ID:
        await forward_to_admin(update, context, message.text)
    
    if user_id in user_data:
        if text in ["cancel", "रद्द", "exit"]:
            if user_id in user_data:
                del user_data[user_id]
            await cancel_booking_command(update, context)
            return
        await handle_booking_flow(update, context)
        return
    
    if text in ["book", "booking", "बुक", "hi", "hello", "hey", "hy", "hii"]:
        await book_command(update, context)
    elif text in ["info", "information", "जानकारी"]:
        await info_command(update, context)
    elif text in ["contact", "support", "संपर्क"]:
        await contact_command(update, context)
    elif text in ["cancel", "रद्द"]:
        await cancel_booking_command(update, context)
    elif text in ["start", "menu"]:
        await show_main_menu(message, user_id)
    else:
        await message.reply_text("📝 Type 'book' or 'hi' to start booking")

# ============================================
# BOOKING FLOW HANDLER
# ============================================

async def handle_booking_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    text = message.text.strip()
    
    if user_id not in user_data:
        return
    
    current_step = user_data[user_id].get("step")
    
    if current_step == "age":
        user_data[user_id]["age"] = text
        user_data[user_id]["step"] = "location"
        await message.reply_text(
            f"✅ Age: *{text}*\n\n📍 *Share your LOCATION (Area Name)*\nExample: Gomti Nagar, Lucknow",
            parse_mode='Markdown'
        )
    
    elif current_step == "location":
        user_data[user_id]["location"] = text
        user_data[user_id]["step"] = "contact_details"
        
        keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data="skip_contact")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            f"✅ Location: *{text}*\n\n📞 *Share CONTACT (Optional)*\nExample: 9876543210\nOr click SKIP",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif current_step == "contact_details":
        await complete_booking(update, context, user_id, message, text)

# ============================================
# CALLBACK HANDLER
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "main_menu":
        await show_main_menu(query.message, user_id)
    
    elif data == "menu_book":
        await book_command(update, context)
    
    elif data == "menu_info":
        await query.edit_message_text(
            "ℹ️ *SERVICE INFO*\n\n💆‍♂️ Massage: Day/Night\n🤝 Casual Meet Up: Day/Night\n☀️ Day Service: 1,2,4 Hours\n🌙 Night Package: 1,2,4 Hours, Full Night",
            parse_mode='Markdown'
        )
    
    elif data == "menu_contact":
        user = query.from_user
        try:
            await context.bot.send_message(ADMIN_ID, f"📞 Contact from {user.first_name} (@{user.username or 'N/A'})\nID: {user.id}")
            await query.edit_message_text("✅ Request sent to admin!", parse_mode='Markdown')
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", parse_mode='Markdown')
    
    elif data == "menu_cancel_booking":
        if user_id in user_active_booking:
            booking_id = user_active_booking[user_id].get("booking_id", "Unknown")
            keyboard = [
                [InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{booking_id}")],
                [InlineKeyboardButton("❌ No", callback_data="confirm_no")],
            ]
            await query.edit_message_text(f"⚠️ Cancel `{booking_id}`?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ No active booking!", parse_mode='Markdown')
    
    # ========== CONFIRM YES - WITH CANCELLATION ALERT ==========
    elif data.startswith("confirm_yes_"):
        booking_id = data.replace("confirm_yes_", "")
        if user_id in user_active_booking:
            booking_data = user_active_booking[user_id]
            
            # Send cancellation alert to admin
            username_display = f"@{booking_data.get('username', 'N/A')}" if booking_data.get('username') else "N/A"
            
            cancel_msg = f"""🔔 <b>BOOKING CANCELLED</b> 🔔

━━━━━━━━━━━━━━━━
<b>CUSTOMER DETAILS:</b>
━━━━━━━━━━━━━━━━
👤 Name: {booking_data.get('user_name', 'Unknown')}
📝 Username: {username_display}
🆔 User ID: <code>{user_id}</code>
🎂 Age: {booking_data.get('age', 'N/A')}
👥 Status: {booking_data.get('status', 'N/A')}
📞 Contact: {booking_data.get('contact', 'N/A')}

━━━━━━━━━━━━━━━━
<b>CANCELLED BOOKING DETAILS:</b>
━━━━━━━━━━━━━━━━
💼 Service: {booking_data.get('service', 'Unknown')} {booking_data.get('service_type', '')}
⏱️ Duration: {booking_data.get('duration', 'Unknown')}
📍 Place: {booking_data.get('place', 'Unknown')}
🏠 Location: {booking_data.get('location', 'Unknown')}
📋 Booking ID: <code>{booking_id}</code>

🕐 Cancelled at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            try:
                await context.bot.send_message(ADMIN_ID, cancel_msg, parse_mode='HTML')
                print(f"✅ Cancellation alert sent to admin for booking {booking_id}")
            except Exception as e:
                print(f"❌ Failed to send cancellation alert: {e}")
                # Simple fallback
                await context.bot.send_message(ADMIN_ID, f"🔔 BOOKING CANCELLED\nUser: {booking_data.get('user_name')}\nBooking ID: {booking_id}")
            
            del user_active_booking[user_id]
            await query.edit_message_text(f"✅ Booking `{booking_id}` cancelled!", parse_mode='Markdown')
    
    elif data == "confirm_no":
        await query.edit_message_text("✅ Booking kept active!", parse_mode='Markdown')
    
    # ========== SERVICE SELECTION ==========
    elif data == "book_massage":
        user_data[user_id] = {"service": "Massage", "step": "day_night"}
        keyboard = [
            [InlineKeyboardButton("☀️ Day", callback_data="massage_day")],
            [InlineKeyboardButton("🌙 Night", callback_data="massage_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text("✅ *Massage*\n\nSelect Day or Night:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "massage_day":
        user_data[user_id]["type"] = "Day"
        user_data[user_id]["step"] = "duration"
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🔙 Back", callback_data="book_massage")]
        ]
        await query.edit_message_text("✅ Massage - *Day*\n\nSelect duration:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "massage_night":
        user_data[user_id]["type"] = "Night"
        user_data[user_id]["step"] = "duration"
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="book_massage")]
        ]
        await query.edit_message_text("✅ Massage - *Night*\n\nSelect duration:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "book_casual":
        user_data[user_id] = {"service": "Casual Meet Up", "step": "day_night"}
        keyboard = [
            [InlineKeyboardButton("☀️ Day", callback_data="casual_day")],
            [InlineKeyboardButton("🌙 Night", callback_data="casual_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text("✅ *Casual Meet Up*\n\nSelect Day or Night:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "casual_day":
        user_data[user_id]["type"] = "Day"
        user_data[user_id]["step"] = "duration"
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🔙 Back", callback_data="book_casual")]
        ]
        await query.edit_message_text("✅ Casual Meet Up - *Day*\n\nSelect duration:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "casual_night":
        user_data[user_id]["type"] = "Night"
        user_data[user_id]["step"] = "duration"
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="book_casual")]
        ]
        await query.edit_message_text("✅ Casual Meet Up - *Night*\n\nSelect duration:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "book_day":
        user_data[user_id] = {"service": "Day Service", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text("✅ *Day Service*\n\nSelect duration:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "book_night":
        user_data[user_id] = {"service": "Night Package", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text("✅ *Night Package*\n\nSelect duration:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    # ========== DURATION ==========
    elif data in ["dur_1", "dur_2", "dur_4", "dur_night"]:
        duration_map = {"dur_1": "1 Hour", "dur_2": "2 Hours", "dur_4": "4 Hours", "dur_night": "Full Night"}
        user_data[user_id]["duration"] = duration_map[data]
        user_data[user_id]["step"] = "place"
        
        keyboard = [
            [InlineKeyboardButton("🏢 Public Place", callback_data="place_public")],
            [InlineKeyboardButton("🏨 Hotel", callback_data="place_hotel")],
            [InlineKeyboardButton("🏠 Your Home", callback_data="place_home")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        
        service = user_data[user_id].get("service", "Service")
        type_info = user_data[user_id].get("type", "")
        type_info = f" ({type_info})" if type_info else ""
        
        await query.edit_message_text(
            f"✅ *{service}{type_info}* | Duration: *{duration_map[data]}*\n\n📍 Where?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ========== PLACE ==========
    elif data in ["place_public", "place_hotel", "place_home"]:
        place_map = {"place_public": "Public Place", "place_hotel": "Hotel", "place_home": "Your Home"}
        user_data[user_id]["place"] = place_map[data]
        user_data[user_id]["step"] = "status"
        
        keyboard = [
            [InlineKeyboardButton("👤 Single", callback_data="status_single")],
            [InlineKeyboardButton("👥 Couple", callback_data="status_couple")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            f"✅ Place: *{place_map[data]}*\n\n👥 Single or Couple?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ========== STATUS ==========
    elif data in ["status_single", "status_couple"]:
        status_map = {"status_single": "Single", "status_couple": "Couple"}
        user_data[user_id]["status"] = status_map[data]
        user_data[user_id]["step"] = "age"
        await query.edit_message_text(f"✅ Status: *{status_map[data]}*\n\n🎂 Enter your age:", parse_mode='Markdown')
    
    elif data == "skip_contact":
        await skip_contact(update, context)

# ============================================
# SKIP CONTACT
# ============================================

async def skip_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in user_data or user_data[user_id].get("step") != "contact_details":
        await query.edit_message_text("Type 'book' to start")
        return
    
    await complete_booking(update, context, user_id, query.message, "Not provided")

# ============================================
# COMPLETE BOOKING - FIXED VERSION
# ============================================

async def complete_booking(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, message, contact_details):
    """Complete booking and send to admin - FIXED with HTML parse mode"""
    
    print(f"\n📝 COMPLETING BOOKING FOR USER: {user_id}")
    
    try:
        service = user_data[user_id].get("service", "Unknown")
        duration = user_data[user_id].get("duration", "Unknown")
        place = user_data[user_id].get("place", "Unknown")
        status = user_data[user_id].get("status", "Unknown")
        age = user_data[user_id].get("age", "Unknown")
        location = user_data[user_id].get("location", "Unknown")
        service_type = user_data[user_id].get("type", "")
        contact = contact_details
        booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        user = message.from_user
        
        print(f"📋 Booking ID: {booking_id}")
        print(f"👤 Customer: {user.first_name}")
        
        # Store booking
        booking_data = {
            "user_id": user_id, "user_name": user.first_name, "username": user.username,
            "service": service, "service_type": service_type, "duration": duration,
            "place": place, "status": status, "age": age, "location": location,
            "contact": contact, "booking_id": booking_id, "time": datetime.now().isoformat()
        }
        bookings[booking_id] = booking_data
        user_active_booking[user_id] = booking_data
        
        # Keyboard after booking for user
        keyboard = [
            [InlineKeyboardButton("📅 New Booking", callback_data="menu_book")],
            [InlineKeyboardButton("❌ Cancel Booking", callback_data="menu_cancel_booking")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send confirmation to customer
        await message.reply_text(f"""
✅ *BOOKING CONFIRMED!* ✅

📋 *Booking ID:* `{booking_id}`

💼 Service: {service} {service_type}
⏱️ Duration: {duration}
📍 Place: {place}
👥 Status: {status}
🎂 Age: {age}
🏠 Location: {location}
📞 Contact: {contact}

*Our associate will contact you shortly!*
""", reply_markup=reply_markup, parse_mode='Markdown')
        
        # Build admin message - BEAUTIFUL FORMAT with HTML (more stable)
        username_display = f"@{user.username}" if user.username else "N/A"
        
        admin_msg = f"""🔔 <b>NEW BOOKING</b> 🔔

━━━━━━━━━━━━━━━━
<b>CUSTOMER DETAILS:</b>
━━━━━━━━━━━━━━━━
👤 Name: {user.first_name}
📝 Username: {username_display}
🆔 User ID: <code>{user_id}</code>
🎂 Age: {age}
👥 Status: {status}
📞 Contact: {contact}

━━━━━━━━━━━━━━━━
<b>BOOKING DETAILS:</b>
━━━━━━━━━━━━━━━━
💼 Service: {service} {service_type}
⏱️ Duration: {duration}
📍 Place: {place}
🏠 Location: {location}
📋 Booking ID: <code>{booking_id}</code>

🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <i>To reply to this user:</i> Use /send {user_id} [message] or reply to this message"""
        
        # Send to admin - using HTML parse mode (more reliable than Markdown)
        await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
        print(f"✅ Beautiful formatted booking sent to admin {ADMIN_ID}")
        
        # Clear user data
        if user_id in user_data:
            del user_data[user_id]
            
    except Exception as e:
        print(f"❌ ERROR in complete_booking: {e}")
        # Send simple fallback message in case of error
        try:
            await context.bot.send_message(ADMIN_ID, f"🔔 NEW BOOKING!\nUser: {user.first_name}\nService: {service}\nID: {booking_id}\nUser ID: {user_id}")
        except:
            pass
        await message.reply_text(f"❌ Error: {str(e)[:100]}")

# ============================================
# MAIN
# ============================================

def main():
    print("=" * 50)
    print("🚀 LUCKNOW GLEEDEN BOT STARTING...")
    print("=" * 50)
    
    # Start Flask
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Flask server started")
    
    # Create bot
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel_booking_command))
    app.add_handler(CommandHandler("send", send_to_user))
    
    # Admin reply handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), admin_reply_handler))
    
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, easy_type_handler))
    
    print("✅ Bot started!")
    print("✅ FEATURES:")
    print("   • /send [ID] [message] - Send message to any user")
    print("   • Reply to any forwarded message - Auto sends reply to user")
    print("   • All user messages are forwarded to admin")
    print("   • Beautiful HTML formatted booking alerts!")
    print("   • Cancellation alerts sent to admin! ✅")
    print("=" * 50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
