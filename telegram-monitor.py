import logging
from telegram import Bot
from anyio import run, sleep
from json import dumps


telegram_token = "TELEGRAM_TOKEN"
chat_id = "YOUR_TELEGRAM_CHAT_ID"

telegram_administrators = ["Admin_1", "Admin_2", "Admin_3"]


async def get_current_admins(bot: Bot, chat_id: str) -> list[str | None]:
    admins = await bot.get_chat_administrators(chat_id)
    return [admin.user.username for admin in admins]


def log_admin_changes(chat_title: str, new_admins: set[str], removed_admins: set[str]) -> None:
    data = {
        "telegram_group": chat_title,
        "event_type": "Telegram admin changed",
        "telegram_admin": [],
        "source": "telegram-api",
    }

    if new_admins:
        data["event"] = "Telegram admin account added"
        data["telegram_admin"] = list(new_admins)
        data[
            "full_description"
        ] = f"Telegram admin account(s) {', '.join(new_admins)} were added to the Telegram group '{chat_title}'."

    if removed_admins:
        data["event"] = "Telegram admin account removed"
        data["telegram_admin"] = list(removed_admins)
        data[
            "full_description"
        ] = f"Telegram accounts {', '.join(removed_admins)} were removed from the Telegram group '{chat_title}'."
    with open("Telegram_monitoring.log", "a") as file:
        file.write(dumps(data))
        file.write("\n")


async def main():
    bot = Bot(telegram_token)
    chat = await bot.get_chat(chat_id)
    last_administrators = telegram_administrators

    while True:
        try:
            current_administrators = await get_current_admins(bot, chat_id)
            new_admins = set(current_administrators) - set(last_administrators)
            removed_admins = set(last_administrators) - set(current_administrators)

            if new_admins or removed_admins:
                log_admin_changes(chat.title, new_admins, removed_admins)

            last_administrators = current_administrators
            await sleep(2)
        except Exception as e:
            logging.error(f"Error during monitoring: {e}")

        await sleep(2)


if __name__ == "__main__":
    run(main)
