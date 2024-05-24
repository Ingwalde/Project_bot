import os
from dotenv import load_dotenv
import telebot
from telebot import types
import deezer
import lyricsgenius
client = deezer.Client()


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
genius = lyricsgenius.Genius(os.getenv("GENIUS"))

print(BOT_TOKEN)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot has been started")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('music')
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Press music to start finding:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'music':
        text = "Please, send name of music:"
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, music_handler)
    if message.text=='/start':
        send_welcome(message)

def music_handler(message):
    if message.text != 'music':
        if message.text!='/start':
            music = message.text
            get_music(music, message)
        else:
            send_welcome(message)
    else:
        text = "Please, send name of music:"
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, music_handler)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)

def get_music(music: str, message: types.Message):
    res = client.search(music)
    text = f"Song: {music} is finded"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    list_length = len(res)
    if isinstance(res, object) and (list_length !=0):
        max_num = min(list_length, 12)
        tracks_to_display = res[:max_num]
        tracks_as_dicts = []
        for track in tracks_to_display:
            track_dict = {
                'title': track.title,
                'id': track.id,
            }
            tracks_as_dicts.append(track_dict)
        print(tracks_as_dicts)
        for track in tracks_as_dicts:
            textA = f"{track['title']}"
            trackId = track['id']
            markup.add(types.InlineKeyboardButton(text=textA + " id: " + str(trackId)))

        sent_msg = bot.send_message(message.from_user.id, text, reply_markup=markup)
        bot.register_next_step_handler(sent_msg, get_somemusic)
    else:
        bot.send_message(message.from_user.id, "No results found. Please, try another name.")
        bot.register_next_step_handler_by_chat_id(message.chat.id, music_handler)

def get_somemusic(message):
    if message.text=='/start':
        send_welcome(message)
    else:
        if message.text=='/start':
            get_text_messages(message)
        else: 
            if message.text.find(' id: ')==-1:
                text='Send name of music:'
                sent_msg = bot.send_message(message.from_user.id, text)
                bot.register_next_step_handler(sent_msg, get_somemusic)
            music = message.text.split(' id: ')[0]
            trackId = message.text.split(' id: ')[1]
            res = client.get_track(trackId)
            duration = convert(res.duration)
            print(res)
            track_dict = {
                'title': res.title,
                'artist': res.artist,
                'album': res.album,
                'duration': duration,
                'link': res.link
            }
            text = f"{track_dict['title']}, {track_dict['artist']}, \n{track_dict['album']}, \nDuration: {track_dict['duration']}, \n\nLink: {track_dict['link']}"
            bot.send_message(message.from_user.id, text)
            song = genius.search_song(res.title)
            if song.lyrics != None:
                bot.send_message(message.from_user.id, song.lyrics)

            bot.send_message(message.from_user.id, "Search of lyrics is done")
            text = "Please, send name of another music:"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('music')
            markup.add(btn1)
            sent_msg = bot.send_message(message.from_user.id, text, reply_markup=markup)
            bot.register_next_step_handler(sent_msg, music_handler)
bot.infinity_polling()