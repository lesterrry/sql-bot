from telegram import __version__ as TG_VER
# python-telegram-bot==13.15
import logging
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes
import os.path
import datetime
from dateutil.relativedelta import relativedelta
import subprocess
import requests

#
# ЗДЕСЬ НИКНЕЙМЫ ТЕХ, КОМУ МОЖНО ТРОГАТЬ БОТ
#
ALLOWED = ["andy", "ben", "jack"]
TOKEN = "TOKEN"
CHANNEL_ID = "1234"

logging.basicConfig(
    filename=f"{os.path.dirname(os.path.abspath(__file__))}/log.txt",
    filemode='a',
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

def log(msg:str) -> None:
    logging.info(msg)
    requests.post(url=f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHANNEL_ID, "text": msg})

def get_keyboard(categories: object, step: int, key: str = None) -> list:
    ret = [[]]
    index = 0
    if step == 0:
        for i in list(categories):
            ret[0].append(InlineKeyboardButton(i, callback_data=f"0_{i}"))
        return ret
    if step == 1:
        for i in range(0, len(categories[key])):
            ret[index].append(InlineKeyboardButton(list(categories[key][i])[0], callback_data=f"1_{key}_{list(categories[key][i].values())[0]}"))
            if i != 0 and i % 3 == 0:
                ret.append([])
                index += 1
        return ret

def parse_categories(for_allowlists: list) -> object:
    ret = {}
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/cat.txt") as f:
        for line in f:
            entries = line.rstrip().split(":")
            #  if (`allowed` has elements and (current category is not in it or current category is in `denied`)) or current category in in `denied`
            if (len(for_allowlists[0]) > 0 and (entries[2] not in for_allowlists[0] or entries[2] in for_allowlists[1])) or entries[2] in for_allowlists[1]:
                continue
            if entries[0] in ret:
                ret[entries[0]].append({ entries[1] : entries[2] })
            else:
                ret[entries[0]] = [{ entries[1] : entries[2] }]
    return ret

def parse_allowlists(for_username: str) -> list:
    ret = [[], []]
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/allow.txt") as f:
        for line in f:
            entries = line.rstrip().split(":")
            if for_username == entries[0]:
                ret[0] = entries[1].split(",")
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/deny.txt") as f:
        for line in f:
            entries = line.rstrip().split(":")
            if for_username == entries[0]:
                ret[1] = entries[1].split(",")
    return ret

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.username is None or user.username not in ALLOWED:
        return
    update.message.reply_text("Чтобы начать, отправьте команду /request")

def text(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.username is None or user.username not in ALLOWED:
        return
    user = update.effective_user
    update.message.reply_text("Чтобы начать, отправьте команду /request")

def request(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.username is None or user.username not in ALLOWED:
        return
    keyboard = get_keyboard(parse_categories(parse_allowlists(user.username)), 0)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Выберите категорию", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.username is None or user.username not in ALLOWED:
        return
    query = update.callback_query
    query.answer()
    data = query.data.split("_");
    if data[0] == "0":
        keyboard = get_keyboard(parse_categories(parse_allowlists(user.username)), 1, data[1])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Выберите подкатегорию", reply_markup=reply_markup)
    elif data[0] == "1":
        #
        # ЗДЕСЬ НАСТРАИВАЮТСЯ ДАТЫ НАЧАЛА
        #
        now = datetime.datetime.now()
        now_s_p1 = (now + relativedelta(months=1)).strftime("%Y-%m-01")
        now_s = (now).strftime("%Y-%m-01")
        now_s_m1 = (now - relativedelta(months=1)).strftime("%Y-%m-01")
        now_s_m2 = (now - relativedelta(months=2)).strftime("%Y-%m-01")
        now_s_m3 = (now - relativedelta(months=3)).strftime("%Y-%m-01")
        keyboard = [
            [ InlineKeyboardButton(now_s_p1, callback_data=f"2_{data[1]}_{data[2]}_{now_s_p1}") ],
            [ InlineKeyboardButton(now_s, callback_data=f"2_{data[1]}_{data[2]}_{now_s}") ],
            [ InlineKeyboardButton(now_s_m1, callback_data=f"2_{data[1]}_{data[2]}_{now_s_m1}") ],
            [ InlineKeyboardButton(now_s_m2, callback_data=f"2_{data[1]}_{data[2]}_{now_s_m2}") ],
            [ InlineKeyboardButton(now_s_m3, callback_data=f"2_{data[1]}_{data[2]}_{now_s_m3}") ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Выберите дату начала", reply_markup=reply_markup)
    elif data[0] == "2":
        #
        # ЗДЕСЬ НАСТРАИВАЮТСЯ ДАТЫ КОНЦА
        #
        now = datetime.datetime.strptime(data[3], "%Y-%m-%d")
        now_s_p2 = (now + relativedelta(months=2)).strftime("%Y-%m-01")
        now_s_p1 = (now + relativedelta(months=1)).strftime("%Y-%m-01")
        now_s = (now).strftime("%Y-%m-01")
        keyboard = [
            [ InlineKeyboardButton(now_s_p2, callback_data=f"3_{data[1]}_{data[2]}_{data[3]}_{now_s_p2}") ],
            [ InlineKeyboardButton(now_s_p1, callback_data=f"3_{data[1]}_{data[2]}_{data[3]}_{now_s_p1}") ],
            [ InlineKeyboardButton(now_s, callback_data=f"3_{data[1]}_{data[2]}_{data[3]}_{now_s}") ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Выберите дату конца", reply_markup=reply_markup)
    elif data[0] == "3":
        success_msg = f"Запуск процедуры...\nКатегория: {data[1]}\nКлиент: {data[2]}\nДата начала: {data[3]}\nДата конца: {data[4]}"
        #
        # ЗДЕСЬ НАСТРАИВАЮТСЯ СКРИПТЫ ПО КАТЕГОРИЯМ
        # РАЗБИВКА ПЕРЕМЕННОЙ `data`:
        #  data[0] — системное значение
        #  data[1] — текстовое значение категории (К1/К2...)
        #  data[2] — номер клиента
        #  data[3] — дата начала
        #  data[4] — дата конца
        # Помимо этих данных в процедуру еще нужно передать str(user.id), чтобы бот из процедуры писал людям
        #
        if data[1] == "К1":
            query.edit_message_text(text=success_msg)
            # subprocess.Popen(["python", f"{os.path.dirname(os.path.abspath(__file__))}/new_pycharm.py", data[2], data[3], str(user.id)])
        elif data[1] == "К2":
            query.edit_message_text(text=success_msg)
            # subprocess.Popen(["python", f"{os.path.dirname(os.path.abspath(__file__))}/new_pycharm.py", data[2], data[3], str(user.id)])
        elif data[1] == "К3":
            query.edit_message_text(text=success_msg)
            # subprocess.Popen(["python", f"{os.path.dirname(os.path.abspath(__file__))}/new_pycharm.py", data[2], data[3], str(user.id)])
        else:
            query.edit_message_text(text=f"Категория {data[1]} неизвестна")
            return
        log(f"{user.username} запустил команду, \n  Категория: {data[1]}\n  Клиент: {data[2]}\n  Дата начала: {data[3]}\n  Дата конца: {data[4]}");

def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("request", request))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text))

    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    