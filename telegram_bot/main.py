"""Telegram bot entry point. Use: python -m telegram_bot.main"""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "proto_gen") not in sys.path:
    sys.path.insert(0, str(ROOT / "proto_gen"))

from telegram import Update
from telegram.error import NetworkError, TimedOut
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from telegram_bot.config import TelegramBotConfig
from telegram_bot.gateway_client import GatewayClient
from telegram_bot.handlers.add_city import add_city
from telegram_bot.handlers.cities import cities
from telegram_bot.handlers.city_callback import city_callback
from telegram_bot.handlers.dress import dress
from telegram_bot.handlers.language import language_callback, language_command
from telegram_bot.handlers.start import start
from telegram_bot.handlers.weather import weather
from telegram_bot.i18n import t
from telegram_bot.menu_commands import get_menu_commands

logger = logging.getLogger(__name__)


def _is_main_menu_button(text: str) -> bool:
    for locale in ("en", "ru"):
        if text == t("buttons.cities", locale) or text == t("buttons.weather", locale):
            return True
        if text == t("buttons.dress", locale) or text == t("buttons.add_city", locale):
            return True
        if text == t("buttons.language", locale):
            return True
    return False


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log exceptions and optionally notify the user (skip for network errors)."""
    err = context.error
    logger.exception("Update %s caused error: %s", update, err)
    if err and isinstance(err, (TimedOut, NetworkError)):
        return
    if isinstance(update, Update) and update.effective_message:
        locale = (context.user_data or {}).get("locale", "en")
        try:
            await update.effective_message.reply_text(t("commands.errors.generic", locale))
        except Exception:
            logger.debug("Could not send error message to user", exc_info=True)


async def main_menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    gateway_client: GatewayClient,
    cities_cmd,
    weather_cmd,
    dress_cmd,
    add_city_cmd,
) -> None:
    """Route main menu button text to the right command handler; or try add_city with free text."""
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    if _is_main_menu_button(text):
        for locale in ("en", "ru"):
            if text == t("buttons.cities", locale):
                await cities_cmd(update, context)
                return
            if text == t("buttons.weather", locale):
                await weather_cmd(update, context)
                return
            if text == t("buttons.dress", locale):
                await dress_cmd(update, context)
                return
            if text == t("buttons.add_city", locale):
                await add_city_cmd(update, context)
                return
            if text == t("buttons.language", locale):
                await language_command(update, context)
                return
        return
    # Try parsing as "CityName lat lon" for add_city
    parts = text.split()
    if len(parts) >= 3:
        try:
            float(parts[-2])
            float(parts[-1])
            context.args = parts
            await add_city_cmd(update, context)
        except ValueError:
            pass


def main() -> None:
    config = TelegramBotConfig()
    logging.basicConfig(
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        level=getattr(logging, config.log_level.upper(), logging.INFO),
    )
    if not config.telegram_bot_token:
        print("Set TELEGRAM_BOT_TOKEN to run the bot.")
        return
    client = GatewayClient(config.gateway_grpc_addr)

    async def cities_cmd(update, context):
        await cities(update, context, gateway_client=client)

    async def weather_cmd(update, context):
        await weather(update, context, gateway_client=client)

    async def dress_cmd(update, context):
        await dress(update, context, gateway_client=client)

    async def add_city_cmd(update, context):
        await add_city(update, context, gateway_client=client)

    async def on_main_menu_text(update, context):
        await main_menu_handler(
            update,
            context,
            gateway_client=client,
            cities_cmd=cities_cmd,
            weather_cmd=weather_cmd,
            dress_cmd=dress_cmd,
            add_city_cmd=add_city_cmd,
        )

    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands(get_menu_commands("en"))

    app = Application.builder().token(config.telegram_bot_token).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cities", cities_cmd))
    app.add_handler(CommandHandler("add_city", add_city_cmd))
    app.add_handler(CommandHandler("weather", weather_cmd))
    app.add_handler(CommandHandler("dress", dress_cmd))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("lang", language_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_main_menu_text))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang:"))

    async def on_city_callback(update, context):
        await city_callback(update, context, gateway_client=client)

    app.add_handler(
        CallbackQueryHandler(
            on_city_callback,
            pattern="^(main:|cities:|city_sel:|city_act:|[wd]:)",
        )
    )
    app.add_error_handler(error_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
