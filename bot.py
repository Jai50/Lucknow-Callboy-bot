"""
LUCKNOW CALLBOY BOT - HINDI + ENGLISH
24x7 Timing | No Photoshoot | FIXED BUTTONS
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
✨ *प्रीमियम मनोरंजन सेवाएं* ✨

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
        [InlineKeyboardButton("🍽️ Dinner Date / डिनर डेट", callback_data="book_dinner")],
        [InlineKeyboardButton("🎉 Party Companion / पार्टी कम्पेनियन", callback_data="book_party")],
        [InlineKeyboardButton("🌙 Night Package / नाइट पैकेज", callback_data="book_night")],
        [InlineKeyboardButton("❌ Cancel / रद्द करें", callback_data="book_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Using edit_message_text if it's a callback, otherwise send new message
    if update.callback_query:
        await update.callback_query.message.edit_text(
            "📅 *NEW BOOKING / नई बुकिंग*\n\nSelect service / सेवा चुनें:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
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
• Dinner Date Companion / डिनर डेट कम्पेनियन
• Party/Event Companion / पार्टी/इवेंट कम्पेनियन
• Night Out Package / नाइट आउट पैकेज

✅ *Features / विशेषताएं:*
• Verified Professionals / वेरिफाइड प्रोफेशनल्स
• 100% Privacy Guaranteed / 100% प्राइवेसी गारंटी
• Safe & Discreet Service / सुरक्षित और गोपनीय सेवा

⏰ *24x7 Service Available*
"""
    if update.callback_query:
        await update.callback_query.message.edit_text(info_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(info_text, parse_mode='Markdown')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contact information"""
    contact_text = """
📞 *CONTACT US / संपर्क करें* 📞

💬 *Reply here / यहाँ रिप्लाई करें* - We respond quickly
⏰ *Service Hours:* 🟢 *24x7 (Always Open)*
📍 *Location:* Lucknow / लखनऊ

🔒 *Privacy Guaranteed*

📝 *How to Book:*
1️⃣ Type /book or click Book Now
2️⃣ Select service
3️⃣ Choose duration
4️⃣ Share location

*हम 24 घंटे आपकी सेवा में हैं!*
"""
    if update.callback_query:
        await update.callback_query.message.edit_text(contact_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(contact_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help menu"""
    help_text = """
ℹ️ *HOW TO USE / उपयोग कैसे करें* ℹ️

📅 *To Book:*
1️⃣ Type /book or click Book Now
2️⃣ Select service
3️⃣ Choose duration
4️⃣ Share your live location
5️⃣ Booking confirmed!

💬 *Commands:*
/start - Main menu
/book - Start booking
/info - Service info
/contact - Contact us
/help - This menu

🔒 *100% Privacy Guaranteed*
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ============================================
# CALLBACK QUERY HANDLER - FIXED
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks - FIXED VERSION"""
    query = update.callback_query
    await query.answer()  # Always answer callback query first
    
    user_id = query.from_user.id
    data = query.data
    
    # ========== MAIN MENU BUTTONS ==========
    if data == "menu_book":
        user_data[user_id] = {"step": "service"}
        keyboard = [
            [InlineKeyboardButton("💆‍♂️ Massage / मालिश", callback_data="book_massage")],
            [InlineKeyboardButton("🍽️ Dinner Date / डिनर डेट", callback_data="book_dinner")],
            [InlineKeyboardButton("🎉 Party Companion / पार्टी कम्पेनियन", callback_data="book_party")],
            [InlineKeyboardButton("🌙 Night Package / नाइट पैकेज", callback_data="book_night")],
            [InlineKeyboardButton("❌ Cancel / रद्द करें", callback_data="book_cancel")]
        ]
        await query.edit_message_text(
            "📅 *NEW BOOKING / नई बुकिंग*\n\nSelect service / सेवा चुनें:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "menu_info":
        info_text = """
ℹ️ *SERVICE INFORMATION / सेवा की जानकारी* ℹ️

✨ *What We Offer:*
• Professional Massage / प्रोफेशनल मालिश
• Dinner Date Companion / डिनर डेट कम्पेनियन
• Party/Event Companion / पार्टी/इवेंट कम्पेनियन
• Night Out Package / नाइट आउट पैकेज

✅ *Features:*
• Verified Professionals
• 100% Privacy Guaranteed
• Safe & Discreet Service

⏰ *24x7 Service Available*

🔙 Click /start to go back
"""
        await query.edit_message_text(info_text, parse_mode='Markdown')
    
    elif data == "menu_contact":
        contact_text = """
📞 *CONTACT US / संपर्क करें* 📞

💬 *Reply here* - We respond quickly
⏰ *Service Hours:* 🟢 *24x7*
📍 *Location:* Lucknow

📝 *How to Book:*
1️⃣ Type /book 
2️⃣ Select service
3️⃣ Choose duration  
4️⃣ Share location

*हम 24 घंटे आपकी सेवा में हैं!*

🔙 Click /start to go back
"""
        await query.edit_message_text(contact_text, parse_mode='Markdown')
    
    # ========== SERVICE SELECTION ==========
    elif data == "book_massage":
        user_data[user_id] = {"service": "Massage / मालिश", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour / 1 घंटा", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours / 2 घंटे", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours / 4 घंटे", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night / पूरी रात", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ Selected: *Massage / मालिश*\n\nSelect duration / समय चुनें:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "book_dinner":
        user_data[user_id] = {"service": "Dinner Date / डिनर डेट", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour / 1 घंटा", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours / 2 घंटे", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours / 4 घंटे", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night / पूरी रात", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ Selected: *Dinner Date / डिनर डेट*\n\nSelect duration / समय चुनें:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "book_party":
        user_data[user_id] = {"service": "Party Companion / पार्टी कम्पेनियन", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour / 1 घंटा", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours / 2 घंटे", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours / 4 घंटे", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night / पूरी रात", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ Selected: *Party Companion / पार्टी कम्पेनियन*\n\nSelect duration / समय चुनें:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "book_night":
        user_data[user_id] = {"service": "Night Package / नाइट पैकेज", "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour / 1 घंटा", callback_data="dur_1")],
            [InlineKeyboardButton("⏰ 2 Hours / 2 घंटे", callback_data="dur_2")],
            [InlineKeyboardButton("⏰ 4 Hours / 4 घंटे", callback_data="dur_4")],
            [InlineKeyboardButton("🌙 Full Night / पूरी रात", callback_data="dur_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_book")]
        ]
        await query.edit_message_text(
            "✅ Selected: *Night Package / नाइट पैकेज*\n\nSelect duration / समय चुनें:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "book_cancel":
        if user_id in user_data:
            del user_data[user_id]
        await query.edit_message_text(
            "❌ *Booking cancelled / बुकिंग रद्द*\n\nYou can start again with /book",
            parse_mode='Markdown'
        )
    
    # ========== DURATION SELECTION ==========
    elif data == "dur_1":
        if user_id in user_data:
            user_data[user_id]["duration"] = "1 Hour / 1 घंटा"
            user_data[user_id]["step"] = "location"
        await query.edit_message_text(
            "✅ Duration: *1 Hour / 1 घंटा*\n\n📍 *Please share your location / कृपया अपनी लोकेशन भेजें*\n\nTap attachment (📎) → Location → Send Live Location",
            parse_mode='Markdown'
        )
    
    elif data == "dur_2":
        if user_id in user_data:
            user_data[user_id]["duration"] = "2 Hours / 2 घंटे"
            user_data[user_id]["step"] = "location"
        await query.edit_message_text(
            "✅ Duration: *2 Hours / 2 घंटे*\n\n📍 *Please share your location / कृपया अपनी लोकेशन भेजें*\n\nTap attachment (📎) → Location → Send Live Location",
            parse_mode='Markdown'
        )
    
    elif data == "dur_4":
        if user_id in user_data:
            user_data[user_id]["duration"] = "4 Hours / 4 घंटे"
            user_data[user_id]["step"] = "location"
        await query.edit_message_text(
            "✅ Duration: *4 Hours / 4 घंटे*\n\n📍 *Please share your location / कृपया अपनी लोकेशन भेजें*\n\nTap attachment (📎) → Location → Send Live Location",
            parse_mode='Markdown'
        )
    
    elif data == "dur_night":
        if user_id in user_data:
            user_data[user_id]["duration"] = "Full Night / पूरी रात"
            user_data[user_id]["step"] = "location"
        await query.edit_message_text(
            "✅ Duration: *Full Night / पूरी रात*\n\n📍 *Please share your location / कृपया अपनी लोकेशन भेजें*\n\nTap attachment (📎) → Location → Send Live Location",
            parse_mode='Markdown'
        )

# ============================================
# LOCATION HANDLER
# ============================================

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's live location"""
    user_id = update.effective_user.id
    message = update.message
    
    if user_id not in user_data or user_data[user_id].get("step") != "location":
        await message.reply_text(
            "📍 Type /book to start a new booking"
        )
        return
    
    lat = message.location.latitude
    lon = message.location.longitude
    service = user_data[user_id].get("service", "Unknown")
    duration = user_data[user_id].get("duration", "Unknown")
    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    bookings[booking_id] = {
        "user_id": user_id,
        "user_name": message.from_user.first_name,
        "service": service,
        "duration": duration,
        "time": datetime.now().isoformat()
    }
    
    await message.reply_text(f"""
✅ *BOOKING CONFIRMED!* ✅

📋 *Booking ID:* `{booking_id}`
💼 *Service:* {service}
⏱️ *Duration:* {duration}

📞 *Next Steps:*
Our associate will call you shortly.

*Thank you for choosing our service!*
""", parse_mode='Markdown')
    
    maps_link = f"https://maps.google.com/?q={lat},{lon}"
    await context.bot.send_message(ADMIN_ID, f"""
🔔 *NEW BOOKING ALERT* 🔔

👤 *Customer:* {message.from_user.first_name}
🆔 *Username:* @{message.from_user.username or 'N/A'}
📋 *Booking ID:* `{booking_id}`

💼 *Service:* {service}
⏱️ *Duration:* {duration}

📍 *Location:* {maps_link}
""", parse_mode='Markdown')
    
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
    elif "location" in text or "लोकेशन" in text or "area" in text:
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
    
    # Add callback query handler - IMPORTANT: This handles all button clicks
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handlers
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    
    print("✅ Bot is running 24/7!")
    print("✅ All buttons are now WORKING!")
    print("=" * 50)
    
    # Start bot polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
