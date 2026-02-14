"""Bot menu commands per locale for set_my_commands."""

from telegram import BotCommand

from telegram_bot.i18n import t


def get_menu_commands(locale: str = "en") -> list[BotCommand]:
    """Return list of BotCommand for the given locale."""
    return [
        BotCommand("start", t("menu.start", locale)),
        BotCommand("cities", t("menu.cities", locale)),
        BotCommand("weather", t("menu.weather", locale)),
        BotCommand("dress", t("menu.dress", locale)),
        BotCommand("add_city", t("menu.add_city", locale)),
        BotCommand("language", t("menu.language", locale)),
    ]
