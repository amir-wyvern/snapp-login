import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from datetime import datetime, timedelta
import snapp_module
from models import Session, SnappUser
from sqlalchemy import desc
import os
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# States for conversation handler
CHOOSING, PHONE_NUMBER, OTP, GET_DATA, LIST_ACCOUNTS = range(5)

# Keyboard layouts
BACK_KEYBOARD = ReplyKeyboardMarkup([['⬅️ Back']], one_time_keyboard=True, resize_keyboard=True)
CANCEL_KEYBOARD = ReplyKeyboardMarkup([['❌ Cancel']], one_time_keyboard=True, resize_keyboard=True)
RETRY_KEYBOARD = ReplyKeyboardMarkup([['🔄 Retry', '⬅️ Back']], one_time_keyboard=True, resize_keyboard=True)
START_KEYBOARD = ReplyKeyboardMarkup([['➕ Add Account', '📱 Get Data', '📋 List Accounts']], one_time_keyboard=True, resize_keyboard=True)

# Constants
ACCOUNTS_PER_PAGE = 20

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    # Remove any spaces
    phone = phone.replace(" ", "")
    # Check if it's a valid Iranian phone number (10 digits, no prefix)
    return phone.isdigit() and len(phone) == 10

def format_account_info(user: SnappUser) -> str:
    """Format user account information for display."""
    status = "✅ Active" if user.status else "❌ Inactive"
    expire_time = user.token_expire_time.strftime("%Y-%m-%d %H:%M:%S") if user.token_expire_time else "N/A"
    login_time = user.login_time.strftime("%Y-%m-%d %H:%M:%S") if user.login_time else "N/A"
    
    return (
        f"👤 Name: {user.full_name or 'Not set'}\n"
        f"📱 Phone: {user.phone_number}\n"
        f"🔵 Status: {status}\n"
        f"🕒 Login Time: {login_time}\n"
        f"⏰ Token Expires: {expire_time}\n"
        f"🔑 Access Token: {user.access_token[:20]}...\n"
        f"🔄 Refresh Token: {user.refresh_token[:20]}..."
    )

def get_accounts_page(page: int = 1) -> tuple[list[SnappUser], int, int]:
    """Get paginated list of accounts."""
    session = Session()
    
    # Get total count
    total_accounts = session.query(SnappUser).count()
    total_pages = (total_accounts + ACCOUNTS_PER_PAGE - 1) // ACCOUNTS_PER_PAGE
    
    # Get accounts for current page
    accounts = session.query(SnappUser).order_by(desc(SnappUser.login_time)).offset(
        (page - 1) * ACCOUNTS_PER_PAGE
    ).limit(ACCOUNTS_PER_PAGE).all()
    
    session.close()
    return accounts, total_pages, total_accounts

def create_pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Create pagination keyboard."""
    keyboard = []
    row = []
    
    # Previous page button
    if current_page > 1:
        row.append(InlineKeyboardButton("⬅️", callback_data=f"page_{current_page-1}"))
    
    # Current page indicator
    row.append(InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="current"))
    
    # Next page button
    if current_page < total_pages:
        row.append(InlineKeyboardButton("➡️", callback_data=f"page_{current_page+1}"))
    
    keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def format_accounts_list(accounts: list[SnappUser], page: int, total_pages: int, total_accounts: int) -> str:
    """Format the accounts list message."""
    header = f"📋 Accounts List (Total: {total_accounts})\n"
    header += f"Page {page} of {total_pages}\n"
    header += "Click on any phone number to view details\n\n"
    
    accounts_text = ""
    for i, account in enumerate(accounts, 1):
        status = "✅" if account.status else "❌"
        accounts_text += f"{i}. {status} /phone_{account.phone_number}\n"
    
    return header + accounts_text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and show the main menu."""
    await update.message.reply_text(
        "Welcome to Snapp Login Bot!\n"
        "Choose an option:",
        reply_markup=START_KEYBOARD
    )
    return CHOOSING

async def choosing_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the main menu button presses."""
    text = update.message.text.strip()
    
    if text == '➕ Add Account':
        await update.message.reply_text(
            "Please send the phone number (without +98 or 0):",
            reply_markup=CANCEL_KEYBOARD
        )
        return PHONE_NUMBER
    elif text == '📱 Get Data':
        await update.message.reply_text(
            "Please enter the phone number to view its data (without +98 or 0):",
            reply_markup=CANCEL_KEYBOARD
        )
        return GET_DATA
    elif text == '📋 List Accounts':
        # Get first page of accounts
        accounts, total_pages, total_accounts = get_accounts_page(1)
        
        if total_accounts == 0:
            await update.message.reply_text(
                "No accounts registered yet.",
                reply_markup=START_KEYBOARD
            )
            return CHOOSING
        
        message_text = format_accounts_list(accounts, 1, total_pages, total_accounts)
        
        # Only show pagination keyboard if there are multiple pages
        if total_pages > 1:
            keyboard = create_pagination_keyboard(1, total_pages)
            await update.message.reply_text(message_text, reply_markup=keyboard)
        else:
            await update.message.reply_text(message_text, reply_markup=START_KEYBOARD)
        
        return LIST_ACCOUNTS
    else:
        await update.message.reply_text(
            "Please use one of the buttons to proceed.",
            reply_markup=START_KEYBOARD
        )
        return CHOOSING

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pagination button clicks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "current":
        return LIST_ACCOUNTS
    
    # Extract page number from callback data
    page = int(query.data.split('_')[1])
    
    # Get accounts for requested page
    accounts, total_pages, total_accounts = get_accounts_page(page)
    message_text = format_accounts_list(accounts, page, total_pages, total_accounts)
    
    # Update message with new page
    keyboard = create_pagination_keyboard(page, total_pages)
    await query.edit_message_text(message_text, reply_markup=keyboard)
    
    return LIST_ACCOUNTS

async def get_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle viewing account data."""
    text = update.message.text.strip()
    
    if text == '❌ Cancel':
        await update.message.reply_text(
            "Operation cancelled.",
            reply_markup=START_KEYBOARD
        )
        return CHOOSING
    
    if text == '⬅️ Back':
        await update.message.reply_text(
            "Choose an option:",
            reply_markup=START_KEYBOARD
        )
        return CHOOSING
    
    # Validate phone number format
    if not validate_phone_number(text):
        await update.message.reply_text(
            "❌ Invalid phone number format! Please enter a 10-digit number without +98 or 0.\n"
            "For example: 9123456789",
            reply_markup=RETRY_KEYBOARD
        )
        return GET_DATA
    
    try:
        session = Session()
        user = session.query(SnappUser).filter_by(phone_number=text).first()
        session.close()
        
        if user:
            # Check if token is expired
            is_expired = user.token_expire_time and user.token_expire_time < datetime.utcnow()
            if is_expired:
                status_msg = "\n⚠️ Note: Token has expired!"
            else:
                status_msg = ""
                
            await update.message.reply_text(
                f"📱 Account Information:\n\n{format_account_info(user)}{status_msg}",
                reply_markup=START_KEYBOARD
            )
        else:
            await update.message.reply_text(
                "❌ No account found with this phone number!",
                reply_markup=START_KEYBOARD
            )
        
        return CHOOSING
        
    except Exception as e:
        logging.error(f"Database error in get_data: {str(e)}")
        await update.message.reply_text(
            "❌ Error retrieving account data. Please try again.",
            reply_markup=RETRY_KEYBOARD
        )
        return GET_DATA

async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle phone number input and request OTP."""
    text = update.message.text.strip()
    
    if text == '❌ Cancel':
        await update.message.reply_text(
            "Operation cancelled. Click Add Account to try again.",
            reply_markup=START_KEYBOARD
        )
        return CHOOSING
    
    if text == '🔄 Retry':
        await update.message.reply_text(
            "Please enter the phone number again (without +98 or 0):",
            reply_markup=CANCEL_KEYBOARD
        )
        return PHONE_NUMBER
    
    phone = text
    
    # Validate phone number format
    if not validate_phone_number(phone):
        await update.message.reply_text(
            "❌ Invalid phone number format! Please enter a 10-digit number without +98 or 0.\n"
            "For example: 9123456789",
            reply_markup=RETRY_KEYBOARD
        )
        return PHONE_NUMBER
    
    # Store phone number in context for later use
    context.user_data['phone'] = phone
    
    # Check if user already exists and is logged in
    try:
        session = Session()
        existing_user = session.query(SnappUser).filter_by(phone_number=phone).first()
        session.close()
        
        if existing_user and existing_user.status:
            await update.message.reply_text(
                "This phone number is already registered and logged in!\n"
                "Click Add Account to register a different number.",
                reply_markup=START_KEYBOARD
            )
            return CHOOSING
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Database error while checking existing users. Please try again.",
            reply_markup=RETRY_KEYBOARD
        )
        logging.error(f"Database error in phone_number: {str(e)}")
        return PHONE_NUMBER
    
    try:
        # Request OTP from Snapp
        result = snapp_module.login(phone)
        await update.message.reply_text(
            "✅ OTP code has been sent to your phone.\n"
            "Please enter the code you received:",
            reply_markup=BACK_KEYBOARD
        )
        return OTP
    except Exception as e:
        error_msg = str(e)
        if "Too many attempts" in error_msg:
            msg = "❌ Too many OTP requests. Please wait a few minutes before trying again."
        else:
            msg = f"❌ Error requesting OTP: {error_msg}\nPlease try again or use a different number."
        
        await update.message.reply_text(
            msg,
            reply_markup=RETRY_KEYBOARD
        )
        return PHONE_NUMBER

async def otp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle OTP verification and complete login."""
    text = update.message.text.strip()
    
    if text == '⬅️ Back':
        await update.message.reply_text(
            "Please enter the phone number again (without +98 or 0):",
            reply_markup=CANCEL_KEYBOARD
        )
        return PHONE_NUMBER
        
    if text == '🔄 Retry':
        await update.message.reply_text(
            "Please enter the OTP code again:",
            reply_markup=BACK_KEYBOARD
        )
        return OTP
    
    otp_code = text
    phone = context.user_data.get('phone')
    
    if not phone:
        await update.message.reply_text(
            "❌ Session expired. Please start over.",
            reply_markup=START_KEYBOARD
        )
        return CHOOSING
    
    # Validate OTP format
    if not otp_code.isdigit():
        await update.message.reply_text(
            "❌ Invalid OTP format! Please enter only numbers.",
            reply_markup=RETRY_KEYBOARD
        )
        return OTP
    
    try:
        # Verify OTP with Snapp
        result = snapp_module.otp(phone, otp_code)
        
        # Extract tokens and user info from response
        access_token = result.get('access_token')
        refresh_token = result.get('refresh_token')
        expires_in = result.get('expires_in', 3600)  # Default to 1 hour if not provided
        full_name = result.get('fullname')  # Get full name from response
        
        if not all([access_token, refresh_token]):
            raise Exception("Invalid response from Snapp: Missing tokens")
        
        # Calculate token expiration time
        expire_time = datetime.utcnow() + timedelta(seconds=expires_in)
        
        try:
            # Store in database
            session = Session()
            
            # Check if user exists
            user = session.query(SnappUser).filter_by(phone_number=phone).first()
            
            if user:
                # Update existing user
                user.full_name = full_name
                user.access_token = access_token
                user.refresh_token = refresh_token
                user.login_time = datetime.utcnow()
                user.token_expire_time = expire_time
                user.status = True
            else:
                # Create new user
                user = SnappUser(
                    phone_number=phone,
                    full_name=full_name,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_expire_time=expire_time
                )
                session.add(user)
            
            session.commit()
            session.close()
            
            await update.message.reply_text(
                "✅ Successfully logged in and saved to database!\n"
                "Click Add Account to register another number.",
                reply_markup=START_KEYBOARD
            )
            return CHOOSING
            
        except Exception as e:
            logging.error(f"Database error in OTP verification: {str(e)}")
            await update.message.reply_text(
                "❌ Error saving to database. Please try again.",
                reply_markup=RETRY_KEYBOARD
            )
            return OTP
            
    except Exception as e:
        error_msg = str(e)
        if "Invalid code" in error_msg:
            msg = "❌ Invalid OTP code! Please try again or request a new code."
        elif "expired" in error_msg.lower():
            msg = "❌ OTP code has expired. Please go back and request a new code."
        else:
            msg = f"❌ Error verifying OTP: {error_msg}"
        
        await update.message.reply_text(
            msg,
            reply_markup=RETRY_KEYBOARD
        )
        return OTP

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "Operation cancelled. Click Add Account to start again.",
        reply_markup=START_KEYBOARD
    )
    return CHOOSING

async def handle_phone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle phone number command clicks from the list."""
    # Extract phone number from command (remove the /phone_ prefix)
    phone = update.message.text[7:]  # Remove /phone_
    
    if not validate_phone_number(phone):
        await update.message.reply_text(
            "❌ Invalid phone number format!",
            reply_markup=START_KEYBOARD
        )
        return CHOOSING
    
    try:
        session = Session()
        user = session.query(SnappUser).filter_by(phone_number=phone).first()
        session.close()
        
        if user:
            # Check if token is expired
            is_expired = user.token_expire_time and user.token_expire_time < datetime.utcnow()
            if is_expired:
                status_msg = "\n⚠️ Note: Token has expired!"
            else:
                status_msg = ""
                
            await update.message.reply_text(
                f"📱 Account Information:\n\n{format_account_info(user)}{status_msg}",
                reply_markup=START_KEYBOARD
            )
        else:
            await update.message.reply_text(
                "❌ No account found with this phone number!",
                reply_markup=START_KEYBOARD
            )
        
        return CHOOSING
        
    except Exception as e:
        logging.error(f"Database error in handle_phone_command: {str(e)}")
        await update.message.reply_text(
            "❌ Error retrieving account data. Please try again.",
            reply_markup=START_KEYBOARD
        )
        return CHOOSING

def main() -> None:
    """Start the bot."""
    # Load environment variables
    load_dotenv()
    
    # Get bot token from environment variable
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is not set")

    # Create the Application and pass it your bot's token
    application = Application.builder().token(bot_token).build()

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choosing_action),
                MessageHandler(filters.Regex("^/phone_[0-9]+$"), handle_phone_command),
            ],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number)],
            OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, otp)],
            GET_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_data)],
            LIST_ACCOUNTS: [
                CallbackQueryHandler(handle_pagination),
                MessageHandler(filters.Regex("^/phone_[0-9]+$"), handle_phone_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, choosing_action),  # Handle menu buttons
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main() 