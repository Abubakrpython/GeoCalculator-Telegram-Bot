import logging
from aiogram import Router, types
from aiogram.filters import Command

from keyboards.keyboardm import main_menu

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("help"))
async def help_command(message: types.Message):
    """
    Displays help information and explains how to use the bot.
    """
    try:
        text = (
            "❓ <b>Help Center</b>\n"
            "────────────────────────────\n"
            "<b>GeoCalculator Bot</b> is a geographic calculation system designed "
            "to compute distances between coordinates and generate intermediate waypoints.\n\n"

            "📘 <b>Available commands:</b>\n"
            "• /start — Start the bot and open the main menu\n"
            "• /coordinate — Start coordinate calculation 🧭\n"
            "• /history — View your recent calculations 📜\n"
            "• /about — Information about the bot ℹ️\n"
            "• /help — Open this help window ❓\n\n"

            "────────────────────────────\n"
            "🧭 <b>How to use:</b>\n"
            "1️⃣ Tap <b>“🧭 Coordinate calculation”</b> or send /coordinate\n"
            "2️⃣ Enter the first coordinate (example: <code>41.311081, 69.240562</code>)\n"
            "3️⃣ Enter the second coordinate\n"
            "4️⃣ Select the number of segments (5, 10, 15, ...)\n"
            "5️⃣ The bot will calculate total distance and all intermediate points\n\n"

            "────────────────────────────\n"
            "💡 <b>Tips:</b>\n"
            "• Always use the format: <code>latitude, longitude</code>\n"
            "• To cancel the process, press <b>“❌ Cancel”</b>\n\n"
            "────────────────────────────\n"
        )

        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=main_menu
        )

        logger.info(
            f"📘 User ({message.from_user.id}) opened the help section."
        )

    except Exception as e:
        logger.exception(f"❌ Error in /help command: {e}")
        await message.answer(
            "⚠️ An error occurred while opening the help section."
        )
