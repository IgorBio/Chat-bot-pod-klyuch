import datetime
import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from yookassa import Configuration, Payment
import config

# Инициализация бота и настройка YooKassa
bot = telebot.TeleBot(config.TOKEN)
Configuration.account_id = config.SHOP_ID
Configuration.secret_key = config.SHOP_API_TOKEN

# Настройка доступа к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("tg-bot.json", scope)
client = gspread.authorize(creds)
sheet = client.open("гугл_табличка").sheet1

# Функция для создания платежа
def create_payment(value, description):
    payment = Payment.create({
        "amount": {
            "value": value,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://web.telegram.org/"
        },
        "capture": True,
        "description": description
    })
    # Возвращаем ссылку для подтверждения оплаты
    return json.loads(payment.json())['confirmation']['confirmation_url']

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем клавиатуру с кнопками
    markup = types.InlineKeyboardMarkup()
    # Добавляем кнопку с ссылкой на Яндекс Карты
    markup.add(types.InlineKeyboardButton("Ленина 1, перейти на Яндекс карты", url="https://yandex.ru/maps/?text=Ленина 1"))
    # Создание ссылки на оплату 2 рублей
    payment_url = create_payment("2.00", "Оплата 2 рубля")
    markup.add(types.InlineKeyboardButton("Оплатить 2 рубля", url=payment_url))
    # Добавляем кнопки для отправки изображения и получения значения из Google Sheets
    markup.add(types.InlineKeyboardButton("Картинка img1.jpg", callback_data="send_image"))
    markup.add(types.InlineKeyboardButton("Получить значение A2 гугл таблички", callback_data="get_google_sheet_value"))
    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "send_image":
        # Отправка изображения
        photo = open('./media/img1.jpg', 'rb')
        bot.send_photo(call.message.chat.id, photo)
    elif call.data == "get_google_sheet_value":
        # Получение значения ячейки A2 из Google Sheets
        cell_value = sheet.cell(2, 1).value
        bot.send_message(call.message.chat.id, f"Значение A2: {cell_value}")

# Обработка текстового ввода даты
@bot.message_handler(func=lambda message: True)
def handle_date_input(message):
    input_date = message.text
    
    # проверяю формат даты на соответствие дд.мм.гг
    try:
        date_format = "%d.%m.%y"
        datetime.datetime.strptime(input_date, date_format)
    except ValueError:
        # Сообщение об ошибке, если дата неверна
        bot.reply_to(message, "Дата введена неверно")
        return

    # обращаемся к гугл табличке
    values = sheet.col_values(2)  # Получаем все значения столбца B
    next_row = len(values) + 1 # Определяем следующую строку для записи
    sheet.update_cell(next_row, 2, input_date) # Обновляем ячейку с новой датой
    bot.reply_to(message, "Дата верна") # Подтверждаем пользователю, что дата верна

if __name__ == '__main__':
    bot.polling(none_stop=True)