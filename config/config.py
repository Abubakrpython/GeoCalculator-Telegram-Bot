import os
from dataclasses import dataclass
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TelegramBotConfig:
    token: str


@dataclass
class DatabaseConfig:
    dsn: str


@dataclass
class AdminConfig:
    ids: list[int]


@dataclass
class Config:
    tg_bot: TelegramBotConfig
    database: DatabaseConfig
    admins: AdminConfig
    parse_mode: ParseMode = ParseMode.HTML


def load_config() -> Config:
    admin_ids = [
        int(x.strip())
        for x in os.getenv("ADMIN_IDS", "").split(",")
        if x.strip().isdigit()
    ]

    return Config(
        tg_bot=TelegramBotConfig(
            token=os.getenv("BOT_TOKEN")
        ),
        database=DatabaseConfig(
            dsn=os.getenv("DATABASE_URL")
        ),
        admins=AdminConfig(
            ids=admin_ids
        ),
        parse_mode=ParseMode.HTML
    )
