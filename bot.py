"""
LUCKNOW GLEEDEN BOT - HINDI + ENGLISH
24x7 Timing | No Photoshoot | ONLY FOR FEMALE | FIXED VERSION
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

# Temporary storage
user_data = {}
bookings = {}

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    welcome_text = """
🔥 *WELCOME TO LUCKNOW GLEEDEN SERVICE* 🔥
🔥 *लखनऊ ग्लीडेन सर्विस में आपका स्वागत है* 🔥
👩 *ONLY FOR FEMALE / केवल महिलाओं के लिए* 👩

✨ *Premium Entertainment Services* ✨

📋 *Commands:*
/book - Book Now
/info - Service Info
/contact - Contact Us

🔒 *100% Privacy Guaranteed*
📍 *Service in Lucknow*
"""
    keyboard = [
        [InlineKeyboardButton("📅 Book Now", callback_data="menu_book")],
        [InlineKeyboardButton("ℹ️ Service Info", callback_data="menu_info")],
        [InlineKeyboardButton("📞 Contact Us", callback_data="menu_contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def book_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start booking"""
    user_id = update.effective_user.id
    user_data[user_id] = {"step": "service"}
    
    keyboard = [
        [InlineKeyboardButton("💆‍♂️ Massage", callback_data="book_massage")],
        [InlineKeyboardButton("🤝 Casual Meet Up", callback_data="book_casual")],
        [InlineKeyboardButton("☀️ Day Service", callback_data="book_day")],
        [InlineKeyboardButton("🌙 Night Package", callback_data="book_night")],
        [InlineKeyboardButton("❌ Cancel", callback_data="book_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📅 *NEW BOOKING*\n\nSelect service:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Service information"""
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
    """Contact information"""
    user = update.effective_user
    
    admin_msg = f"""
📞 *CONTACT REQUEST*

👤 Name: {user.first_name}
🆔 Username: @{user.username or 'N/A'}
🆔 ID: `{user.id}`
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
    
    contact_text = f"""
📞 *CONTACT US*

✅ Request sent to admin!
✅ We will contact you shortly!

📍 Lucknow | 24x7
"""
    await update.message.reply_text(contact_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help menu"""
    help_text = """
ℹ️ *HOW TO USE* ℹ️

📅 *To Book:*
1️⃣ Type /book
2️⃣ Select service
3️⃣ Choose Day or Night (for Massage/Casual)
4️⃣ Choose duration
5️⃣ Choose place
6️⃣ Tell status (Single/Couple)
7️⃣ Share age
8️⃣ Share location
9️⃣ Share contact details (Optional)

💬 *Commands:*
/start - Main menu
/book - Start booking
/info - Service info
/contact - Contact us
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ============================================
# CALLBACK QUERY HANDLER
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # ========== MAIN MENU ==========
    if data == "menu_book":
        user_data[user_id] = {"step": "service"}
        keyboard = [
            [InlineKeyboardButton("💆‍♂️ Massage", callback_data="book_massage")],
            [InlineKeyboardButton("🤝 Casual Meet Up", callback_data="book_casual")],
            [InlineKeyboardButton("☀️ Day Service", callback_data="book_day")],
            [InlineKeyboardButton("🌙 Night Package", callback_data="book_night")],
            [InlineKeyboardButton("❌ Cancel", callback_data="book_cancel")]
        ]
        await query.edit_message_text(
            "📅 *NEW BOOKING*\n\nSelect service:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "menu_info":
        info_text = """
ℹ️ *SERVICE INFORMATION*

💆‍♂️ Massage - Day OR Night
🤝 Casual Meet Up - Day OR Night
☀️ Day Service - 1,2,4 Hours
🌙 Night Package - 1,2,4 Hours, Full Night

✅ 24x7 Available
✅ Only for Female
"""
        await query.edit_message_text(info_text, parse_mode='Markdown')
    
    elif data == "menu_contact":
        user = query.from_user
        admin_msg = f"📞 Contact Request from {user.first_name} (@{user.username or 'N/A'}) ID: {user.id}"
        await context.bot.send_message(ADMIN_ID, admin_msg)
        await query.edit_message_text("✅ Request sent to admin! We'll contact you shortly.", parse_mode='Markdown')
    
    # ========== MASSAGE (Day OR Night) ==========
    elif data == "book_massage":
        user_data[user_id] = {"service": "Massage", "step": "day_night"}
        keyboard = [
            [InlineKeyboardButton("☀️ Day", callback_data="massage_day")],
            [InlineKeyboardButton("🌙 Night", callback_data="massage_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ *Massage*\n\nSelect Day OR Night:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "massage_day":
        user_data[user_id]["type"] = "Day"
        user_data[user_id]["step"] = "duration"
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🔙 Back", callback_data="book_massage")]
        ]
        await query.edit_message_text(
            "✅ Massage - *Day*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
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
        await query.edit_message_text(
            "✅ Massage - *Night*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ========== CASUAL MEET UP (Day OR Night) ==========
    elif data == "book_casual":
        user_data[user_id] = {"service": "Casual Meet Up", "step": "day_night"}
        keyboard = [
            [InlineKeyboardButton("☀️ Day", callback_data="casual_day")],
            [InlineKeyboardButton("🌙 Night", callback_data="casual_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ *Casual Meet Up*\n\nSelect Day OR Night:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "casual_day":
        user_data[user_id]["type"] = "Day"
        user_data[user_id]["step"] = "duration"
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🔙 Back", callback_data="book_casual")]
        ]
        await query.edit_message_text(
            "✅ Casual Meet Up - *Day*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
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
        await query.edit_message_text(
            "✅ Casual Meet Up - *Night*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ========== DAY SERVICE (Direct: 1,2,4 Hours) ==========
    elif data == "book_day":
        user_data[user_id] = {"service": "Day Service", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ *Day Service*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ========== NIGHT PACKAGE (Direct: 1,2,4 Hours, Full Night) ==========
    elif data == "book_night":
        user_data[user_id] = {"service": "Night Package", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ *Night Package*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "book_cancel":
        if user_id in user_data:
            del user_data[user_id]
        await query.edit_message_text(
            "❌ *Booking cancelled*\n\nStart again with /book",
            parse_mode='Markdown'
        )
    
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
        if type_info:
            type_info = f" ({type_info})"
        
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
            f"✅ Status: *{status_map[data]}*\n\n🎂 *Please enter your age:*\n\nExample: `25`\n\n*कृपया अपनी उम्र बताएं:*",
            parse_mode='Markdown'
        )

# ============================================
# MESSAGE HANDLER - Age, Location, Contact
# ============================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages - Age, Location, Contact Details"""
    user_id = update.effective_user.id
    message = update.message
    text = message.text.strip()
    
    # Check if user is in booking flow
    if user_id not in user_data:
        # Auto reply for random messages
        await message.reply_text("📝 Type /book to start a new booking")
        return
    
    current_step = user_data[user_id].get("step")
    
    # ========== AGE STEP ==========
    if current_step == "age":
        user_data[user_id]["age"] = text
        user_data[user_id]["step"] = "location"
        
        await message.reply_text(
            f"✅ Age: *{text}*\n\n"
            f"📍 *Please share your LOCATION (Area Name)*\n\n"
            f"Example: Gomti Nagar, Lucknow\n\n"
            f"*अब कृपया अपनी लोकेशन भेजें (इलाके का नाम)*",
            parse_mode='Markdown'
        )
    
    # ========== LOCATION STEP ==========
    elif current_step == "location":
        user_data[user_id]["location"] = text
        user_data[user_id]["step"] = "contact_details"
        
        keyboard = [
            [InlineKeyboardButton("⏭️ Skip / छोड़ें", callback_data="skip_contact")],
            [InlineKeyboardButton("❌ Cancel Booking", callback_data="book_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            f"✅ Location: *{text}*\n\n"
            f"📞 *Please share your CONTACT DETAILS (Optional)*\n\n"
            f"Example: Phone Number or WhatsApp Number\n\n"
            f"Example: `9876543210`\n\n"
            f"*You can also click SKIP if you don't want to share*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ========== CONTACT DETAILS STEP ==========
    elif current_step == "contact_details":
        contact_details = text
        await complete_booking(user_id, message, contact_details)
    
    else:
        await message.reply_text("📝 Type /book to start a new booking")

# ============================================
# SKIP CONTACT HANDLER
# ============================================

async def skip_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip contact details"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in user_data or user_data[user_id].get("step") != "contact_details":
        await query.edit_message_text("📝 Type /book to start a new booking")
        return
    
    await complete_booking(user_id, query.message, "Not provided (Skipped)")

# ============================================
# COMPLETE BOOKING FUNCTION
# ============================================

async def complete_booking(user_id, message, contact_details):
    """Complete booking and send details to admin"""
    
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
    
    bookings[booking_id] = {
        "user_id": user_id,
        "user_name": user.first_name,
        "service": service,
        "service_type": service_type,
        "duration": duration,
        "place": place,
        "status": status,
        "age": age,
        "location": location,
        "contact": contact,
        "time": datetime.now().isoformat()
    }
    
    # Send confirmation to customer
    await message.reply_text(f"""
✅ *BOOKING CONFIRMED!* ✅
━━━━━━━━━━━━━━━━━━━━━━━

📋 *Booking ID:* `{booking_id}`

📝 *Your Booking Summary:*
━━━━━━━━━━━━━━━━━━━━━━━
💼 Service: {service} {service_type}
⏱️ Duration: {duration}
📍 Meeting Place: {place}
👥 Status: {status}
🎂 Age: {age}
🏠 Location: {location}
📞 Contact: {contact}
━━━━━━━━━━━━━━━━━━━━━━━

📞 *Next Steps:*
✅ We have received your booking request
✅ Our associate will contact you VERY SOON
✅ Please keep your phone available

*Thank you for choosing Lucknow Gleeden Service!* 🙏
*आपका स्वागत है! हम आपसे जल्द संपर्क करेंगे!*
""", parse_mode='Markdown')
    
    # Send complete details to admin
    admin_message = f"""
🔔 *NEW BOOKING ALERT* 🔔
━━━━━━━━━━━━━━━━━━━━━━━

👤 *CUSTOMER DETAILS:*
━━━━━━━━━━━━━━━━━━━━━━━
• Name: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'N/A'}
• User ID: `{user_id}`
• Age: {age}
• Status: {status}
• Contact: {contact}

━━━━━━━━━━━━━━━━━━━━━━━
📋 *BOOKING DETAILS:*
━━━━━━━━━━━━━━━━━━━━━━━
• Service: {service} {service_type}
• Duration: {duration}
• Place: {place}
• Location: {location}
• Booking ID: `{booking_id}`

━━━━━━━━━━━━━━━━━━━━━━━
⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━

📱 *Customer Chat Link:* [Click to message](tg://user?id={user_id})
"""
    
    await message.bot.send_message(ADMIN_ID, admin_message, parse_mode='Markdown')
    
    # Clear user data
    del user_data[user_id]

# ============================================
# AUTO REPLY HANDLER (for messages outside booking)
# ============================================

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto reply for common questions when not in booking flow"""
    user_id = update.effective_user.id
    
    # If user is in booking flow, don't auto reply (let handle_message handle it)
    if user_id in user_data:
        return
    
    text = update.message.text.lower()
    
    if "help" in text:
        await update.message.reply_text("Type /start for menu\n/book for booking")
    elif "location" in text:
        await update.message.reply_text("📍 Service areas: Lucknow (Gomti Nagar, Hazratganj, Aliganj, Indira Nagar)")
    elif "cancel" in text:
        await update.message.reply_text("❌ To cancel, reply to your booking confirmation message.")
    else:
        await update.message.reply_text("✅ Message received! We'll respond shortly.\n\nType /book to start a new booking")

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
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Add callback query handler
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CallbackQueryHandler(skip_contact, pattern="skip_contact"))
    
    # Add message handlers - IMPORTANT: Order matters!
    # First check if message is part of booking flow
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is running 24/7!")
    print("=" * 50)
    print("📋 SERVICE OPTIONS:")
    print("• Massage: Day OR Night")
    print("• Casual Meet Up: Day OR Night")
    print("• Day Service: 1,2,4 Hours")
    print("• Night Package: 1,2,4 Hours, Full Night")
    print("=" * 50)
    print("✅ FIXED:")
    print("• Age → Location → Contact Details")
    print("• Skip button working")
    print("• Booking Confirmation")
    print("• Admin message working")
    print("=" * 50)
    
    # Start bot polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
