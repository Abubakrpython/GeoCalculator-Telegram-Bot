import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from my_loaders import bot, db, config
from handlers import start, location, about, help
from utils.set_my_command import set_default_commands

# -------------------------------------------------------------------
# Logging configuration
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


async def run_bot() -> None:
    """
    Main entry point for running the Telegram bot.
    Initializes database, registers routers and starts polling.
    """
    dispatcher = Dispatcher(storage=MemoryStorage())

    # ---------------- Database ----------------
    await db.connect()
    await db.create_tables()
    logger.info("✅ Database connected and tables ensured.")

    # ---------------- Routers ----------------
    dispatcher.include_router(start.router)
    dispatcher.include_router(location.router)
    dispatcher.include_router(help.router)
    dispatcher.include_router(about.router)

    # ---------------- Bot startup ----------------
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await set_default_commands(bot)

        # Notify admins that bot is online
        for admin_id in config.admin_ids:
            try:
                await bot.send_message(admin_id, "🤖 Bot has started successfully!")
            except Exception:
                logger.warning(f"Could not notify admin {admin_id}")

        logger.info("🚀 Bot started successfully.")
        await dispatcher.start_polling(bot)

    except asyncio.CancelledError:
        logger.warning("🛑 Bot polling cancelled.")

    except Exception as e:
        logger.exception(f"❌ Unexpected error: {e}")
        for admin_id in config.admin_ids:
            try:
                await bot.send_message(admin_id, f"❌ Bot error:\n<code>{e}</code>")
            except Exception:
                pass

    finally:
        # ---------------- Shutdown ----------------
        await db.disconnect()
        await bot.session.close()
        logger.info("🔌 Bot and database connections closed.")

        for admin_id in config.admin_ids:
            try:
                await bot.send_message(admin_id, "🛑 Bot has been stopped.")
            except Exception:
                pass


def main() -> None:
    """CLI entry point."""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by KeyboardInterrupt")


if __name__ == "__main__":
    main()
