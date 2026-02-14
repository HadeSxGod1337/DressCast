"""Language selection: /language command and callback for buttons."""

from telegram import BotCommandScopeChat, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram_bot.i18n import t
from telegram_bot.menu_commands import get_menu_commands


def _get_locale(context: ContextTypes.DEFAULT_TYPE) -> str:
    return (context.user_data or {}).get("locale", "en")


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection keyboard."""
    locale = _get_locale(context)
    await update.message.reply_text(
        t("commands.language.choose", locale),
        reply_markup=_language_keyboard(),
    )


def _language_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(t("buttons.lang_en", "en"), callback_data="lang:en"),
            InlineKeyboardButton(t("buttons.lang_ru", "ru"), callback_data="lang:ru"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language button: show picker (lang:menu) or set locale (lang:en/ru)."""
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.startswith("lang:"):
        return
    part = query.data.split(":")[-1]
    if part == "menu":
        locale = _get_locale(context)
        await query.edit_message_text(
            t("commands.language.choose", locale),
            reply_markup=_language_keyboard(),
        )
        return
    lang = part if part in ("en", "ru") else "en"
    if context.user_data is None:
        context.user_data = {}
    context.user_data["locale"] = lang
    chat_id = query.message.chat.id if query.message else None
    if chat_id is not None and context.bot:
        await context.bot.set_my_commands(
            get_menu_commands(lang),
            scope=BotCommandScopeChat(chat_id=chat_id),
        )
    await query.edit_message_text(text=t("commands.language.set", lang))
