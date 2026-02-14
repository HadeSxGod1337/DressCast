"""Cities command: list user cities with pagination, then choose action per city."""

import logging
from math import ceil

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram_bot.i18n import t

logger = logging.getLogger(__name__)

CITIES_PER_PAGE = 6


def _city_list_page_keyboard(
    city_names: list[str],
    page: int,
    intent: str,
    locale: str,
) -> InlineKeyboardMarkup:
    """Build inline keyboard: city name buttons for one page + Prev/Next."""
    total_pages = max(1, ceil(len(city_names) / CITIES_PER_PAGE))
    start = page * CITIES_PER_PAGE
    end = min(start + CITIES_PER_PAGE, len(city_names))
    rows = []
    for i in range(start, end):
        name = city_names[i]
        # Telegram button text limit 64 bytes; city name can be long
        label = name[:30] + "…" if len(name) > 30 else name
        rows.append(
            [
                InlineKeyboardButton(
                    label,
                    callback_data=f"city_sel:{i}:{page}:{intent}",
                )
            ]
        )
    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(
                t("buttons.prev", locale),
                callback_data=f"cities:p:{page - 1}:{intent}",
            )
        )
    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton(
                t("buttons.next", locale),
                callback_data=f"cities:p:{page + 1}:{intent}",
            )
        )
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(rows)


def city_list_page_text(city_names: list[str], page: int, intent: str, locale: str) -> str:
    """Message text for city list (with optional intent hint)."""
    total_pages = max(1, ceil(len(city_names) / CITIES_PER_PAGE))
    if intent == "weather":
        base = t("commands.cities.choose_weather", locale)
    elif intent == "dress":
        base = t("commands.cities.choose_dress", locale)
    else:
        base = t("commands.cities.choose", locale)
    if total_pages > 1:
        base += "\n\n" + t("commands.cities.page", locale).format(n=page + 1, total=total_pages)
    return base


def city_actions_keyboard(
    city_index: int, page: int, intent: str, locale: str
) -> InlineKeyboardMarkup:
    """After city selected: Weather, What to wear, Back to list."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("buttons.weather", locale), callback_data=f"city_act:{city_index}:w"
                ),
                InlineKeyboardButton(
                    t("buttons.dress", locale), callback_data=f"city_act:{city_index}:d"
                ),
            ],
            [
                InlineKeyboardButton(
                    t("buttons.back_to_list", locale),
                    callback_data=f"cities:p:{page}:{intent}",
                ),
            ],
        ]
    )


async def send_city_list_page(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    gateway_client,
    page: int,
    intent: str,
    *,
    from_callback: bool,
) -> None:
    """Load cities, build page, then reply or edit message."""
    locale = (context.user_data or {}).get("locale", "en")
    telegram_id = str(getattr(update.effective_user, "id", None) or "")
    if not telegram_id:
        msg = t("commands.errors.generic", locale)
        if from_callback and update.callback_query:
            await update.callback_query.edit_message_text(msg)
        elif update.message:
            await update.message.reply_text(msg)
        return
    try:
        user = await gateway_client.get_or_create_user_by_telegram(telegram_id)
        r = await gateway_client.list_cities(user.id)
        city_names = [c.name for c in r.cities]
        if not city_names:
            empty_msg = t("commands.cities.empty", locale)
            if from_callback and update.callback_query:
                await update.callback_query.edit_message_text(empty_msg)
            elif update.message:
                await update.message.reply_text(empty_msg)
            return
        if context.user_data is None:
            context.user_data = {}
        context.user_data["cities"] = city_names
        total_pages = max(1, ceil(len(city_names) / CITIES_PER_PAGE))
        page = max(0, min(page, total_pages - 1))
        text = city_list_page_text(city_names, page, intent, locale)
        keyboard = _city_list_page_keyboard(city_names, page, intent, locale)
        if from_callback and update.callback_query:
            await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.warning("Cities list failed for telegram_id=%s: %s", telegram_id, e, exc_info=True)
        msg = t("commands.errors.generic", locale)
        if from_callback and update.callback_query:
            await update.callback_query.edit_message_text(msg)
        elif update.message:
            await update.message.reply_text(msg)


async def cities(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    gateway_client,
) -> None:
    """Show first page of city list; user then picks city, then action (weather/dress)."""
    await send_city_list_page(
        update, context, gateway_client, page=0, intent="cities", from_callback=False
    )
