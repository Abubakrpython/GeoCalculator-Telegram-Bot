import logging
from aiogram import Router, types
from aiogram.filters import Command

from my_loaders import db, bot, config
from keyboards.keyboardm import main_menu

router = Router()
logger = logging.getLogger(__name__)

ADMIN_IDS = config.admins.ids


@router.message(Command("start"))
async def start_cmd(message: types.Message):
    """Start command — registers user and shows main menu."""
    try:
        # Save user
        await db.add_user(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )

        logger.info(
            f"New user registered: {message.from_user.full_name} ({message.from_user.id})"
        )

        # Notify admins
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    (
                        "🆕 <b>New user joined</b>\n\n"
                        f"👤 <b>Name:</b> {message.from_user.full_name}\n"
                        f"🔗 <b>Username:</b> @{message.from_user.username or 'N/A'}\n"
                        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>"
                    ),
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"Failed to notify admin {admin_id}: {e}")

        # Reply to user
        await message.answer(
            (
                f"Hello, <b>{message.from_user.first_name}</b> 👋\n\n"
                "I am a geographic calculation bot.\n"
                "Please choose an option from the menu below 👇"
            ),
            reply_markup=main_menu,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.exception("Error in /start command")

        await message.answer(
            "⚠️ An internal error occurred.\n"
            "Please try again later."
        )

        # Notify admins about error
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    (
                        "❌ <b>Bot error (start command)</b>\n\n"
                        f"👤 User: {message.from_user.full_name}\n"
                        f"🆔 <code>{message.from_user.id}</code>\n"
                        f"📝 Error:\n<code>{e}</code>"
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass
