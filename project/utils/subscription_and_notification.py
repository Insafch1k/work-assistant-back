import aiogram.exceptions
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ChatMemberStatus
import asyncio
from project.utils.logger import Logger
from project.config import settings
from project.utils.methods_for_datetime import format_any_datetime

BOT_TOKEN = settings.BOT_TOKEN
CHANNEL_ID_KAZAN = settings.CHANNEL_ID_KAZAN
CHANNEL_ID_CHELNY = settings.CHANNEL_ID_CHELNY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# В отдельный файл
def format_job_message_html(job_data):
    created_at = job_data.get('created_at', '')
    date = job_data.get('date', '')
    formatted_date_of_creation = format_any_datetime(str(created_at), with_hour=True)
    formatted_date_of_work = format_any_datetime(str(date), with_hour=False)
    # Создаем сообщение
    message = (
        f"<b>🔨 {job_data.get('title', 'Не указано')}</b>\n\n"
        f"<b>👤 Категория:</b> {job_data.get('wanted_job', 'Не указано')}\n"
        f"<b>🏙️ Город:</b> {job_data.get('city', 'Не указано')}\n"
        f"<b>📍 Адрес:</b> {job_data.get('address', 'Не указано')}\n"
        f"<b>💰 Зарплата:</b> {job_data.get('salary', 'Не указано')} руб.\n"
        f"<b>🕐 Время работы:</b> {job_data.get('time_start', '')} - {job_data.get('time_end', '')}\n"
        f"<b>☀️ Дата выхода на работу:</b> {formatted_date_of_work}\n"
        f"<b>❗ Возраст:</b> {job_data.get('age', 'Не указано')}\n"
        f"<b>🧑‍🎓 Опыт:</b> {job_data.get('xp', 'Не указано')}\n"
        f"<b>📃 Описание</b> {job_data.get('description', 'Не указано')}\n"
    )

    # Добавляем информацию о машине
    if job_data.get('car'):
        message += f"<b>🚗 Требуется автомобиль:</b> Да\n"
    if job_data.get('is_urgent'):
        message += f"<b>⚡ Срочное объявление:</b> Да\n"

    # Добавляем дату
    message += f"<b>📅 Опубликовано:</b> {formatted_date_of_creation}\n\n"

    message += f'<a href="https://t.me/PodrabotaiBot">Написать работодателю</a>'

    return message


async def check_user_subscription(tg_id: int, city) -> bool:

    temp_bot = Bot(token=settings.BOT_TOKEN)
    CHANNEL_ID = which_city_send_message(city)
    try:

        member = await temp_bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=tg_id
        )

        logger.info(f"Subscription status for user {tg_id}: {member.status}")

        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]

    except aiogram.exceptions.TelegramBadRequest as e:
        if "PARTICIPANT_ID_INVALID" in str(e):
            logger.warning(f"Telegram user {tg_id} is not member of channel {CHANNEL_ID} or account was deleted")
            return False
        elif "USER_ID_INVALID" in str(e):
            logger.warning(f"Invalid Telegram user ID: {tg_id}")
            return False
        elif "CHAT_NOT_FOUND" in str(e):
            logger.error(f"Channel {CHANNEL_ID} not found for city: {city}")
            return False
        else:
            logger.error(f"Telegram API error for user {tg_id}: {e}")
            return False

    except Exception as e:
        logger.error(f"Unexpected error checking subscription for user {tg_id}: {e}")
        return False

    finally:
        if temp_bot.session:
            await temp_bot.session.close()

# В отдельный файл
def which_city_send_message(city):
    city = city.lower().strip()
    if city == "казань":
        return CHANNEL_ID_KAZAN
    elif city == "набережные-челны":
        return CHANNEL_ID_CHELNY
    else:
        Logger.error(f"Неизвестный город: {city}")
        return None


async def send_to_channel(message_json):
    # Создаем НОВОГО бота для этого вызова
    temp_bot = Bot(token=settings.BOT_TOKEN)
    try:

        # web_app_button = InlineKeyboardButton(
        #     text="Посмотреть объявление",
        #     web_app=WebAppInfo(url="https://app.podrabot.ru/app/"),
        # )
        # keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])

        if not message_json.get("city"):
            Logger.error("Город не указан в message_json")
            return False

        channel_id = which_city_send_message(message_json["city"])
        if not channel_id:
            Logger.error(f"Не найден channel_id для города: {message_json['city']}")
            return False

        await temp_bot.send_message(
            chat_id=channel_id,
            text=format_job_message_html(message_json),
            parse_mode="HTML",
            disable_web_page_preview=True
            # reply_markup=keyboard
        )

        await temp_bot.session.close()
        return True

    except Exception as e:
        Logger.error(f"Ошибка отправки в канал: {e}")
        return False
    finally:
        await temp_bot.session.close()


async def send_notification(tg_id: int,text: str):
    try:
        temp_bot = Bot(token=settings.BOT_TOKEN)
        await temp_bot.send_message(
                chat_id=tg_id,
                text=text, parse_mode='HTML')
    except Exception as ex:
        Logger.error(f"Ошибка отправки уведомления в тг юзеру {tg_id}\n{ex}")
