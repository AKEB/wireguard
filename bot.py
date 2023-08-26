#!./venv/bin/python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that works with polls. Only 3 people are allowed to interact with each
poll/quiz the bot generates. The preview command generates a closed poll/quiz, exactly like the
one the user sends the bot
"""
import logging
from telegram import __version__ as TG_VER
from dotenv import load_dotenv
import os
import glob
import subprocess

load_dotenv(".env")

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import (
    Poll,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ADMIN_TELEGRAM_ID = os.getenv('TELEGRAM_USER_ID')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    if str(update.effective_chat.id) != str(ADMIN_TELEGRAM_ID):
        return await update.message.reply_text("You don't have permissions")
    await update.message.reply_text(
        "OK"
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a predefined poll"""
    questions = ["1", "2", "4", "20"]
    message = await update.effective_message.reply_poll(
        "How many eggs do you need for a cake?", questions, type=Poll.QUIZ, correct_option_id=2
    )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    context.bot_data.update(payload)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    await update.message.reply_text("Use /add <user1> <user2>, /del <user1> <user2>, /send <user1> <user2>, /stat, /users.")


async def add_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ """
    if str(update.effective_chat.id) != str(ADMIN_TELEGRAM_ID):
        return await update.message.reply_text("You don't have permissions")
    users = str(update.message.text).replace('/add ', '', 1).strip()
    if not users:
        return await update.message.reply_text("Use /add <user1> <user2>")
    result = subprocess.run(['./wg.sh', 'add', users], stdout=subprocess.PIPE)
    await update.message.reply_text("OK")


async def del_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ """
    if str(update.effective_chat.id) != str(ADMIN_TELEGRAM_ID):
        return await update.message.reply_text("You don't have permissions")
    users = str(update.message.text).replace('/del ', '', 1).strip()
    if not users:
        return await update.message.reply_text("Use /del <user1> <user2>")
    result = subprocess.run(['./wg.sh', 'del', users], stdout=subprocess.PIPE)
    await update.message.reply_text(result.stdout.decode('utf-8'))


async def send_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ """
    if str(update.effective_chat.id) != str(ADMIN_TELEGRAM_ID):
        return await update.message.reply_text("You don't have permissions")
    users = str(update.message.text).replace('/send ', '', 1).strip()
    if not users:
        return await update.message.reply_text("Use /send <user1> <user2>")
    result = subprocess.run(['./wg.sh', 'send', users], stdout=subprocess.PIPE)
    await update.message.reply_text(result.stdout.decode('utf-8'))


async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ """
    if str(update.effective_chat.id) != str(ADMIN_TELEGRAM_ID):
        return await update.message.reply_text("You don't have permissions")
    result = subprocess.Popen(['./wg.sh', 'stat'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    await update.message.reply_text(result.communicate()[0].decode('utf-8'))


async def users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ """
    if str(update.effective_chat.id) != str(ADMIN_TELEGRAM_ID):
        return await update.message.reply_text("You don't have permissions")
    users = glob.glob('./config/peer_*')
    users = [sub.replace('./config/peer_', '') for sub in users]
    await update.message.reply_text("\n".join(users))


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_users))
    application.add_handler(CommandHandler("del", del_users))
    application.add_handler(CommandHandler("stat", stat))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("send", send_users))
    application.add_handler(CommandHandler("help", help_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
