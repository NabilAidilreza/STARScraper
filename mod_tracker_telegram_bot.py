import os
import telebot
from datetime import datetime
from ntu_hub import create_timetable_list, compile_mods, get_today, get_weekly, get_all_mods, combine_NTU_dict
from ntu_hub import generate_timeline, check_what_week_day, generate_ics_file
import requests
from sqlalchemy import Column, Integer, Unicode, String
from sqlalchemy.types import JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.mutable import MutableDict

# Telegram bot startup #
API_KEY = open("TELEGRAM_API_KEY.txt","rb").readline().decode("utf-8")
bot = telebot.TeleBot(API_KEY, parse_mode=None)

# Set up class for Users #
Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Unicode(40))
    first_name = Column(Unicode(40))
    last_name = Column(Unicode(40))
    start_date = Column(String(20))
    mod_dict = Column(MutableDict.as_mutable(JSON))

    def __init__(self, chat_id, first_name, last_name):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.start_date = ""
        self.mod_dict = {}

    # Getters / Setters #
    def getusername(self):
        return self.first_name + " " + self.last_name
    def get_chat_id(self):
        return self.chat_id
    def get_start_date(self):
        return self.start_date
    def get_mod_dict(self):
        return self.mod_dict
    def set_start_date(self,value):
        self.start_date = value
    def set_mod_dict(self,value):
        self.mod_dict = value


# Connect to db #
def get_connection():
    return create_engine('sqlite:///ntu_stars_bot_database.db', echo=False)
engine = get_connection()
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

### STARTING PROMPT ###
@bot.message_handler(commands=['start','help','commands'])
def start(message):
    # Connect to DB #
    db = Session()
    # Check if this is a new user #
    check_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    if check_user == None:
        curr_user = User(message.chat.id, message.from_user.first_name, message.from_user.last_name)
        db.add(curr_user)
        db.commit()
        bot.send_message(message.chat.id,"Welcome: {}".format(curr_user.getusername()))
    else:
        curr_user = check_user
        bot.send_message(message.chat.id,"Welcome back: {}".format(curr_user.getusername()))
    bot.send_message(message.chat.id, "------ NTU Stars Bot ------\n\
Main functions: Display mod info, check day/week schedules, generate calendar file."+\
"\n\nCommands:\n\
1. /checkmods\n\
2. /checktoday\n\
3. /checkweekly\n\
4. /checkweek ?\n\
5. /genicsfile\n\
6. /help | /start | /commands\n")
    db.close()
    # Check required data #
    if verify_empty_data_set(message):
        prepdata(message)
        send_sample_html(message)   
        
### INITIALIZATION PROMPTS ###
@bot.message_handler(commands=['prepdata'])
def prepdata(message):
    bot.send_message(message.chat.id, "If you are a returning user and would like to check another STARS file, pls send new start date and html.\n")
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
    db = Session()
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    curr_user.set_start_date(message.text)
    db.commit()
    db.close()
    bot.send_message(message.chat.id,"Start date received. This will be used to properly allign your schedule to real-time.")

### Function to extract STARS HTML ###
def checksubmissionofSTARS(message):
    # Check if proper HTML file is submitted #
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
    main_dir = os.path.dirname(os.path.abspath(data_file_name))
    temp = data_file_name.split(".")
    new_data_file_name = temp[0] + "_" + str(message.chat.id) + "." + temp[1]
    new_data_file_location = "submitted_htmls/" + new_data_file_name
    os.replace(main_dir+"/"+data_file_name, main_dir+"/"+new_data_file_location)
    db = Session()
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    data = create_timetable_list(new_data_file_location)
    data_dict = compile_mods(data,curr_user.get_start_date())
    data_timeline = generate_timeline(curr_user.get_start_date())
    final_dict = combine_NTU_dict(data_dict,data_timeline,new_data_file_name)
    curr_user.set_mod_dict(final_dict)
    db.commit()
    db.close()
    bot.send_message(message.chat.id,"Data verified. Ready for actions.")

### EVENT CHECKERS ###
def verify_empty_data_set(message):
    db = Session()
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    db.close()
    # Check if data is empty #
    if curr_user.get_mod_dict() == {}:
        return True
    else:
        return False

def verify_missing_start_date(message):
    db = Session()
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    db.close()
    # Check if start date is present #
    if curr_user.get_start_date() == "":
        return True
    else:
        return False

### ERROR CHECKERS ###
@bot.message_handler(func=verify_empty_data_set, content_types=['text'])
def handle_html_doc(message):
	bot.send_message(message.chat.id,"STARS not initialized yet!!!")

### HANDLERS ###
@bot.message_handler(commands=["checkmods"])
def check_mods(message):
    db = Session()
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    db.close()
    data_dict = curr_user.get_mod_dict()["mods"]
    curr_sem_mods = get_all_mods(data_dict)
    bot.send_message(message.chat.id,curr_sem_mods)

@bot.message_handler(commands=["checktoday"])
def check_today(message):
    db = Session()
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    db.close()
    data_dict = curr_user.get_mod_dict()["mods"]
    today_data = get_today(data_dict,datetime.today().strftime("%d/%m/%Y"))
    bot.send_message(message.chat.id,today_data)

@bot.message_handler(commands=['checkweek1', 'checkweek2', 'checkweek3', 'checkweek4', 'checkweek5', 'checkweek6', 'checkweek7', 'checkweek8', 'checkweek9', 'checkweek10', 'checkweek11', 'checkweek12', 'checkweek13'])
def check_forecast(message):
    db = Session()
    week_num = int(message.text.replace("/checkweek",""))
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    db.close()
    data_dict = curr_user.get_mod_dict()["mods"]
    weekly_data = get_weekly(data_dict,week_num)
    bot.send_message(message.chat.id,weekly_data)

@bot.message_handler(commands=["checkweekly"])
def check_weekly(message):
    db = Session()
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    db.close()
    full_dict = curr_user.get_mod_dict()
    data_dict = full_dict["mods"]
    data_timeline = full_dict["timeline"]
    today_date = datetime.today().strftime("%d/%m/%Y")
    week_day_num = check_what_week_day(data_timeline,today_date) # [a,b]
    if week_day_num == 0:
        bot.send_message(message.chat.id,"No events this week. Go enjoy yourself!")
    else:
        weekly_data = get_weekly(data_dict,week_day_num[0])
        bot.send_message(message.chat.id,weekly_data)

@bot.message_handler(commands=["genicsfile"])
def gen_ics_file(message):
    db = Session()
    curr_user = db.query(User).filter(User.chat_id == message.chat.id).first()
    db.close()
    file_name = generate_ics_file("submitted_htmls/"+curr_user.get_mod_dict()["file_name"],curr_user.get_start_date())
    doc = open("calendars/"+file_name, 'rb')
    bot.send_document(message.chat.id, doc)
    bot.send_message(message.chat.id, "Success!!! Click on the file to add to your chosen calendar app.")
    
### LISTENING... ###
bot.infinity_polling()
