from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from utils.database import Database
from config.config import load_config

# ⚙️ Load config from .env
config = load_config()

# 🤖 Telegram bot instance
bot = Bot(
    token=config.tg_bot.token,
    default=DefaultBotProperties(parse_mode=config.parse_mode)
)

# 🧠 FSM storage
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# 🗄️ Database (DSN from .env)
db = Database(dsn=config.database.dsn)

# 🔀 Shared router
router = Router()

__all__ = ["bot", "dp", "db", "router", "config"]
