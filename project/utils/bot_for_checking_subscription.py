from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from project.utils.logger import Logger

# Настройки
BOT_TOKEN = "8188370617:AAG2pEMtLhKnePAgwJPTxKGrb1lo_Fifn4s"
CHANNEL_ID = "-1003065443674"  # или ID канала: -1001234567890

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def check_user_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )

        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]

    except Exception as e:
        print(f"Ошибка: {e}")
        return False


async def send_to_channel(message_text: str):
    """Функция для отправки сообщения в канал"""
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message_text)
        return True
    except Exception as e:
        Logger.error(f"Ошибка отправки в канал: {e}")
        return False


async def main():
    """Основная функция"""
    print("Бот запускается...")

    # Проверяем подключение
    try:
        me = await bot.get_me()
        await send_to_channel("blablabla")
        print(f"Бот @{me.username} успешно подключен")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return

    # Запускаем polling
    try:
        await dp.start_polling(bot)

    except Exception as e:
        print(f"Ошибка polling: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())