import logging
import os

# Log papkasini yaratamiz
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log fayli nomi
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

# Asosiy logging konfiguratsiyasi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("CyberLogs")
