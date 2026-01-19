import logging
from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("about"))
async def about_bot(message: types.Message):
    """
    Displays information about the GeoCalculator Bot.
    """
    text = (
        "🤖 <b>GeoCalculator Bot</b>\n"
        "────────────────────────────\n"
        "🧭 <b>Purpose:</b>\n"
        "Calculates the distance between two geographic coordinates and "
        "splits the route into equal segments with intermediate waypoints.\n\n"

        "📍 <b>What you can do:</b>\n"
        "• Quickly calculate distance between coordinates\n"
        "• Generate intermediate points along the route\n"
        "• Save and view calculation history\n\n"

        "🏢 <b>Project:</b> <i>Developed специально for CyberPark</i>\n"
        "🌐 <b>Author:</b> <i>CyberPark Development Team</i>\n"
        "📅 <b>Created:</b> 2025\n"
        "────────────────────────────\n"
        "⚙️ <b>Technologies:</b>\n"
        "Python 🐍 | Aiogram ⚙️ | PostgreSQL 🗄️ | Geopy 🌍\n\n"
        "© 2025 <b>CyberPark</b> — All rights reserved ⚡"
    )

    await message.answer(text, parse_mode="HTML")
    logger.info(f"ℹ️ User ({message.from_user.id}) opened the About section.")
