import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import fake_useragent

# Замените токен и ID на свои
token = "7408551097:AAGh55_89v5Yaxnxk9QWEa0NOlz_Ng6uqYs"
MyID = "@Benwen4ik"
bot = telebot.TeleBot(token)

# Переменная для остановки парсинга
is_parsing = False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь команду в формате:\n/search <откуда> <куда> <дата> <время>")

@bot.message_handler(commands=['stop'])
def stop_parsing(message):
    global is_parsing
    is_parsing = False
    bot.reply_to(message, "Парсинг остановлен.")

@bot.message_handler(commands=['search'])
def search_tickets(message):
    global is_parsing
    is_parsing = True  # Устанавливаем флаг парсинга
    try:
        _, place1, place2, date, times = message.text.split()
        date = date.split(".")
        url = f"https://pass.rw.by/ru/route/?from={place1}&to={place2}&date={date[2]}-{date[1]}-{date[0]}"
        
        Parsing(url, times, message.chat.id)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

def Parsing(url, times, chat_id):
    agent = fake_useragent.UserAgent().random
    option = webdriver.FirefoxOptions()
    option.set_preference("dom.webdriver.enabled", False)
    option.set_preference("dom.webnotifications.enabled", False)
    option.set_preference("general.useragent.override", agent)
    option.add_argument('--headless')
    
    browser = webdriver.Firefox(options=option)
    
    while True:
        if not is_parsing:  # Проверяем флаг парсинга
            browser.quit()  # Закрываем браузер
            break

        try:
            browser.get(url)
            massiv_biletov = browser.find_elements(By.CLASS_NAME, "sch-table__row-wrap")
            MyTicket = check(massiv_biletov, times)
            
            if MyTicket:
                exist = MyTicket.find_element(By.CLASS_NAME, "cell-4")
                if exist.text != "Мест нет":
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    bot.send_message(chat_id, f"{current_time} - места появились: {MyTicket.text}")
                else:
                    time.sleep(55)
            else:
                time.sleep(25)
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            time.sleep(25)

def check(massive, times):
    for i in massive:
        time_i = i.find_element(By.CLASS_NAME, "train-from-time").text
        if time_i == times:
            return i

if __name__ == "__main__":
    bot.polling(none_stop=True)