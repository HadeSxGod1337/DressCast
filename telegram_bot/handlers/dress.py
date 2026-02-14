"""Dress advice command: /dress [city_name] — advice via gateway."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.i18n import t

logger = logging.getLogger(__name__)


async def get_dress_message(gateway_client, user_id: int, city_name: str, locale: str) -> str:
    """Fetch dress advice and return message text (or error message)."""
    try:
        r = await gateway_client.get_dress_advice(user_id, city_name, locale=locale)
        text = (r.advice_text or "").strip() or t("commands.errors.city_not_found", locale)
        return text
    except Exception as e:
        logger.warning("Dress advice failed for user_id=%s city %s: %s", user_id, city_name, e)
        err_msg = str(e).lower()
        if "not found" in err_msg or "city_not_found" in err_msg:
            return t("commands.errors.city_not_found", locale)
        return t("commands.errors.generic", locale)


async def dress(
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
        await update.message.reply_text(t("commands.dress.usage", locale))
        return
    try:
        user = await gateway_client.get_or_create_user_by_telegram(telegram_id)
        text = await get_dress_message(gateway_client, user.id, city_name, locale)
        await update.message.reply_text(text)
    except Exception as e:
        logger.warning("Dress advice failed for user %s city %s: %s", telegram_id, city_name, e)
        await update.message.reply_text(t("commands.errors.generic", locale))
