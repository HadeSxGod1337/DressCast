"""Add city command: /add_city <name> <lat> <lon>."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.i18n import t

logger = logging.getLogger(__name__)


async def add_city(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    gateway_client,
) -> None:
    locale = (context.user_data or {}).get("locale", "en")
    telegram_id = str(getattr(update.effective_user, "id", None) or "")
    if not telegram_id:
        await update.message.reply_text(t("commands.errors.generic", locale))
        return
    args = (context.args or []) if context.args else []
    if len(args) < 3:
        await update.message.reply_text(
            t("commands.add_city.usage", locale),
            parse_mode="HTML",
        )
        return
    try:
        lat = float(args[-2])
        lon = float(args[-1])
        name = " ".join(args[:-2]).strip()
    except ValueError:
        await update.message.reply_text(
            t("commands.add_city.usage", locale),
            parse_mode="HTML",
        )
        return
    if not name:
        await update.message.reply_text(
            t("commands.add_city.usage", locale),
            parse_mode="HTML",
        )
        return
    try:
        user = await gateway_client.get_or_create_user_by_telegram(telegram_id)
        await gateway_client.add_city(user.id, name, lat, lon)
        await update.message.reply_text(t("commands.add_city.success", locale).format(city=name))
    except Exception as e:
        logger.warning("Add city failed for user %s: %s", telegram_id, e)
        err_msg = str(e).lower()
        if "not found" in err_msg or "already exists" in err_msg or "duplicate" in err_msg:
            await update.message.reply_text(t("commands.add_city.exists", locale))
        else:
            await update.message.reply_text(t("commands.errors.generic", locale))
