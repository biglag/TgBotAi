import telebot
import openai
import requests
import os

# Токен для доступа к Telegram API
TELEGRAM_TOKEN = "5934304986:AAGYzUc8oaOa0Qpc2IKojs0nPdWCXTEnyFQ"

# Токен для доступа к OpenAI API
OPENAI_TOKEN = "your_openai_token"

# Токен для доступа к Midjourney API
MIDJOURNEY_TOKEN = "your_midjourney_token"

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Инициализация OpenAI API
openai.api_key = OPENAI_TOKEN

# Словарь для хранения количества сообщений, которые были отправлены пользователем более двух раз
messages_dict = {}

# Клавиатура с выбором нейросети
keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
button_chat_gpt = telebot.types.KeyboardButton("Chat GPT")
button_midjourney = telebot.types.KeyboardButton("Midjourney")
keyboard.add(button_chat_gpt, button_midjourney)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который может генерировать текст и изображения с помощью нейросетей. Выбери нейросеть, которую хочешь использовать:", reply_markup=keyboard)

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Получение количества сообщений, которые были отправлены пользователем более двух раз
    count = messages_dict.get(message.text, 0)

    # Если пользователь пытается отправить одно и то же сообщение более двух раз
    if count >= 2:
        bot.reply_to(message, "Пожалуйста, напиши что-то другое.")
        return

    # Увеличение количества сообщений, которые были отправлены пользователем более двух раз
    messages_dict[message.text] = count + 1

    # Если выбрана нейросеть Chat GPT
    if message.text == "Chat GPT":
        # Генерация ответа с помощью OpenAI API
        response = openai.Completion.create(
            engine="davinci",
            prompt=message.text,
            max_tokens=50
        )

        # Отправка ответа пользователю
        bot.reply_to(message, response.choices[0].text)
    # Если выбрана нейросеть Midjourney
    elif message.text == "Midjourney":
        # Отправка сообщения с просьбой прикрепить изображение
        bot.reply_to(message, "Пожалуйста, прикрепи изображение.")

# Обработчик сообщений с изображениями
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Загрузка изображения во временный файл
    file_info = bot.get_file(message.photo[-1].file_id)
    file = bot.download_file(file_info.file_path)
    with open("temp.jpg", "wb") as f:
        f.write(file)

    # Отправка запроса к Midjourney API для генерации изображения по описанию
    headers = {
        "Authorization": f"Bearer {MIDJOURNEY_TOKEN}"
    }
    data = {
        "description": "an image of a beach with palm trees and a sunset",
        "model": "image-generation",
        "tags": ["beach", "palm trees", "sunset"]
    }
    files = {
        "image": open("temp.jpg", "rb")
    }
    response = requests.post("https://api.midjourney.com/v1/models/image-generation/generate", headers=headers, data=data, files=files)

    # Если запрос выполнен успешно
    if response.ok:
        # Сохранение сгенерированного изображения в файл
        with open("generated.jpg", "wb") as f:
            f.write(response.content)

        # Отправка сгенерированного изображения пользователю
        with open("generated.jpg", "rb") as f:
            bot.send_photo(message.chat.id, f)
    # Если запрос выполнен с ошибкой
    else:
        bot.reply_to(message, "Произошла ошибка при генерации изображения.")