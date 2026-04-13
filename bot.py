"""
LUCKNOW CALLBOY BOT - HINDI + ENGLISH
24x7 Timing | No Photoshoot | SIMPLIFIED VERSION
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
    """Welcome message with working buttons"""
    welcome_text = """
🔥 *WELCOME TO LUCKNOW CALLBOY SERVICE* 🔥
🔥 *लखनऊ कॉलबॉय सर्विस में आपका स्वागत है* 🔥

✨ *Premium Entertainment Services* ✨

📋 *Commands / कमांड्स:*
/book - Book Now / अभी बुक करें
/info - Service Info / सेवा की जानकारी
/contact - Contact Us / संपर्क करें

🔒 *100% Privacy Guaranteed*
📍 *Service in Lucknow*
"""
    keyboard = [
        [InlineKeyboardButton("📅 Book Now / अभी बुक करें", callback_data="menu_book")],
        [InlineKeyboardButton("ℹ️ Service Info / सेवा की जानकारी", callback_data="menu_info")],
        [InlineKeyboardButton("📞 Contact Us / संपर्क करें", callback_data="menu_contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def book_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start booking - Shows service menu"""
    user_id = update.effective_user.id
    user_data[user_id] = {"step": "service"}
    
    keyboard = [
        [InlineKeyboardButton("💆‍♂️ Massage / मालिश", callback_data="book_massage")],
        [InlineKeyboardButton("🤝 Casual Meet Up", callback_data="book_casual")],
        [InlineKeyboardButton("☀️ Day Service / डे सर्विस", callback_data="book_day")],
        [InlineKeyboardButton("🌙 Night Package / नाइट पैकेज", callback_data="book_night")],
        [InlineKeyboardButton("❌ Cancel / रद्द करें", callback_data="book_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📅 *NEW BOOKING / नई बुकिंग*\n\nSelect service / सेवा चुनें:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Service information"""
    info_text = """
ℹ️ *SERVICE INFORMATION / सेवा की जानकारी* ℹ️

✨ *What We Offer / हम क्या प्रदान करते हैं:*
• Professional Massage / प्रोफेशनल मालिश
• Casual Meet Up / कैजुअल मीट अप
• Day Service / डे सर्विस
• Night Package / नाइट पैकेज

✅ *Features:*
• Verified Professionals
• 100% Privacy Guaranteed
• Safe & Discreet Service

⏰ *24x7 Service Available*
"""
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contact information - Sends user details to admin"""
    user = update.effective_user
    
    # User ki details admin ko bhejein
    admin_msg = f"""
📞 *CONTACT REQUEST* 📞

👤 *User Details:*
• Name: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'N/A'}
• User ID: `{user.id}`
• Language: {user.language_code or 'Unknown'}

⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📱 *Chat Link:* [Click to message](tg://user?id={user.id})
"""
    await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
    
    # User ko reply
    contact_text = f"""
📞 *CONTACT US / संपर्क करें* 📞

✅ *Your request has been forwarded to admin!*
✅ *आपका अनुरोध एडमिन को भेज दिया गया है!*

📝 *Details sent to admin:*
• Name: {user.first_name}
• Username: @{user.username or 'N/A'}
• User ID: `{user.id}`

⏰ *We will contact you shortly!*
⏰ *हम आपसे जल्द संपर्क करेंगे!*

📌 *Service Hours:* 🟢 24x7
📍 *Location:* Lucknow
"""
    await update.message.reply_text(contact_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help menu"""
    help_text = """
ℹ️ *HOW TO USE / उपयोग कैसे करें* ℹ️

📅 *To Book:*
1️⃣ Type /book
2️⃣ Select service
3️⃣ Choose duration
4️⃣ Choose meeting place
5️⃣ Tell status (Single/Couple)
6️⃣ Share age
7️⃣ Share location

💬 *Commands:*
/start - Main menu
/book - Start booking
/info - Service info
/contact - Contact us

🔒 *100% Privacy Guaranteed*
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
    
    # ========== MAIN MENU BUTTONS ==========
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
ℹ️ *SERVICE INFORMATION* ℹ️

✨ *What We Offer:*
• Professional Massage
• Casual Meet Up
• Day Service
• Night Package

✅ *Verified Professionals*
✅ *100% Privacy Guaranteed*
⏰ *24x7 Available*
"""
        await query.edit_message_text(info_text, parse_mode='Markdown')
    
    elif data == "menu_contact":
        # Contact button se bhi admin ko details jaye
        user = query.from_user
        admin_msg = f"""
📞 *CONTACT REQUEST (from menu)* 📞

👤 *User Details:*
• Name: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'N/A'}
• User ID: `{user.id}`

⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
        
        contact_text = f"""
📞 *CONTACT US*

✅ *Request sent to admin!*
✅ *एडमिन को रिक्वेस्ट भेज दी गई!*

📝 *Your ID:* `{user.id}`

⏰ *We'll contact you shortly!*
📍 *Lucknow | 24x7*
"""
        await query.edit_message_text(contact_text, parse_mode='Markdown')
    
    # ========== SERVICE SELECTION ==========
    elif data == "book_massage":
        user_data[user_id] = {"service": "Massage", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ Selected: *Massage*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "book_casual":
        user_data[user_id] = {"service": "Casual Meet Up", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ Selected: *Casual Meet Up*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "book_day":
        user_data[user_id] = {"service": "Day Service", "step": "duration"}
        # Day Service mein FULL NIGHT nahi hoga
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ Selected: *Day Service*\n\nSelect duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
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
            "✅ Selected: *Night Package*\n\nSelect duration:",
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
        await query.edit_message_text(
            f"✅ Duration: *{duration_map[data]}*\n\n📍 *Where do you want the service?*\n*सेवा कहाँ चाहिए?*",
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
            f"✅ Place: *{place_map[data]}*\n\n👥 *Are you Single or Couple?*\n*आप सिंगल हैं या कपल?*",
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
            f"✅ Status: *{status_map[data]}*\n\n🎂 *Please enter your age*\n*कृपया अपनी उम्र बताएं*\n\nExample / उदाहरण: `25`",
            parse_mode='Markdown'
        )

# ============================================
# AGE HANDLER
# ============================================

async def handle_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle age input"""
    user_id = update.effective_user.id
    message = update.message
    
    if user_id not in user_data or user_data[user_id].get("step") != "age":
        await message.reply_text(
            "📝 Type /book to start a new booking"
        )
        return
    
    age = message.text.strip()
    user_data[user_id]["age"] = age
    user_data[user_id]["step"] = "location"
    
    await message.reply_text(
        f"✅ Age: *{age}*\n\n"
        f"📍 *Now please share your LIVE LOCATION*\n\n"
        f"Tap attachment (📎) → Location → Send Live Location\n\n"
        f"*अब कृपया अपनी लाइव लोकेशन भेजें*",
        parse_mode='Markdown'
    )

# ============================================
# LOCATION HANDLER
# ============================================

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's live location and send complete details to admin"""
    user_id = update.effective_user.id
    message = update.message
    
    if user_id not in user_data or user_data[user_id].get("step") != "location":
        await message.reply_text(
            "📍 Type /book to start a new booking"
        )
        return
    
    lat = message.location.latitude
    lon = message.location.longitude
    
    # Get all booking details
    service = user_data[user_id].get("service", "Unknown")
    duration = user_data[user_id].get("duration", "Unknown")
    place = user_data[user_id].get("place", "Unknown")
    status = user_data[user_id].get("status", "Unknown")
    age = user_data[user_id].get("age", "Unknown")
    
    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
    user = message.from_user
    
    bookings[booking_id] = {
        "user_id": user_id,
        "user_name": user.first_name,
        "service": service,
        "duration": duration,
        "place": place,
        "status": status,
        "age": age,
        "time": datetime.now().isoformat()
    }
    
    # Send confirmation to customer
    await message.reply_text(f"""
✅ *BOOKING CONFIRMED!* ✅

📋 *Booking ID:* `{booking_id}`

📝 *Your Details:*
💼 Service: {service}
⏱️ Duration: {duration}
📍 Place: {place}
👥 Status: {status}
🎂 Age: {age}

📞 *Next Steps:*
Our associate will contact you shortly.

*Thank you for choosing our service!*
""", parse_mode='Markdown')
    
    # Send complete details to admin
    maps_link = f"https://maps.google.com/?q={lat},{lon}"
    
    admin_message = f"""
🔔 *NEW BOOKING ALERT* 🔔

━━━━━━━━━━━━━━━━━━
👤 *CUSTOMER DETAILS:*
━━━━━━━━━━━━━━━━━━

• Name: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'N/A'}
• User ID: `{user_id}`
• Age: {age}
• Status: {status}

━━━━━━━━━━━━━━━━━━
📋 *BOOKING DETAILS:*
━━━━━━━━━━━━━━━━━━

• Service: {service}
• Duration: {duration}
• Place: {place}
• Booking ID: `{booking_id}`

━━━━━━━━━━━━━━━━━━
📍 *LOCATION:*
━━━━━━━━━━━━━━━━━━

• Maps Link: {maps_link}

━━━━━━━━━━━━━━━━━━
⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    await context.bot.send_message(ADMIN_ID, admin_message, parse_mode='Markdown')
    
    # Send location separately for easy access
    await context.bot.send_location(ADMIN_ID, latitude=lat, longitude=lon)
    
    # Clear user data
    del user_data[user_id]

# ============================================
# AUTO REPLY HANDLER
# ============================================

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto reply for common questions"""
    text = update.message.text.lower()
    
    if "help" in text or "मदद" in text:
        await update.message.reply_text(
            "Type /start for menu\n/book for booking"
        )
    elif "location" in text or "लोकेशन" in text:
        await update.message.reply_text(
            "📍 Service areas: Lucknow (Gomti Nagar, Hazratganj, Aliganj, Indira Nagar)"
        )
    elif "cancel" in text or "रद्द" in text:
        await update.message.reply_text(
            "❌ To cancel, reply to your booking confirmation message."
        )
    else:
        await context.bot.send_message(ADMIN_ID, f"📩 *New Message*\n👤 @{update.effective_user.username or update.effective_user.first_name}\n💬 {update.message.text}", parse_mode='Markdown')
        await update.message.reply_text(
            "✅ Message received! We'll respond shortly."
        )

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("=" * 50)
    print("🚀 LUCKNOW CALLBOY BOT STARTING...")
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
    
    # Add message handlers
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_age))
    
    print("✅ Bot is running 24/7!")
    print("✅ Day Service - No Full Night option!")
    print("✅ Day option removed!")
    print("✅ Single/Couple option added!")
    print("✅ Age option added!")
    print("✅ Contact Us sends user details to admin!")
    print("=" * 50)
    
    # Start bot polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
