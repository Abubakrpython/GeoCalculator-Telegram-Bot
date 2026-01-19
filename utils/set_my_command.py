from aiogram.types import BotCommand


async def set_default_commands(bot):
    """
    Set default bot commands visible in Telegram UI.
    """
    commands = [
        BotCommand(
            command="start",
            description="🤖 Start the bot"
        ),
        BotCommand(
            command="coordinate",
            description="🧭 Calculate distance between coordinates"
        ),
        BotCommand(
            command="history",
            description="📜 View your recent calculations"
        ),
    ]

    await bot.set_my_commands(commands)
