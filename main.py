from funners_core import get_new_fun_pos
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import jdatetime
import logging
import shutil
import json
import io
import osgit


logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os. getenv('BOT_TOKEN')

FUNNERS = []

async def funners(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if os.path.exists('./funners.json'):
        with open('./funners.json', 'rb') as file:
            await update.message.reply_document(document=file)        
    
    else:
        await update.message.reply_text('No funners.json file found.')

async def funners_bak(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if os.path.exists('./funners.json.bak'):
        with open('./funners.json.bak', 'rb') as file:
            await update.message.reply_document(document=file)        
    
    else:
        await update.message.reply_text('No funners.json.bak file found.')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me an Excel file!')


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    global FUNNERS

    document = update.message.document
    
    if document.mime_type == 'application/json':
        
        if os.path.exists('./funners.json'):
            shutil.copy('./funners.json', './funners.json.bak')
        
        file = await document.get_file()
        await file.download_to_drive('./funners.json')

        with open('./funners.json', 'r') as f:
            FUNNERS = json.load(f)

        await update.message.reply_text('Saved new funners.json')

    elif document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':

        if not os.path.exists('./funners.json'):
            await update.message.reply_text('funners.json file not exist.')
            return
        
        file = await document.get_file()
        file_stream = io.BytesIO()
        
        await file.download_to_memory(out=file_stream)
        
        file_stream.seek(0)

        new_funners = get_new_fun_pos(FUNNERS, file_stream)

        current_jalali_datetime = jdatetime.datetime.now()
        formatted_jalali_datetime = current_jalali_datetime.strftime('%Y_%m_%d--%H_%M')

        await update.message.reply_document(document= new_funners, filename=f"{formatted_jalali_datetime}.xlsx")

    else:
        await update.message.reply_text('Please send a valid Excel file.')

if __name__ == '__main__':

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("funners", funners))
    application.add_handler(CommandHandler("funners_bak", funners_bak))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    application.run_polling()