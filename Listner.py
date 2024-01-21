from telegram import BotCommand, Update
from DBPipeline import DBInstance
# from bridge_skillz_gpt.constants import PROJECT_ROOT_PATH
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from datetime import datetime
from rich.console import Console
from rich.text import Text
import os
import asyncio
from SettingLoder import BOT_WELCOME_MESSAGE
DataBase = DBInstance()

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ["client_tele_bot_token"]
console = Console()


def printPrompt(msg, color="red",end="\n"):
    console.print(Text(msg, style=color),end=end)



def InsertChat(chatId,username,Query,Response):
    DataBase.insertChatHistory(chatId, username, "user", Query)
    DataBase.insertChatHistory(chatId, username, "assistant", Response)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username
    if not username:
        username = user.full_name
    history = DataBase.getChatHistoryByUserID(user.id)
    if not history:
        iQuery=f"The date and time  i started chatting with you is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        InsertChat(user.id,username,iQuery,BOT_WELCOME_MESSAGE)
        await update.message.reply_text(BOT_WELCOME_MESSAGE)
    else:
        await update.message.reply_text(f"Yes {user.full_name} How may I assist you ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        Query = update.message.text.strip().lower()
        username = user.username or user.full_name

        if not Query:
            print("Skipped")
            return
        if Query.lower() in ['ok']:
            return
        
        if Query == "0000":
            DataBase.truncateTable()
            return
        if Query == "1111":
            DataBase.deleteChatHistoryByUserID(user.id)
            return
        
        DataBase.insertChatHistory(user.id, username, "user", Query)
        printPrompt(f"({user.full_name}) Query    >>    {Query}")
        await asyncio.sleep(2)
        await context.bot.send_chat_action(chat_id=user.id, action="typing")
    except Exception as e:
        print(f"[+] Telegram Error : {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Script listener is active. Ready to receive messages.")
    # Run the bot until the user presses Ctrl-C
    app.run_polling()


def StartListner():
    main()

if __name__=="__main__":
    main()