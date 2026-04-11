"""
LUCKNOW CALLBOY BOT - RENDER DEPLOYMENT VERSION
No Payment - Only Booking System
"""

import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# ============================================
# FLASK APP FOR RENDER HEALTH CHECK
# Render needs a web server to keep the service alive
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
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Render environment variable से लेगा
ADMIN_ID = int(os.environ.get("ADMIN_ID", 1919682117))

# Temporary storage (in production, use database)
user_data = {}
bookings = {}

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    welcome_text = """
🔥 *WELCOME TO LUCKNOW CALLBOY SERVICE* 🔥

✨ *Premium Entertainment Services* ✨

📋 *Commands:*
/book - Book Now
/info - Service Info
/contact - Contact Us
/help - Need Help?

🔒 *100% Privacy Guaranteed*
📍 *Service in Lucknow & nearby*
"""
    keyboard = [
        [InlineKeyboardButton("📅 Book Now", callback_data="book")],
        [InlineKeyboardButton("ℹ️ Service Info", callback_data="info")],
        [InlineKeyboardButton("📞 Contact Us", callback_data="contact")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start booking process"""
    user_id = update.effective_user.id
    user_data[user_id] = {"step": "service"}
    
    keyboard = [
        [InlineKeyboardButton("💆‍♂️ Massage", callback_data="service_massage")],
        [InlineKeyboardButton("🍽️ Dinner Date", callback_data="service_dinner")],
        [InlineKeyboardButton("🎉 Party Companion", callback_data="service_party")],
        [InlineKeyboardButton("📸 Photoshoot", callback_data="service_photo")],
        [InlineKeyboardButton("🌙 Night Package", callback_data="service_night")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    await update.message.reply_text("📅 *NEW BOOKING*\n\nSelect service:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Service information"""
    info_text = """
ℹ️ *SERVICE INFORMATION* ℹ️

✨ *What We Offer:*
• Professional Massage Service
• Dinner Date Companion
• Party/Event Companion
• Professional Photoshoot
• Night Out Package

✅ *Features:*
• Verified Professionals
• 100% Privacy Guaranteed
• Safe & Discreet Service
"""
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contact information"""
    contact_text = """
📞 *CONTACT US* 📞

💬 *Reply here* - We respond within 5 minutes
⏰ *Service Hours:* 10 AM - 10 PM
📍 *Location:* Lucknow

🔒 *Privacy Guaranteed*
"""
    await update.message.reply_text(contact_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help menu"""
    help_text = """
ℹ️ *HOW TO USE THIS BOT* ℹ️

📅 *To Book a Service:*
1. Type /book
2. Select service type
3. Choose duration
4. Share your live location
5. Booking confirmed!

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
# BUTTON CALLBACKS
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    if data == "book":
        await book(update, context)
    elif data == "info":
        await info(update, context)
    elif data == "contact":
        await contact(update, context)
    elif data.startswith("service_"):
        service = data.replace("service_", "")
        user_data[user_id] = {"service": service, "step": "duration"}
        keyboard = [
            [InlineKeyboardButton("⏰ 1 Hour", callback_data="duration_1")],
            [InlineKeyboardButton("⏰ 2 Hours", callback_data="duration_2")],
            [InlineKeyboardButton("⏰ 4 Hours", callback_data="duration_4")],
            [InlineKeyboardButton("🌙 Full Night", callback_data="duration_night")],
            [InlineKeyboardButton("🔙 Back", callback_data="book")]
        ]
        await query.edit_message_text(f"✅ Selected: *{service}*\n\nSelect duration:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    elif data.startswith("duration_"):
        duration_map = {
            "duration_1": "1 Hour",
            "duration_2": "2 Hours",
            "duration_4": "4 Hours",
            "duration_night": "Full Night"
        }
        duration = duration_map.get(data, "Unknown")
        user_data[user_id]["duration"] = duration
        user_data[user_id]["step"] = "location"
        await query.edit_message_text(f"✅ Duration: *{duration}*\n\n📍 *Please share your location*\n\nTap attachment (📎) → Location → Send Live Location", parse_mode='Markdown')
    elif data == "cancel":
        if user_id in user_data:
            del user_data[user_id]
        await query.edit_message_text("❌ *Booking cancelled*", parse_mode='Markdown')

# ============================================
# LOCATION HANDLER
# ============================================

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's live location"""
    user_id = update.effective_user.id
    message = update.message
    
    if user_id not in user_data or user_data[user_id].get("step") != "location":
        await message.reply_text("📍 Type /book to start a new booking")
        return
    
    lat = message.location.latitude
    lon = message.location.longitude
    service = user_data[user_id].get("service", "Unknown")
    duration = user_data[user_id].get("duration", "Unknown")
    
    # Generate unique booking ID
    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Save booking
    bookings[booking_id] = {
        "user_id": user_id,
        "user_name": message.from_user.first_name,
        "service": service,
        "duration": duration,
        "time": datetime.now().isoformat()
    }
    
    # Send confirmation to user
    await message.reply_text(f"""
✅ *BOOKING CONFIRMED!* ✅

📋 *Booking ID:* `{booking_id}`
💼 *Service:* {service}
⏱️ *Duration:* {duration}

📞 *Next Steps:*
Our associate will call you shortly at your location.

⚠️ *Cancellation:* Free up to 2 hours before

*Thank you for choosing our service!*
""", parse_mode='Markdown')
    
    # Send notification to admin
    maps_link = f"https://maps.google.com/?q={lat},{lon}"
    await context.bot.send_message(ADMIN_ID, f"""
🔔 *NEW BOOKING ALERT* 🔔

👤 *Customer:* {message.from_user.first_name}
🆔 *Username:* @{message.from_user.username or 'N/A'}
📋 *Booking ID:* `{booking_id}`

💼 *Service:* {service}
⏱️ *Duration:* {duration}

📍 *Location:* {maps_link}
📅 *Booked at:* {datetime.now().strftime('%d-%b %I:%M %p')}
""", parse_mode='Markdown')
    
    # Clear user data
    del user_data[user_id]

# ============================================
# AUTO REPLY HANDLER
# ============================================

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto reply for common questions and forward to admin"""
    text = update.message.text.lower()
    
    # Quick replies for common questions
    if "help" in text:
        await update.message.reply_text("Type /start for menu, /book for booking")
    elif "location" in text or "area" in text:
        await update.message.reply_text("📍 Service areas: Lucknow (Gomti Nagar, Hazratganj, Aliganj, Indira Nagar)")
    elif "cancel" in text:
        await update.message.reply_text("❌ To cancel, please reply to your booking confirmation message.")
    else:
        # Forward unknown messages to admin
        await context.bot.send_message(ADMIN_ID, f"📩 *New Message*\n👤 @{update.effective_user.username or update.effective_user.first_name}\n💬 {update.message.text}", parse_mode='Markdown')
        await update.message.reply_text("✅ Message received! We'll respond shortly.")

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("=" * 50)
    print("🚀 LUCKNOW CALLBOY BOT STARTING...")
    print("=" * 50)
    
    # Start Flask health check server in background
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Flask health check server started on port 8080")
    
    # Create bot application
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("help", help_command))
    
    # Add callback query handler for buttons
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handlers
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    
    print("✅ Bot is running 24/7 on Render!")
    print("=" * 50)
    
    # Start bot polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()