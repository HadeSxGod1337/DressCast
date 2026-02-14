"""Start command handler."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram_bot.i18n import t


def main_menu_inline_markup(locale: str) -> InlineKeyboardMarkup:
    """Build inline keyboard for main menu (in message)."""
    keyboard = [
        [
            InlineKeyboardButton(t("buttons.cities", locale), callback_data="main:cities"),
            InlineKeyboardButton(t("buttons.weather", locale), callback_data="main:weather"),
            InlineKeyboardButton(t("buttons.dress", locale), callback_data="main:dress"),
        ],
        [
            InlineKeyboardButton(t("buttons.add_city", locale), callback_data="main:add_city"),
            InlineKeyboardButton(t("buttons.language", locale), callback_data="main:language"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    locale = (context.user_data or {}).get("locale", "en")
    await update.message.reply_text(
        t("commands.start.greeting", locale),
        reply_markup=main_menu_inline_markup(locale),
    )
