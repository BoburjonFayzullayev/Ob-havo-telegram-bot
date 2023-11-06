import json
import os
from datetime import datetime
from googletrans import Translator
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv, find_dotenv
import requests

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)
API = os.getenv('API')
mrk = types.ReplyKeyboardMarkup(resize_keyboard=True)
mrk.add('Ob havo malumotlari')


def translate_text(text, target_language='uz'):
    """
    Translate text to the target language using Google Translate.

    Args:
        text (str): The text to be translated.
        target_language (str): The target language code (e.g., 'en' for English).

    Returns:
        str: The translated text.
    """
    translator = Translator()

    try:
        translation = translator.translate(text, dest=target_language)
        translated_text = translation.text
        return translated_text
    except Exception as e:
        return str(e)
async def on_startup(_):
    print("Bot ishga tayyor")

def format24(time_str):
    # Create a datetime object to parse the time
    dt = datetime.strptime(time_str, '%I:%M %p')
    # Convert the time to 24-hour format as a string
    return dt.strftime('%H:%M')



@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):

    await message.answer("Salom botimizga xush kelibsiz", reply_markup=mrk)


@dp.message_handler(text='Ob havo malumotlari')
async def reply(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.InlineKeyboardButton('Toshkent'))
    markup.add(types.InlineKeyboardButton('Samarqand'))
    markup.add(types.InlineKeyboardButton('Buxoro'))
    markup.add(types.InlineKeyboardButton('Qashqadaryo'))
    markup.add(types.InlineKeyboardButton('Jizzax'))
    markup.add(types.InlineKeyboardButton('Sirdaryo'))
    markup.add(types.InlineKeyboardButton('Navoiy'))
    markup.add(types.InlineKeyboardButton('Xorazm'))
    markup.add(types.InlineKeyboardButton('Nukus'))
    markup.add(types.InlineKeyboardButton('Andijon'))
    markup.add(types.InlineKeyboardButton('Farg`ona'))
    markup.add(types.InlineKeyboardButton('Namangan'))
    await message.reply('Tumanlarni ob havo malumotlarini bilmoqchi bo`lsangiz. Tuman nomini kiriting.', reply_markup=markup)




@dp.message_handler()
async def replyy(message: types.Message):
    city = message.text.strip().lower()
    days = 10
    res = requests.get(f'http://api.weatherapi.com/v1/forecast.json?key={API}&q={city}&days={days}&alerts=yes')
    if res.status_code == 200:
        data = json.loads(res.text)
        forecast_days = data['forecast']['forecastday']
        temp = data["current"]["temp_c"]
        time = data["current"]["last_updated"]
        humidity = data['current']['humidity']
        pressure = data['current']['pressure_mb']
        image = data['current']['condition']['icon']
        sunrise = format24(data['forecast']['forecastday'][0]['astro']['sunrise'])
        sunset = format24(data['forecast']['forecastday'][0]['astro']['sunset'])

        foto = f'https:{image}'

        await message.reply(f'{city.capitalize()}ning ob havo ma`lumotlari\n'
                            f'Vaqt: {time}\n'
                            f'Havo xarorati {temp} °C \n'
                            f'Yog`ingarchilik: {humidity}% \n'
                            f'Bosim: {pressure} Pa\n'
                            f'Quyosh chiqishi: {sunrise}\n'
                            f'Quyosh botishi: {sunset}\n')
        await bot.send_photo(chat_id=message.chat.id,
                             photo=foto)

        for forecast_day in forecast_days[:days]:  # Limit the forecast to the specified number of days
            date = forecast_day['date']
            temp_max = forecast_day['day']['maxtemp_c']
            temp_min = forecast_day['day']['mintemp_c']
            maxwind_kph = forecast_day['day']['maxwind_kph']
            daily_chance_of_rain = forecast_day['day']['daily_chance_of_rain']
            sunrise = format24(forecast_day['astro']['sunrise'])
            sunset = format24(forecast_day['astro']['sunset'])
            translat = translate_text(forecast_day['day']['condition']['text'])
            image = forecast_day['day']['condition']['icon']
            foto = f'https:{image}'


            await message.reply(f'{city.capitalize()}ning {date} sanadagi ob havo ma`lumotlari\n'
                                f'Maksimal temperatura: {temp_max} °C\n'
                                f'Minimal temperatura: {temp_min} °C\n'
                                f'Maksimal shamol tezligi: {maxwind_kph} km\soat\n'
                                f'Yog`ingarchilik: {daily_chance_of_rain} %\n'
                                f'Quyosh chiqishi {sunrise}\n'
                                f'Quyosh botishi {sunset}\n'
                                f'Tavsif: {translat}'
                                )
            await bot.send_photo(chat_id=message.chat.id,
                                 photo=foto)
    elif res.status_code == 404:
        await message.reply('Notug`ri shahar manzili ko`rsatildi. Shahar nomini tug`ri kiriting')








if __name__ == "__main__":
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)