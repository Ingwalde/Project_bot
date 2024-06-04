import os # Імпортуємо модуль os для взаємодії з операційною системою
from dotenv import load_dotenv # Імпортуємо функцію для завантаження змінних оточення
import telebot # Імпортуємо модуль для роботи з Telegram Bot API
from telebot import types # Імпортуємо типи з модуля telebot для створення клавіатур    
import deezer # Імпортуємо модуль для роботи з Deezer API
import lyricsgenius # Імпортуємо модуль для роботи з Genius API
client = deezer.Client() # Створюємо клієнт для взаємодії з Deezer API

load_dotenv()  # Завантажуємо змінні оточення з файлу .env

BOT_TOKEN = os.getenv('BOT_TOKEN')  # Отримуємо токен бота з змінних оточення
genius = lyricsgenius.Genius(os.getenv("GENIUS"))  # Створюємо клієнт для взаємодії з Genius API

print(BOT_TOKEN)  # Виводимо токен бота в консоль
bot = telebot.TeleBot(BOT_TOKEN)  # Створюємо екземпляр бота

@bot.message_handler(commands=['start'])  # Декоратор для обробки команди /start
def send_welcome(message):  # Функція відправки привітання
    bot.reply_to(message, "Bot has been started")  # Відповідаємо на повідомлення про старт бота
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Створюємо клавіатуру
    btn1 = types.KeyboardButton('music')  # Створюємо кнопку
    markup.add(btn1)  # Додаємо кнопку до клавіатури
    bot.send_message(message.from_user.id, "Press music to start finding:", reply_markup=markup)  # Відправляємо клавіатуру користувачу

@bot.message_handler(content_types=['text'])  # Декоратор для обробки текстових повідомлень
def get_text_messages(message):  # Функція обробки текстових повідомлень
    if message.text == 'music':  # Якщо текст повідомлення - 'music'
        text = "Please, send name of music:"  # Встановлюємо текст
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")  # Відправляємо повідомлення
        bot.register_next_step_handler(sent_msg, music_handler)  # Реєструємо наступний крок
    if message.text=='/start':  # Якщо текст повідомлення - '/start'
        send_welcome(message)  # Викликаємо функцію відправки привітання

def music_handler(message):  # Функція обробки повідомлень про музику
    if message.text != 'music':  # Якщо текст повідомлення не 'music'
        if message.text!='/start':  # Якщо текст повідомлення не '/start'
            music = message.text  # Зберігаємо текст повідомлення як назву музики
            get_music(music, message)  # Викликаємо функцію пошуку музики
        else:
            send_welcome(message)  # Інакше відправляємо привітання
    else:
        text = "Please, send name of music:"  # Встановлюємо текст
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")  # Відправляємо повідомлення
        bot.register_next_step_handler(sent_msg, music_handler)  # Реєструємо наступний крок

def convert(seconds):  # Функція конвертації секунд у хвилини та секунди
    seconds = seconds % (24 * 3600)  
    seconds %= 3600  
    minutes = seconds // 60  
    seconds %= 60  
    return "%02d:%02d" % (minutes, seconds)  # Повертаємо форматований час

def get_music(music: str, message: types.Message):  # Функція пошуку музики
    res = client.search(music)  # Виконуємо пошук музики через Deezer API
    text = f"Song: {music} is finded"  # Встановлюємо текст
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Створюємо клавіатуру
    list_length = len(res)  # Визначаємо довжину списку результатів
    if isinstance(res, object) and (list_length !=0):  # Якщо результат - об'єкт і не пустий
        max_num = min(list_length, 12)  # Визначаємо максимальну кількість результатів для відображення
        tracks_to_display = res[:max_num]  # Обираємо перші результати для відображення
        tracks_as_dicts = []  # Створюємо список для зберігання інформації про треки
        for track in tracks_to_display:  # Для кожного треку в списку
            track_dict = {  # Створюємо словник з інформацією про трек
                'title': track.title,
                'id': track.id,
            }
            tracks_as_dicts.append(track_dict)  # Додаємо словник до списку
        print(tracks_as_dicts)  # Виводимо список треків в консоль
        for track in tracks_as_dicts:  # Для кожного треку в списку
            textA = f"{track['title']}"  # Встановлюємо текст
            trackId = track['id']  # Зберігаємо ID треку
            markup.add(types.InlineKeyboardButton(text=textA + " id: " + str(trackId)))  # Додаємо кнопку з ID треку до клавіатури

        sent_msg = bot.send_message(message.from_user.id, text, reply_markup=markup)  # Відправляємо клавіатуру користувачу
        bot.register_next_step_handler(sent_msg, get_somemusic)  # Реєструємо наступний крок
    else:
        bot.send_message(message.from_user.id, "No results found. Please, try another name.")  # Відправляємо повідомлення, якщо результатів не знайдено
        bot.register_next_step_handler_by_chat_id(message.chat.id, music_handler) # Реєструємо наступний крок
        
def get_somemusic(message):  # Функція для отримання тексту музики
    if message.text=='/start':  # Якщо текст повідомлення - '/start'
        send_welcome(message)  # Викликаємо функцію відправки привітання
    else:
        if message.text=='/start':  # Якщо текст повідомлення знову - '/start'
            get_text_messages(message)  # Викликаємо функцію обробки текстових повідомлень
        else: 
            if message.text.find(' id: ')==-1:  # Якщо в тексті повідомлення немає ' id: '
                text='Send name of music:'  # Встановлюємо текст
                sent_msg = bot.send_message(message.from_user.id, text)  # Відправляємо повідомлення
                bot.register_next_step_handler(sent_msg, get_somemusic)  # Реєструємо наступний крок
            music = message.text.split(' id: ')[0]  # Отримуємо назву музики з повідомлення
            trackId = message.text.split(' id: ')[1]  # Отримуємо ID треку з повідомлення
            res = client.get_track(trackId)  # Отримуємо трек за ID через Deezer API
            duration = convert(res.duration)  # Конвертуємо тривалість треку
            print(res)  # Виводимо інформацію про трек в консоль
            track_dict = {  # Створюємо словник з інформацією про трек
                'title': res.title,
                'artist': res.artist,
                'album': res.album,
                'duration': duration,
                'link': res.link
            }
            text = f"{track_dict['title']}, {track_dict['artist']}, \n{track_dict['album']}, \nDuration: {track_dict['duration']}, \n\nLink: {track_dict['link']}"  # Формуємо текст з інформацією про трек
            bot.send_message(message.from_user.id, text)  # Відправляємо інформацію користувачу
            song = genius.search_song(res.title)  # Шукаємо текст пісні через Genius API
            if song.lyrics != None:  # Якщо текст пісні знайдено
                bot.send_message(message.from_user.id, song.lyrics)  # Відправляємо текст пісні користувачу

            bot.send_message(message.from_user.id, "Search of lyrics is done")  # Повідомляємо користувача про завершення пошуку тексту
            text = "Please, send name of another music:"  # Встановлюємо текст
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Створюємо клавіатуру
            btn1 = types.KeyboardButton('music')  # Створюємо кнопку
            markup.add(btn1)  # Додаємо кнопку до клавіатури
            sent_msg = bot.send_message(message.from_user.id, text, reply_markup=markup)  # Відправляємо клавіатуру користувачу
            bot.register_next_step_handler(sent_msg, music_handler)  # Реєструємо наступний крок
bot.infinity_polling()  # Запускаємо бота на нескінченне опитування
