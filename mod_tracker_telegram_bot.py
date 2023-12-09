import telebot
import emoji
from datetime import datetime
from hub import create_timetable_list, compile_mods, get_today, get_weekly, get_all_mods
from hub import generate_timeline, check_what_week_day, generate_ics_file
import requests

API_KEY = open("TELEGRAM_API_KEY.txt","rb").readline().decode("utf-8")
bot = telebot.TeleBot(API_KEY)

### TO IMPLEMENT DB ###
data = []
data_dict = {}
data_timeline = []
data_start_date = ""
data_file_name = ""

### STARTING PROMPT ###
@bot.message_handler(commands=['start','help','commands'])
def start(message):
    bot.send_message(message.chat.id, "------ ModTrackerBot ------\n\
This bot is designed to track your NTU modules and schedules for quick references" + \
                 emoji.emojize(':smiling_face_with_smiling_eyes:')+\
"\n\nCommands:\n\
1. /checkmods\n\
2. /checktoday\n\
3. /checkweekly\n\
4. /checkweek ?\n\
5. /genicsfile\n\
6. /help | /start | /commands\n")
    if verify_empty_data_set(message):
        prepdata(message)
        send_sample_html(message)
        
### INITIALIZATION PROMPTS ###
@bot.message_handler(commands=['prepdata'])
def prepdata(message):
    bot.send_message(message.chat.id, "Provide your semester start date FIRST. (based on the STARS you will be sending)(i.e 14/08/2023)")
    bot.send_message(message.chat.id, "Then provide your STARs for initialisation.\n(HTML format)(rename to STARS_YourName.html)")

def send_sample_html(message):
    doc = open('samples\STARS_SAMPLE.html', 'rb')
    bot.send_document(message.chat.id, doc)
    bot.send_message(message.chat.id, "Required sample of STARS Planner.")

### Function to extract start date ###
def checksubmissionofSTARTDATE(message):
    try:
        temp = message.text.split("/")
    except:
        return False
    if len(temp) == 3 and len(temp[-1]) == 4:
        return True
    return False

@bot.message_handler(func=checksubmissionofSTARTDATE,content_types=['text'])
def extractstartdate(message):
    global data_start_date
    start_date = message.text
    data_start_date = start_date
    bot.send_message(message.chat.id,"Start date received. This will be used to properly allign your schedule to real-time.")

### Function to extract STARS HTML ###
def checksubmissionofSTARS(message):
    try:
        temp = message.document.file_name.split(".")
    except:
        return False
    if "html" in temp[-1] and "STARS" in temp[0]:
        return True
    else:
        return False
    
@bot.message_handler(func=checksubmissionofSTARS,content_types=['document'])
def filteroutStars(message):
    global data, data_dict, data_timeline, data_start_date, data_file_name
    if verify_missing_start_date(message):
        bot.send_message(message.chat.id,"Start date empty. Unable to proceed.")
        return prepdata(message)
    bot.send_message(message.chat.id,"File received...")
    bot.send_message(message.chat.id,"Processing data...")
    data_file_id = message.document.file_id
    file_path = bot.get_file(data_file_id).file_path
    URL = "https://api.telegram.org/file/bot" + API_KEY + "/" + file_path
    response = requests.get(URL)
    data_file_name = message.document.file_name
    open(data_file_name, "wb").write(response.content)
    data = create_timetable_list(data_file_name)
    data_dict = compile_mods(data)
    data_timeline = generate_timeline(data_start_date)
    bot.send_message(message.chat.id,"Data verified. Ready for actions.")

### EVENT CHECKERS ###
def verify_empty_data_set(message):
    if data == [] and data_dict == {}:
        return True
    else:
        return False

def verify_missing_start_date(message):
    if data_start_date == "":
        return True
    else:
        return False

def verify_forecast(message):
    checkdataset = verify_empty_data_set(message)
    if not checkdataset:
        temp = message.text.split()
        if len(temp)==2:
            return True
        else:
            return False 
    else:
        return False

### ERROR CHECKERS ###
@bot.message_handler(func=verify_empty_data_set, content_types=['text'])
def handle_html_doc(message):
	bot.send_message(message.chat.id,"STARS not initialized yet!!!")

### HANDLERS ###
@bot.message_handler(commands=["checkmods"])
def check_mods(message):
    curr_sem_mods = get_all_mods(data_dict)
    bot.send_message(message.chat.id,curr_sem_mods)

@bot.message_handler(commands=["checktoday"])
def check_today(message):
    today_data = get_today(data_dict,datetime.today().strftime("%d-%m-%Y"))
    bot.send_message(message.chat.id,today_data)

@bot.message_handler(func=verify_forecast,commands=["checkweek"])
def check_forecast(message):
    week_num = message.text.split()[1]
    weekly_data = get_weekly(data_dict,week_num)
    bot.send_message(message.chat.id,weekly_data)

@bot.message_handler(commands=["checkweekly"])
def check_weekly(message):
    today_date = datetime.today().strftime("%d/%m/%Y")
    week_day_num = check_what_week_day(data_timeline,today_date) # [a,b]
    if week_day_num == 0:
        bot.send_message(message.chat.id,"No events this week. Go enjoy yourself!")
    else:
        weekly_data = get_weekly(data_dict,week_day_num[0])
        bot.send_message(message.chat.id,weekly_data)

@bot.message_handler(commands=["genicsfile"])
def gen_ics_file(message):
    file_name = generate_ics_file(data_file_name,data_start_date)
    doc = open("calendars/"+file_name, 'rb')
    bot.send_document(message.chat.id, doc)
    bot.send_message(message.chat.id, "Success!!! Click on the file to add to your chosen calendar app.")
    
### LISTENING... ###
bot.infinity_polling()
