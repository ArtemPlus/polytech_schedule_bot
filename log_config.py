import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Пути считаются здесь напрямую (без config), чтобы модуль работал
# на свежем клоне, где ещё нет groups.json
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "bot.log"


def setup_logging():
    """Настройка логирования: файл logs/bot.log с ротацией 5 МБ x 3 старых файла."""
    root = logging.getLogger()
    # защита от двойной настройки (бот импортирует parser_run и настраивает логи сам)
    if root.handlers:
        return
    root.setLevel(logging.INFO)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="UTF-8"
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
