"""Handle inline callbacks: main menu, city list pagination, city selection, city actions (weather/dress)."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.handlers.cities import (
    city_actions_keyboard,
    send_city_list_page,
)
from telegram_bot.handlers.dress import get_dress_message
from telegram_bot.handlers.language import _language_keyboard
from telegram_bot.handlers.weather import get_weather_message
from telegram_bot.i18n import t

logger = logging.getLogger(__name__)


async def _handle_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    action: str,
    gateway_client,
) -> bool:
    """Handle main:xxx. Returns True if handled."""
    query = update.callback_query
    if not query or not query.data:
        return False
    locale = (context.user_data or {}).get("locale", "en")
    await query.answer()
    if action == "cities":
        await send_city_list_page(
            update, context, gateway_client, page=0, intent="cities", from_callback=True
        )
        return True
    if action == "weather":
        await send_city_list_page(
            update, context, gateway_client, page=0, intent="weather", from_callback=True
        )
        return True
    if action == "dress":
        await send_city_list_page(
            update, context, gateway_client, page=0, intent="dress", from_callback=True
        )
        return True
    if action == "add_city":
        await query.edit_message_text(
            t("commands.add_city.usage", locale),
            parse_mode="HTML",
        )
        return True
    if action == "language":
        await query.edit_message_text(
            t("commands.language.choose", locale),
            reply_markup=_language_keyboard(),
        )
        return True
    return False


async def _handle_cities_page(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int,
    intent: str,
    gateway_client,
) -> bool:
    """Handle cities:p:P:intent — show city list page."""
    await update.callback_query.answer()
    await send_city_list_page(
        update, context, gateway_client, page=page, intent=intent, from_callback=True
    )
    return True


async def _handle_city_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    city_index: int,
    page: int,
    intent: str,
    gateway_client,
) -> bool:
    """Handle city_sel:i:P:intent — show actions for city or directly weather/dress."""
    query = update.callback_query
    await query.answer()
    cities_list = (context.user_data or {}).get("cities") or []
    if city_index < 0 or city_index >= len(cities_list):
        locale = (context.user_data or {}).get("locale", "en")
        await query.edit_message_text(t("commands.errors.city_not_found", locale))
        return True
    city_name = cities_list[city_index]
    locale = (context.user_data or {}).get("locale", "en")
    telegram_id = str(getattr(update.effective_user, "id", None) or "")
    if not telegram_id:
        await query.edit_message_text(t("commands.errors.generic", locale))
        return True

    if intent == "weather":
        try:
            user = await gateway_client.get_or_create_user_by_telegram(telegram_id)
            text = await get_weather_message(gateway_client, user.id, city_name, locale)
            await query.edit_message_text(text=text)
        except Exception as e:
            logger.warning(
                "City callback weather failed telegram_id=%s city=%s: %s", telegram_id, city_name, e
            )
            await query.edit_message_text(text=t("commands.errors.generic", locale))
        return True
    if intent == "dress":
        try:
            user = await gateway_client.get_or_create_user_by_telegram(telegram_id)
            text = await get_dress_message(gateway_client, user.id, city_name, locale)
            await query.edit_message_text(text=text)
        except Exception as e:
            logger.warning(
                "City callback dress failed telegram_id=%s city=%s: %s", telegram_id, city_name, e
            )
            await query.edit_message_text(text=t("commands.errors.generic", locale))
        return True

    # intent == "cities" — show Weather / What to wear / Back
    text = t("commands.cities.what_to_do", locale).format(city=city_name)
    keyboard = city_actions_keyboard(city_index, page, intent, locale)
    await query.edit_message_text(text=text, reply_markup=keyboard)
    return True


async def _handle_city_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    city_index: int,
    action: str,
    gateway_client,
) -> bool:
    """Handle city_act:i:w or city_act:i:d — show weather or dress for city."""
    query = update.callback_query
    await query.answer()
    cities_list = (context.user_data or {}).get("cities") or []
    if city_index < 0 or city_index >= len(cities_list):
        locale = (context.user_data or {}).get("locale", "en")
        await query.edit_message_text(t("commands.errors.city_not_found", locale))
        return True
    city_name = cities_list[city_index]
    locale = (context.user_data or {}).get("locale", "en")
    telegram_id = str(getattr(update.effective_user, "id", None) or "")
    if not telegram_id:
        await query.edit_message_text(t("commands.errors.generic", locale))
        return True
    try:
        user = await gateway_client.get_or_create_user_by_telegram(telegram_id)
        if action == "w":
            text = await get_weather_message(gateway_client, user.id, city_name, locale)
        else:
            text = await get_dress_message(gateway_client, user.id, city_name, locale)
        await query.edit_message_text(text=text)
    except Exception as e:
        logger.warning("City action failed telegram_id=%s city=%s: %s", telegram_id, city_name, e)
        await query.edit_message_text(text=t("commands.errors.generic", locale))
    return True


async def city_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    gateway_client,
) -> None:
    """Route callback_data: main:*, cities:p:P:intent, city_sel:i:P:intent, city_act:i:w/d, w:i, d:i."""
    query = update.callback_query
    if not query or not query.data:
        return
    data = query.data

    # main:action
    if data.startswith("main:"):
        action = data.split(":", 1)[1]
        if await _handle_main_menu(update, context, action, gateway_client):
            return

    # cities:p:page:intent
    if data.startswith("cities:p:"):
        parts = data.split(":")
        if len(parts) >= 4:
            try:
                page = int(parts[2])
                intent = parts[3]
                if await _handle_cities_page(update, context, page, intent, gateway_client):
                    return
            except ValueError:
                pass

    # city_sel:index:page:intent
    if data.startswith("city_sel:"):
        parts = data.split(":")
        if len(parts) >= 4:
            try:
                city_index = int(parts[1])
                page = int(parts[2])
                intent = parts[3]
                if await _handle_city_selected(
                    update, context, city_index, page, intent, gateway_client
                ):
                    return
            except ValueError:
                pass

    # city_act:index:w or city_act:index:d
    if data.startswith("city_act:"):
        parts = data.split(":")
        if len(parts) >= 3:
            try:
                city_index = int(parts[1])
                act = parts[2]
                if act in ("w", "d") and await _handle_city_action(
                    update, context, city_index, act, gateway_client
                ):
                    return
            except ValueError:
                pass

    # Legacy w:index / d:index (direct weather/dress by index)
    parts = data.split(":", 1)
    if len(parts) != 2:
        return
    kind, index_str = parts[0], parts[1]
    if kind not in ("w", "d"):
        return
    try:
        index = int(index_str)
    except ValueError:
        return
    await query.answer()
    cities_list = (context.user_data or {}).get("cities") or []
    if index < 0 or index >= len(cities_list):
        locale = (context.user_data or {}).get("locale", "en")
        await query.edit_message_text(t("commands.errors.city_not_found", locale))
        return
    city_name = cities_list[index]
    locale = (context.user_data or {}).get("locale", "en")
    telegram_id = str(getattr(update.effective_user, "id", None) or "")
    if not telegram_id:
        await query.edit_message_text(t("commands.errors.generic", locale))
        return
    try:
        user = await gateway_client.get_or_create_user_by_telegram(telegram_id)
        if kind == "w":
            text = await get_weather_message(gateway_client, user.id, city_name, locale)
        else:
            text = await get_dress_message(gateway_client, user.id, city_name, locale)
        await query.edit_message_text(text=text)
    except Exception as e:
        logger.warning("City callback failed telegram_id=%s city=%s: %s", telegram_id, city_name, e)
        await query.edit_message_text(text=t("commands.errors.generic", locale))
