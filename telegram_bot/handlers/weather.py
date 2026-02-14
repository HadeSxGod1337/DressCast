"""Weather command: /weather [city_name] — forecast via gateway."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.i18n import t

logger = logging.getLogger(__name__)


async def get_weather_message(gateway_client, user_id: int, city_name: str, locale: str) -> str:
    """Fetch forecast and return message text (or error message)."""
    try:
        r = await gateway_client.get_forecast(user_id, city_name)
        if not r.weather_data or not r.weather_data.time:
            return t("commands.errors.city_not_found", locale)
        d = r.weather_data
        return t("commands.weather.result", locale).format(
            city=city_name,
            temp=d.temperature,
            humidity=d.humidity,
            wind=d.wind_speed,
            precip=d.precipitation,
            time=d.time or "",
        )
    except Exception as e:
        logger.warning("Weather failed for user_id=%s city %s: %s", user_id, city_name, e)
        err_msg = str(e).lower()
        if "not found" in err_msg or "city_not_found" in err_msg:
            return t("commands.errors.city_not_found", locale)
        return t("commands.errors.generic", locale)


async def weather(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    gateway_client,
) -> None:
    locale = (context.user_data or {}).get("locale", "en")
    telegram_id = str(getattr(update.effective_user, "id", None) or "")
    if not telegram_id:
        await update.message.reply_text(t("commands.errors.generic", locale))
        return
    city_name = (context.args or []) and " ".join(context.args).strip() or ""
    if not city_name:
        await update.message.reply_text(t("commands.weather.usage", locale))
        return
    try:
        user = await gateway_client.get_or_create_user_by_telegram(telegram_id)
        msg = await get_weather_message(gateway_client, user.id, city_name, locale)
        await update.message.reply_text(msg)
    except Exception as e:
        logger.warning("Weather failed for user %s city %s: %s", telegram_id, city_name, e)
        await update.message.reply_text(t("commands.errors.generic", locale))
