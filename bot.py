"""
LUCKNOW GLEEDEN BOT - HINDI + ENGLISH
24x7 Timing | No Photoshoot | BOOKING DETAILS FIXED
"""

import os
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

# Temporary storage
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
            [InlineKeyboardButton(f"❌ Cancel Booking", callback_data="menu_cancel_booking")]
        ]
        menu_text = f"""
🔥 *LUCKNOW GLEEDEN SERVICE* 🔥
👩 *Only for Female* 👩

📋 *Your Active Booking ID:* `{booking_id}`

📌 Type "book" or "hi" - New Booking
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

📌 Type "book" or "hi" to start booking
"""
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await show_main_menu(update.message, user_id)

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

💆‍♂️ Massage - Day OR Night
🤝 Casual Meet Up - Day OR Night
☀️ Day Service - 1,2,4 Hours
🌙 Night Package - 1,2,4 Hours, Full Night

✅ 24x7 Available | Only for Female
"""
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    admin_msg = f"📞 Contact Request from {user.first_name} (@{user.username or 'N/A'}) ID: {user.id}"
    try:
        await context.bot.send_message(ADMIN_ID, admin_msg)
        print(f"✅ Contact request sent")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    await update.message.reply_text("✅ Request sent to admin! We will contact you shortly.", parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
ℹ️ *HOW TO USE* ℹ️

Type "book" or "hi" to start booking
Type "cancel" to cancel booking
Type "info" for service info
Type "contact" to contact us
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ============================================
# CANCEL BOOKING COMMAND
# ============================================

async def cancel_booking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
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
            f"⚠️ *Cancel Booking?*\n\nBooking ID: `{booking_id}`\n\nAre you sure?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📅 Book Now", callback_data="menu_book")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ No active booking found!", reply_markup=reply_markup, parse_mode='Markdown')

# ============================================
# EASY TYPE HANDLER
# ============================================

async def easy_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    text = message.text.lower().strip()
    
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
    elif text in ["help", "मदद"]:
        await help_command(update, context)
    elif text in ["cancel", "रद्द", "cancel booking"]:
        await cancel_booking_command(update, context)
    elif text in ["start", "menu", "मेनू"]:
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
            f"✅ Age: *{text}*\n\n📍 *Share your LOCATION (Area Name)*\n\nExample: Gomti Nagar, Lucknow",
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
    
    if data == "main_menu":
        await show_main_menu(query.message, user_id)
    
    elif data == "menu_book":
        await book_command(update, context)
    
    elif data == "menu_info":
        await query.edit_message_text("ℹ️ *SERVICE INFO*\n\nMassage - Day/Night\nCasual Meet Up - Day/Night\nDay Service - 1,2,4 Hours\nNight Package - 1,2,4 Hours, Full Night", parse_mode='Markdown')
    
    elif data == "menu_contact":
        user = query.from_user
        await context.bot.send_message(ADMIN_ID, f"📞 Contact from {user.first_name} (@{user.username or 'N/A'})")
        await query.edit_message_text("✅ Request sent to admin!", parse_mode='Markdown')
    
    # ========== CANCEL BOOKING ==========
    elif data == "menu_cancel_booking":
        if user_id in user_active_booking:
            booking_id = user_active_booking[user_id].get("booking_id", "Unknown")
            keyboard = [
                [InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{booking_id}")],
                [InlineKeyboardButton("❌ No", callback_data="confirm_no")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
            ]
            await query.edit_message_text(f"⚠️ Cancel Booking?\n\nID: `{booking_id}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ No active booking!", parse_mode='Markdown')
    
    elif data.startswith("confirm_yes_"):
        booking_id = data.replace("confirm_yes_", "")
        if user_id in user_active_booking:
            del user_active_booking[user_id]
            keyboard = [[InlineKeyboardButton("📅 New Booking", callback_data="menu_book")]]
            await query.edit_message_text(f"✅ Booking `{booking_id}` cancelled!", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "confirm_no":
        if user_id in user_active_booking:
            booking_id = user_active_booking[user_id].get("booking_id", "Unknown")
            await query.edit_message_text(f"✅ Booking `{booking_id}` kept active!", parse_mode='Markdown')
    
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
            f"✅ *{service}{type_info}* | Duration: *{duration}*\n\n📍 Where?",
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
            f"✅ Place: *{place_map[data]}*\n\n👥 Single or Couple?",
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
        await query.edit_message_text(f"✅ Status: *{status_map[data]}*\n\n🎂 Enter your age:", parse_mode='Markdown')
    
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
        await query.edit_message_text("Type 'book' to start")
        return
    
    await complete_booking(user_id, query.message, "Not provided")

# ============================================
# COMPLETE BOOKING - FIXED VERSION
# ============================================

async def complete_booking(user_id, message, contact_details):
    """Complete booking and send details to admin"""
    
    print(f"📝 Completing booking for user {user_id}")
    
    try:
        # Get all booking details
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
        print(f"👤 User: {user.first_name}")
        print(f"💼 Service: {service} {service_type}")
        
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

💼 Service: {service} {service_type}
⏱️ Duration: {duration}
📍 Place: {place}
👥 Status: {status}
🎂 Age: {age}
🏠 Location: {location}
📞 Contact: {contact}

*Our associate will contact you shortly!*
""", reply_markup=reply_markup, parse_mode='Markdown')
        
        # ========== SEND BOOKING DETAILS TO ADMIN ==========
        
        # Simple plain text message for admin
        admin_text = f"""
🔔 NEW BOOKING 🔔

━━━━━━━━━━━━━━━━
👤 CUSTOMER DETAILS:
━━━━━━━━━━━━━━━━
Name: {user.first_name}
Username: @{user.username or 'N/A'}
User ID: {user_id}
Age: {age}
Status: {status}
Contact: {contact}

━━━━━━━━━━━━━━━━
📋 BOOKING DETAILS:
━━━━━━━━━━━━━━━━
Service: {service} {service_type}
Duration: {duration}
Place: {place}
Location: {location}
Booking ID: {booking_id}

━━━━━━━━━━━━━━━━
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Try to send to admin
        try:
            await message.bot.send_message(ADMIN_ID, admin_text)
            print(f"✅ Booking details sent to admin {ADMIN_ID}")
        except Exception as e:
            print(f"❌ Failed to send to admin: {e}")
            
            # Try even simpler message
            try:
                simple_text = f"NEW BOOKING!\n\nCustomer: {user.first_name}\nService: {service}\nBooking ID: {booking_id}\nLocation: {location}"
                await message.bot.send_message(ADMIN_ID, simple_text)
                print(f"✅ Simple booking message sent")
            except Exception as e2:
                print(f"❌ Both attempts failed: {e2}")
        
        # Clear user data
        if user_id in user_data:
            del user_data[user_id]
            
    except Exception as e:
        print(f"❌ Error in complete_booking: {e}")
        await message.reply_text(f"❌ Error processing booking. Please try again.\nError: {str(e)[:100]}")

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("=" * 50)
    print("🚀 LUCKNOW GLEEDEN BOT STARTING...")
    print("=" * 50)
    
    # Start Flask health check server
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Flask server started")
    
    # Create bot application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel_booking_command))
    
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, easy_type_handler))
    
    print("✅ Bot started!")
    print("=" * 50)
    print("📌 Bot is ready! Send 'hi' to start booking")
    print("=" * 50)
    
    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
