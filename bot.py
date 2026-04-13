"""
LUCKNOW GLEEDEN BOT - HINDI + ENGLISH
24x7 Timing | No Photoshoot | ADMIN MESSAGE FIXED
"""

import os
import threading
import asyncio
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

# Print for debugging
print("=" * 50)
print(f"🤖 TOKEN Loaded: {'✅ Yes' if TOKEN else '❌ No'}")
print(f"👑 ADMIN_ID: {ADMIN_ID}")
print(f"📝 TOKEN length: {len(TOKEN) if TOKEN else 0}")
print("=" * 50)

# Temporary storage
user_data = {}
bookings = {}
user_active_booking = {}

# ============================================
# TEST ADMIN CONNECTION
# ============================================

async def test_admin_connection(bot):
    """Test if bot can send message to admin"""
    try:
        await bot.send_message(ADMIN_ID, "🤖 *Bot is online and ready!*\n\nI will send all booking details here.", parse_mode='Markdown')
        print(f"✅ Test message sent to admin {ADMIN_ID}")
        return True
    except Exception as e:
        print(f"❌ Cannot send message to admin {ADMIN_ID}: {e}")
        print(f"   Make sure admin has started the bot: https://t.me/{(await bot.get_me()).username}")
        return False

# ============================================
# SHOW MAIN MENU
# ============================================

async def show_main_menu(message, user_id=None):
    """Show main menu with 4 options"""
    
    has_booking = user_id and user_id in user_active_booking
    
    if has_booking:
        booking_id = user_active_booking[user_id].get("booking_id", "Unknown")
        keyboard = [
            [InlineKeyboardButton("📅 Book Now", callback_data="menu_book")],
            [InlineKeyboardButton("ℹ️ Service Info", callback_data="menu_info")],
            [InlineKeyboardButton("📞 Contact Us", callback_data="menu_contact")],
            [InlineKeyboardButton(f"❌ Cancel Booking", callback_data="menu_cancel_booking")]
        ]
        menu_text = f"""
🔥 *LUCKNOW GLEEDEN SERVICE* 🔥
👩 *Only for Female* 👩

✨ *Premium Entertainment Services* ✨

📋 *Your Active Booking ID:* `{booking_id}`

📌 *Quick Commands:*
• Type "book" or "hi" - New Booking
• Type "cancel" - Cancel Booking
• Type "info" - Service Info
• Type "contact" - Contact Us
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
👩 *Only for Female* 👩

✨ *Premium Entertainment Services* ✨

📌 *Quick Commands:*
• Type "book" or "hi" - New Booking
• Type "cancel" - Cancel Booking
• Type "info" - Service Info
• Type "contact" - Contact Us

🔒 *100% Privacy Guaranteed*
📍 *Service in Lucknow*
"""
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Send welcome message to user
    await show_main_menu(update.message, user_id)
    
    # Notify admin that a new user started the bot
    try:
        await context.bot.send_message(
            ADMIN_ID, 
            f"👤 *New User Started Bot*\n\nName: {user_name}\nID: `{user_id}`\nUsername: @{update.effective_user.username or 'N/A'}",
            parse_mode='Markdown'
        )
        print(f"✅ New user notification sent to admin")
    except Exception as e:
        print(f"❌ Failed to send new user notification: {e}")

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
ℹ️ *SERVICE INFORMATION* ℹ️

✨ *What We Offer:*

💆‍♂️ *Massage* - Day OR Night
🤝 *Casual Meet Up* - Day OR Night
☀️ *Day Service* - 1,2,4 Hours
🌙 *Night Package* - 1,2,4 Hours, Full Night

✅ *Features:*
• Verified Professionals
• 100% Privacy Guaranteed
• Only for Female

⏰ *24x7 Service Available*
"""
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    admin_msg = f"""
📞 *CONTACT REQUEST*

👤 Name: {user.first_name}
🆔 Username: @{user.username or 'N/A'}
🆔 ID: `{user.id}`
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    try:
        await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
        print(f"✅ Contact request sent to admin {ADMIN_ID}")
        await update.message.reply_text("✅ Request sent to admin! We will contact you shortly.", parse_mode='Markdown')
    except Exception as e:
        print(f"❌ Failed to send contact request: {e}")
        await update.message.reply_text(f"❌ Error sending request. Please try again later.\n\nError: {str(e)[:100]}", parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
ℹ️ *HOW TO USE* ℹ️

📅 *To Book:*
Simply type: "book", "बुक", "hi", "hello"

📋 *Other Keywords:*
• "info" - Service info
• "contact" - Contact us
• "cancel" - Cancel booking
• "menu" - Show main menu
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ============================================
# CANCEL BOOKING COMMAND
# ============================================

async def cancel_booking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel booking command handler"""
    user_id = update.effective_user.id
    
    print(f"Cancel booking requested by user {user_id}")
    
    if user_id in user_active_booking:
        booking_data = user_active_booking[user_id]
        booking_id = booking_data.get("booking_id", "Unknown")
        
        keyboard = [
            [InlineKeyboardButton("✅ Yes, Cancel", callback_data=f"confirm_yes_{booking_id}")],
            [InlineKeyboardButton("❌ No, Keep", callback_data="confirm_no")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ *Cancel Booking?* ⚠️\n\n"
            f"Your Booking ID: `{booking_id}`\n\n"
            f"Are you sure you want to cancel?\n\n"
            f"This action cannot be undone.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📅 Book Now", callback_data="menu_book")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ *No Active Booking Found!*\n\n"
            "You don't have any active booking to cancel.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# ============================================
# EASY TYPE HANDLER
# ============================================

async def easy_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    text = message.text.lower().strip()
    
    # If user is in booking flow
    if user_id in user_data:
        current_step = user_data[user_id].get("step")
        
        if text in ["cancel", "रद्द", "exit"]:
            if user_id in user_data:
                del user_data[user_id]
            await cancel_booking_command(update, context)
            return
        
        await handle_booking_flow(update, context)
        return
    
    # Easy keywords
    if text in ["book", "booking", "बुक", "hi", "hello", "hey", "hy", "hii"]:
        await book_command(update, context)
    elif text in ["info", "information", "जानकारी"]:
        await info_command(update, context)
    elif text in ["contact", "support", "संपर्क"]:
        await contact_command(update, context)
    elif text in ["help", "मदद"]:
        await help_command(update, context)
    elif text in ["cancel", "रद्द", "cancel booking"]:
        await cancel_booking_command(update, context)
    elif text in ["start", "menu", "मेनू"]:
        await show_main_menu(message, user_id)
    else:
        await message.reply_text(
            "📝 *I don't understand that.*\n\n"
            "📌 *Try typing:*\n"
            "• 'book' or 'hi' - New booking\n"
            "• 'cancel' - Cancel booking\n"
            "• 'info' - Service info\n"
            "• 'contact' - Contact us",
            parse_mode='Markdown'
        )

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
            f"✅ Age: *{text}*\n\n📍 *Please share your LOCATION (Area Name)*\n\nExample: Gomti Nagar, Lucknow",
            parse_mode='Markdown'
        )
    
    elif current_step == "location":
        user_data[user_id]["location"] = text
        user_data[user_id]["step"] = "contact_details"
        
        keyboard = [
            [InlineKeyboardButton("⏭️ Skip", callback_data="skip_contact")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_during_booking")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            f"✅ Location: *{text}*\n\n📞 *Share CONTACT DETAILS (Optional)*\n\nExample: 9876543210\n\nOr click SKIP",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif current_step == "contact_details":
        await complete_booking(user_id, message, text)

# ============================================
# CALLBACK QUERY HANDLER
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    print(f"Button clicked: {data} by user {user_id}")
    
    # ========== MAIN MENU ==========
    if data == "main_menu":
        await show_main_menu(query.message, user_id)
    
    elif data == "menu_book":
        await book_command(update, context)
    
    elif data == "menu_info":
        info_text = """
ℹ️ *SERVICE INFORMATION*

💆‍♂️ Massage - Day OR Night
🤝 Casual Meet Up - Day OR Night
☀️ Day Service - 1,2,4 Hours
🌙 Night Package - 1,2,4 Hours, Full Night

✅ 24x7 Available | Only for Female
"""
        await query.edit_message_text(info_text, parse_mode='Markdown')
    
    elif data == "menu_contact":
        user = query.from_user
        admin_msg = f"📞 Contact Request from {user.first_name} (@{user.username or 'N/A'}) ID: {user.id}"
        try:
            await context.bot.send_message(ADMIN_ID, admin_msg)
            print(f"✅ Contact request sent to admin")
            await query.edit_message_text("✅ Request sent to admin! We'll contact you shortly.", parse_mode='Markdown')
        except Exception as e:
            print(f"❌ Failed: {e}")
            await query.edit_message_text(f"❌ Error: {str(e)[:100]}", parse_mode='Markdown')
    
    # ========== CANCEL BOOKING ==========
    elif data == "menu_cancel_booking":
        if user_id in user_active_booking:
            booking_id = user_active_booking[user_id].get("booking_id", "Unknown")
            keyboard = [
                [InlineKeyboardButton("✅ Yes, Cancel", callback_data=f"confirm_yes_{booking_id}")],
                [InlineKeyboardButton("❌ No, Keep", callback_data="confirm_no")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"⚠️ *Cancel Booking?*\n\nBooking ID: `{booking_id}`\n\nAre you sure?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ No active booking found!", parse_mode='Markdown')
    
    elif data.startswith("confirm_yes_"):
        booking_id = data.replace("confirm_yes_", "")
        if user_id in user_active_booking:
            del user_active_booking[user_id]
            keyboard = [
                [InlineKeyboardButton("📅 New Booking", callback_data="menu_book")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"✅ *Booking Cancelled!*\n\nBooking ID: `{booking_id}` has been cancelled.\n\nStart a new booking?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ Booking not found!", parse_mode='Markdown')
    
    elif data == "confirm_no":
        if user_id in user_active_booking:
            booking_id = user_active_booking[user_id].get("booking_id", "Unknown")
            keyboard = [
                [InlineKeyboardButton("📅 New Booking", callback_data="menu_book")],
                [InlineKeyboardButton("❌ Cancel Booking", callback_data="menu_cancel_booking")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"✅ *Booking Kept!*\n\nYour Booking ID: `{booking_id}` is still active.\n\nWhat would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    elif data == "cancel_during_booking":
        if user_id in user_data:
            del user_data[user_id]
        await query.edit_message_text("❌ Booking cancelled!", parse_mode='Markdown')
        await show_main_menu(query.message, user_id)
    
    # ========== SERVICE SELECTION ==========
    elif data == "book_massage":
        user_data[user_id] = {"service": "Massage", "step": "day_night"}
        keyboard = [
            [InlineKeyboardButton("☀️ Day", callback_data="massage_day")],
            [InlineKeyboardButton("🌙 Night", callback_data="massage_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text("✅ *Massage*\n\nSelect Day OR Night:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
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
        await query.edit_message_text("✅ *Casual Meet Up*\n\nSelect Day OR Night:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
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
    
    # ========== DURATION SELECTION ==========
    elif data in ["dur_1", "dur_2", "dur_4", "dur_night"]:
        duration_map = {
            "dur_1": "1 Hour",
            "dur_2": "2 Hours", 
            "dur_4": "4 Hours",
            "dur_night": "Full Night"
        }
        user_data[user_id]["duration"] = duration_map[data]
        user_data[user_id]["step"] = "place"
        
        keyboard = [
            [InlineKeyboardButton("🏢 Public Place", callback_data="place_public")],
            [InlineKeyboardButton("🏨 Hotel", callback_data="place_hotel")],
            [InlineKeyboardButton("🏠 Your Home", callback_data="place_home")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        
        service = user_data[user_id].get("service", "Service")
        duration = duration_map[data]
        type_info = user_data[user_id].get("type", "")
        type_info = f" ({type_info})" if type_info else ""
        
        await query.edit_message_text(
            f"✅ *{service}{type_info}* | Duration: *{duration}*\n\n📍 Where do you want the service?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ========== PLACE SELECTION ==========
    elif data in ["place_public", "place_hotel", "place_home"]:
        place_map = {
            "place_public": "Public Place",
            "place_hotel": "Hotel",
            "place_home": "Your Home"
        }
        user_data[user_id]["place"] = place_map[data]
        user_data[user_id]["step"] = "status"
        
        keyboard = [
            [InlineKeyboardButton("👤 Single", callback_data="status_single")],
            [InlineKeyboardButton("👥 Couple", callback_data="status_couple")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            f"✅ Place: *{place_map[data]}*\n\n👥 Are you Single or Couple?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ========== STATUS SELECTION ==========
    elif data in ["status_single", "status_couple"]:
        status_map = {
            "status_single": "Single",
            "status_couple": "Couple"
        }
        user_data[user_id]["status"] = status_map[data]
        user_data[user_id]["step"] = "age"
        
        await query.edit_message_text(
            f"✅ Status: *{status_map[data]}*\n\n🎂 *Please enter your age:*\n\nExample: `25`",
            parse_mode='Markdown'
        )
    
    elif data == "skip_contact":
        await skip_contact(update, context)

# ============================================
# SKIP CONTACT HANDLER
# ============================================

async def skip_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in user_data or user_data[user_id].get("step") != "contact_details":
        await query.edit_message_text("Type 'book' to start a new booking")
        return
    
    await complete_booking(user_id, query.message, "Not provided")

# ============================================
# COMPLETE BOOKING
# ============================================

async def complete_booking(user_id, message, contact_details):
    """Complete booking and send details to admin"""
    
    print(f"📝 Completing booking for user {user_id}")
    
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
    
    booking_data = {
        "user_id": user_id,
        "user_name": user.first_name,
        "username": user.username,
        "service": service,
        "service_type": service_type,
        "duration": duration,
        "place": place,
        "status": status,
        "age": age,
        "location": location,
        "contact": contact,
        "booking_id": booking_id,
        "time": datetime.now().isoformat()
    }
    
    bookings[booking_id] = booking_data
    user_active_booking[user_id] = booking_data
    
    # Keyboard after booking
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

📝 *Summary:*
💼 Service: {service} {service_type}
⏱️ Duration: {duration}
📍 Place: {place}
👥 Status: {status}
🎂 Age: {age}
🏠 Location: {location}
📞 Contact: {contact}

*Our associate will contact you shortly!*
""", reply_markup=reply_markup, parse_mode='Markdown')
    
    # Send to admin - MULTIPLE ATTEMPTS
    admin_message = f"""
🔔 *NEW BOOKING* 🔔
━━━━━━━━━━━━━━━━

👤 *CUSTOMER:*
• Name: {user.first_name}
• Username: @{user.username or 'N/A'}
• ID: `{user_id}`
• Age: {age}
• Status: {status}
• Contact: {contact}

📋 *BOOKING:*
• Service: {service} {service_type}
• Duration: {duration}
• Place: {place}
• Location: {location}
• ID: `{booking_id}`

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Attempt 1: With Markdown
    try:
        await message.bot.send_message(ADMIN_ID, admin_message, parse_mode='Markdown')
        print(f"✅ Booking sent to admin {ADMIN_ID} (with markdown)")
    except Exception as e:
        print(f"❌ Attempt 1 failed: {e}")
        
        # Attempt 2: Without Markdown
        try:
            await message.bot.send_message(ADMIN_ID, admin_message.replace('*', '').replace('_', '').replace('`', ''))
            print(f"✅ Booking sent to admin {ADMIN_ID} (without markdown)")
        except Exception as e2:
            print(f"❌ Attempt 2 failed: {e2}")
            
            # Attempt 3: Plain text only
            try:
                plain_text = f"NEW BOOKING!\n\nCustomer: {user.first_name}\nID: {user_id}\nService: {service}\nBooking ID: {booking_id}"
                await message.bot.send_message(ADMIN_ID, plain_text)
                print(f"✅ Booking sent to admin {ADMIN_ID} (plain text)")
            except Exception as e3:
                print(f"❌ All attempts failed! Admin ID: {ADMIN_ID}")
                print(f"   Make sure admin has started the bot at: https://t.me/{(await message.bot.get_me()).username}")
    
    # Clear user data
    if user_id in user_data:
        del user_data[user_id]

# ============================================
# MAIN FUNCTION
# ============================================

async def async_main():
    """Async main function"""
    print("=" * 50)
    print("🚀 LUCKNOW GLEEDEN BOT STARTING...")
    print(f"🤖 TOKEN: {'✅ Loaded' if TOKEN else '❌ Missing'}")
    print(f"👑 ADMIN_ID: {ADMIN_ID}")
    print("=" * 50)
    
    # Create bot application
    app = Application.builder().token(TOKEN).build()
    
    # Initialize bot and test admin connection
    await app.initialize()
    await app.start()
    
    # Test admin connection
    bot_info = await app.bot.get_me()
    print(f"🤖 Bot Name: @{bot_info.username}")
    
    try:
        await app.bot.send_message(ADMIN_ID, f"🤖 *Bot is online!*\n\nBot Name: @{bot_info.username}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", parse_mode='Markdown')
        print(f"✅ Test message sent to admin {ADMIN_ID}")
        print(f"   Admin will receive all booking notifications here.")
    except Exception as e:
        print(f"❌ CANNOT SEND MESSAGE TO ADMIN {ADMIN_ID}")
        print(f"   Error: {e}")
        print(f"   Please make sure:")
        print(f"   1. ADMIN_ID is correct: {ADMIN_ID}")
        print(f"   2. Admin has started the bot: https://t.me/{bot_info.username}")
        print(f"   3. Admin sent /start to the bot")
    
    await app.stop()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel_booking_command))
    
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, easy_type_handler))
    
    print("✅ Bot started! Check admin messages above.")
    print("=" * 50)
    
    # Start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep running
    while True:
        await asyncio.sleep(1)

def main():
    # Start Flask health check server
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Run async main
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
