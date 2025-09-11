from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, WebAppInfo, InlineKeyboardMarkup, LoginUrl
import asyncio
from project.utils.logger import Logger
from project.config import settings

BOT_TOKEN = settings.BOT_TOKEN
CHANNEL_ID_KAZAN = settings.CHANNEL_ID_KAZAN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# В отдельный файл
def format_job_message(job_data):
    created_at = job_data.get('created_at', '')
    if created_at:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%d.%m.%Y в %H:%M")
        except:
            formatted_date = created_at
    else:
        formatted_date = "Не указано"

    # Создаем сообщение
    message = (
        f"<b>🏢 Новая вакансия!</b>\n\n"
        f"<b>📝 Должность:</b> {job_data.get('title', 'Не указано')}\n"
        f"<b>👤 Ищет:</b> {job_data.get('wanted_job', 'Не указано')}\n"
        f"<b>💰 Зарплата:</b> {job_data.get('salary', 'Не указано')} руб.\n"
        f"<b>🕐 Время работы:</b> {job_data.get('time_start', '')} - {job_data.get('time_end', '')}\n"
        f"<b>📍 Адрес:</b> {job_data.get('address', 'Не указано')}\n"
        f"<b>🏙️ Город:</b> {job_data.get('city', 'Не указано')}\n"
    )

    # Добавляем информацию о машине
    if job_data.get('car'):
        message += f"<b>🚗 Требуется автомобиль:</b> Да\n"

    # Добавляем дату
    message += f"<b>📅 Опубликовано:</b> {formatted_date}\n"

    return message

# async def check_user_subscription(user_id: int) -> bool:
#     try:
#         member = await bot.get_chat_member(
#             chat_id=CHANNEL_ID,
#             user_id=user_id
#         )
#
#         return member.status in [
#             ChatMemberStatus.MEMBER,
#             ChatMemberStatus.ADMINISTRATOR,
#             ChatMemberStatus.CREATOR
#         ]
#
#     except Exception as e:
#         print(f"Ошибка: {e}")
#         return False

# В отдельный файл
def which_city_send_message(city):
    city = city.lower().strip()
    if city == "казань":
        return settings.CHANNEL_ID_KAZAN
    elif city == "набережные-челны":
        return settings.CHANNEL_ID_CHELNY
    else:
        Logger.error(f"Неизвестный город: {city}")
        return None


async def send_to_channel(message_json):
    try:
        # Создаем НОВОГО бота для этого вызова
        temp_bot = Bot(token=settings.BOT_TOKEN)

        web_app_button = InlineKeyboardButton(
            text="Посмотреть объявление",
            web_app=WebAppInfo(url="https://app.podrabot.ru/app/"),
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])

        if not message_json.get("city"):
            Logger.error("Город не указан в message_json")
            return False

        channel_id = which_city_send_message(message_json["city"])
        if not channel_id:
            Logger.error(f"Не найден channel_id для города: {message_json['city']}")
            return False

        await temp_bot.send_message(
            chat_id=channel_id,
            text=format_job_message(message_json),
            parse_mode="HTML",
            # reply_markup=keyboard
        )

        await temp_bot.session.close()
        return True

    except Exception as e:
        Logger.error(f"Ошибка отправки в канал: {e}")
        return False



async def main():
    print("Бот запускается...")

    try:
        me = await bot.get_me()
        print(f"Бот @{me.username} успешно подключен")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return

    try:
        await dp.start_polling(bot)

    except Exception as e:
        print(f"Ошибка polling: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())