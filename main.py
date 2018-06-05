import telebot
import constants
import json
import time
import random
from emoji import emojize
import xml.etree.ElementTree as ET
import urllib.request as urllib2
import requests
from multiprocessing import Process
bot = telebot.TeleBot(constants.token)


def log(message):
    print("\n ----------------")
    from datetime import datetime
    print(datetime.now())
    print("Message from {0} {1}. ( id = {2}) \n Text: {3}".format(message.from_user.first_name,
                                                                  message.from_user.last_name,
                                                                  str(message.from_user.id), message.text))


def insert_to_queue(sendTime, id, message):
    sendTemp = str(sendTime)
    sendData = { 'id':id, 'message':message}
    cur_data = json.load(open('Queue.json'))
    if sendTemp not in cur_data:
        cur_data[sendTemp] = [sendData]
    else:
        cur_data[sendTemp].append(sendData)
    write_json(cur_data, 'Queue.json')





def send_notification():
    cur_time = str(int(time.time()))
    cur_data = json.load(open('Queue.json'))
    if cur_time not in cur_data:
        return
    else:
        for each in cur_data[cur_time]:
            bot.send_message(each['id'], each['message'])   #Sending Message to the user
        del cur_data[cur_time]
    write_json(cur_data, 'Queue.json')


def convertToSec(freq, weekDay, startTime):
    cur_time = time.localtime()
    givenDay = constants.dayInIdx[weekDay]

    extraSec = cur_time.tm_hour * 3600 + cur_time.tm_min * 60 + cur_time.tm_sec
    ans = int(time.time()) - extraSec;
    wDay = cur_time.tm_wday
    if givenDay >= wDay:
        ans = ans + ((givenDay - wDay) * constants.secInDay)
    else:
        ans = ans + ((givenDay - wDay) + 7) * constants.secInDay

    ans = ans + startTime + (freq * constants.secInWeek)
    return ans



#---------------------------------------------------------------

@bot.message_handler(commands=['start', 'help', 'finish'])
def start_function(message):
    log(message)
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/add_several','/add_single','/end')
    user_markup.row('/music_for_study', '/math','/reset')
    user_markup.row('/my_timeTable', '/add_notification', '/generate_homework')
    bot.send_message(message.from_user.id, "Hello my friend! My name is TeenHelper and I will help you" 
" to organize your time for studying, to solve some maths problems and do my best to help you.\n" 
"Now you can build your timetable by the help of \n/add_several\n/add_single\n/add_notification functions \n" 
"/math function will help you to solve maths problems!\n/my_timeTable gives an access to your personal timetable\n"
"/music_for_study gives a link to music for study" , reply_markup=user_markup)



@bot.message_handler(commands=['end'])
def end_function(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    bot.send_message(message.from_user.id, "GoodBye, my dear friend! ""\n"
     "Thank you for choosing our service! ""\n"
     "We wish you safe and confortable flight, and unforgetable travel! ")


@bot.message_handler(commands=['add_several'])
def add_several_function(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/finish', '/end','/math')
    user_markup.row('/my_timeTable', '/start')
    msg = bot.send_message(message.from_user.id,
"Now please add your courses/subjects as it is show below\nex:" 
"Monday-Physics-15:00-16:00 \n Click FINISH to end", reply_markup=user_markup)
    bot.register_next_step_handler(msg, initial_case_step)

@bot.message_handler(commands=['add_single'])
def add_single_function(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/add_several','/add_single', '/end')
    user_markup.row('/my_timeTable','/math', '/start')
    msg = bot.send_message(message.from_user.id, "Now please add your courses/subjects as it is show below\n" 
"ex: Monday-Physics-15:00-16:00", reply_markup=user_markup)
    bot.register_next_step_handler(msg, add_helper)

@bot.message_handler(commands=['reset'])
def reset_function(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', '/end')
    user_markup.row('/my_timeTable')
    reset_helper(message.from_user.id)
    msg = bot.send_message(message.from_user.id, "Reset Done", reply_markup=user_markup)

@bot.message_handler(commands=['music_for_study'])
def music_for_study_function(message):
    url='https://www.googleapis.com/youtube/v3/activities?part=snippet,contentDetails&channelId=UC68KnvCZ-nJzmmuSu_tKASA&key=AIzaSyDakZSyasvaXJL_OfM_DgAD_fvWvQ0Gw6k&maxResults=50'
    req = requests.get(url)
    req_dict = req.json()
    id = req_dict['items'][random.randint(0,49)]['contentDetails']['upload']['videoId']
    ans='https://www.youtube.com/watch?v='+id
    bot.send_message(message.from_user.id, ans)

def time_converter(seconds):
    res = ""
    hour = int(seconds / 3600)
    minute = int((seconds - 3600 * hour) / 60)
    if minute<10 and minute>=0:
        minute = '0' + str(minute)
    res += str(hour) + ":" + str(minute)
    return res

@bot.message_handler(commands=['my_timeTable'])
def my_timeTable_function(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/add_several','/add_single', '/end')
    cur_data = json.load(open('cur_data.json'))
    current_id = str(message.from_user.id)
    res = ""
    r1="\n\tMonday" + "\n\t-------"
    r2="\n\tTuesday" + "\n\t-------"
    r3="\n\tWednesday" + "\n\t-------"
    r4="\n\tThursday" + "\n\t-------"
    r5="\n\tFriday" + "\n\t-------"
    r6="\n\tSaturday" + "\n\t-------"
    r7="\n\tSunday" + "\n\t-------"
    if current_id in cur_data:
        for day in cur_data[current_id]:
            if(day == "Monday" or day=="monday"):
                r1 = "\n\tMonday"
                for time in cur_data[current_id][day]:
                    if(len(time)==0):
                        r1 += "\n\tMonday" + "\n\t-------"
                        break
                    t2 = time_converter(cur_data[current_id][day][time]["endTime"])

                    a = cur_data[current_id][day][time]["activity"]
                    time = int(time)
                    t = time_converter(time)
                    r1 += "\n" + t + "-" + t2 + " - " + a
                continue


            if(day == "Tuesday" or day=="tuesday"):
                r2 = "\n\tTuesday"
                for time in cur_data[current_id][day]:
                    if(len(time)==0):
                        r2 += "\n\tTuesday" + "\n\t-------"
                        break;
                    t2 = time_converter(cur_data[current_id][day][time]["endTime"])

                    a = cur_data[current_id][day][time]["activity"]
                    time = int(time)
                    t = time_converter(time)
                    r2 += "\n" + t + "-" + t2 + " - " + a
                continue


            if (day == "Wednesday" or day == "wednesday"):
                r3 = "\n\tWednesday"
                for time in cur_data[current_id][day]:
                    if (len(time) == 0):
                        r3 += "\n\tWednesday" + "\n\t-------"
                        break
                    t2 = time_converter(cur_data[current_id][day][time]["endTime"])

                    a = cur_data[current_id][day][time]["activity"]
                    time = int(time)
                    t = time_converter(time)
                    r3 += "\n" + t + "-" + t2 + " - " + a
                continue



            if (day == "Thursday" or day == "thursday"):
                r4 = "\n\tThursday"
                for time in cur_data[current_id][day]:
                    if (len(time) == 0):
                        r4 += "\n\tThursday" + "\n\t-------"
                        break
                    t2 = time_converter(cur_data[current_id][day][time]["endTime"])

                    a = cur_data[current_id][day][time]["activity"]
                    time = int(time)
                    t = time_converter(time)
                    r4 += "\n" + t + "-" + t2 + " - " + a
                continue

            if (day == "Friday" or day == "friday"):
                r5 = "\n\tFriday"
                for time in cur_data[current_id][day]:
                    if (len(time) == 0):
                        r5 += "\n\tFriday" + "\n\t-------"
                        break
                    t2 = time_converter(cur_data[current_id][day][time]["endTime"])

                    a = cur_data[current_id][day][time]["activity"]
                    time = int(time)
                    t = time_converter(time)
                    r5 += "\n" + t + "-" + t2 + " - " + a
                continue

            if (day == "Saturday" or day == "saturday"):
                r6 = "\n\tSaturday"
                for time in cur_data[current_id][day]:
                    if (len(time) == 0):
                        r6 += "\n\tSaturday" + "\n\t-------"
                        break
                    t2 = time_converter(cur_data[current_id][day][time]["endTime"])

                    a = cur_data[current_id][day][time]["activity"]
                    time = int(time)
                    t = time_converter(time)
                    r6 += "\n" + t + "-" + t2 + " - " + a
                continue

            if (day == "Sunday" or day == "sunday"):
                r7 = "\n\tSunday"
                for time in cur_data[current_id][day]:
                    if (len(time) == 0):
                        r7 += "\n\tSunday" + "\n\t-------"
                        break
                    t2 = time_converter(cur_data[current_id][day][time]["endTime"])

                    a = cur_data[current_id][day][time]["activity"]
                    time = int(time)
                    t = time_converter(time)
                    r7 += "\n" + t + "-" + t2 + " - " + a
                continue

        res += r1 +r2 +r3+r4+r5+r6+r7

    bot.send_message(message.from_user.id, res, reply_markup=user_markup)


#-----
@bot.message_handler(commands=['math'])
def math_function(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/Integrate', '/Differentiate', '/Solve_Equation')
    user_markup.row('/start','/music_for_study','/end')
    sendtext = "In this section you can /Integrate, /Differentiate or /Solve_Equation of any types.\nNow, please choose on of the options below!"
    msg = bot.send_message(message.from_user.id, sendtext, reply_markup=user_markup)


@bot.message_handler(commands=['Integrate'])
def Integrate_function(message):
    msg=bot.send_message(message.from_user.id,"Please send me your equation that will be Integrated!\n" 
"ex. tanx+x^3-(x^2+6)/4x")
    bot.register_next_step_handler(msg, makeInt)

def makeInt(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    m = message.text
    m = m.replace("+", "%2B%0A")
    url='http://api.wolframalpha.com/v2/query?appid=WG443A-36HJ76H6H9&input=integrate('+m+')'
    req = requests.get(url)
    val=ET.XML(req.content)
    b = False
    a = ""
    try:
        ans = val[0][0][1].text.split('=')
        url_im = val[1][0][0].get('src')
        urllib2.urlretrieve(url_im,'url_image.jpg')
        img = open('url_image.jpg','rb')
        bot.send_chat_action(message.from_user.id,'upload_photo')
        bot.send_photo(message.from_user.id,img)
        img.close()
        a = ans[1]
    except:
        b = True
    if(b):
        a = "invalid_input"


    msg = bot.send_message(message.from_user.id, a)


@bot.message_handler(commands=['Differentiate'])
def Differentiate_function(message):
    msg=bot.send_message(message.from_user.id,
"Please send me your equation that will be Differentiated!\n" 
"ex. cosx+20x^5-6x^3")
    bot.register_next_step_handler(msg, makeDiff)
def makeDiff(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/Integrate', '/Differentiate', '/music_for_study')
    user_markup.row('/start', '/Solve_Equation', '/end')

    m = message.text
    m=m.replace("+", "%2B%0A")
    url = 'http://api.wolframalpha.com/v2/query?appid=WG443A-36HJ76H6H9&input=differentiate(' + m + ')'
    req = requests.get(url)
    val = ET.XML(req.content)
    a=""
    b = False
    try:
        ans = val[0][0][1].text.split('=')
        url_im = val[1][0][0].get('src')
        urllib2.urlretrieve(url_im, 'url_image.jpg')
        img = open('url_image.jpg', 'rb')
        bot.send_chat_action(message.from_user.id, 'upload_photo')
        bot.send_photo(message.from_user.id, img)
        img.close()
        a = ans[1]
    except:
        b = True
    if(b):
        a = "Invalid input"
    msg = bot.send_message(message.from_user.id, a, reply_markup=user_markup)
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/Integrate', '/Differentiate')
    user_markup.row('/start', '/Solve_Equation', '/end')


@bot.message_handler(commands=['Solve_Equation'])
def Solve_Equation_function(message):

    msg = bot.send_message(message.from_user.id, "Please send me your equation of any type that will be solved!\n" 
"ex. x^5+5x^4-14x^3+10x^2+3x-30=0")
    bot.register_next_step_handler(msg, solveEq)
def solveEq(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    m = message.text
    m = m.replace("+", "%2B%0A")
    m = m.replace("=", "%3D%0A")
    url = 'http://api.wolframalpha.com/v2/query?appid=WG443A-36HJ76H6H9&input=solve+' + m
    req = requests.get(url)
    val = ET.XML(req.content)
    ans = " "
    if(len(val)<2):
        return
    for each in val[1]:
        try:
            if each[1].text != None:
                ans += each[1].text + " ; ";
        except:
            print("")

    try:
        url_im = val[2][0][0].get('src')
        urllib2.urlretrieve(url_im, 'url_image.jpg')
        img = open('url_image.jpg', 'rb')
        bot.send_chat_action(message.from_user.id, 'upload_photo')
        bot.send_photo(message.from_user.id, img)
        img.close()
    except:
        print("dddd")
    t = ans
    tem = t.split()
    if tem[1] is "(irreducible)" or tem[1]=="(irreducible)":
        print("aaaaa")
        y = tem[0].split("/")
        k1 = float(y[0])
        k2 = float(y[1])

        sum = k1/k2
        ans = str(sum)
    msg = bot.send_message(message.from_user.id, ans)


#--------

def write_json(data, filename='cur_data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.close()

def add_helper(message):
    print(message)
    checker = True

    if len(message.text.split("-")) == 4:
        weekDay, activity, startTime, endTime = message.text.split("-")
        checker = False

    if (checker == False):
        weekDay = "".join(weekDay.split())
        startTime = "".join(startTime.split())
        endTime = "".join(endTime.split())
        eH, eM = endTime.split(":")
        endT = int(eH)*3600 + int(eM)*60
        sH, sM = startTime.split(":")
        startT = int(sH)*3600 + int(sM)*60

        store(str(message.from_user.id), weekDay, activity, startT, endT)
    else:
        bot.send_message(message.from_user.id, constants.tryagain_message)

def reset_helper( id ):
    cur_data = json.load(open('cur_data.json'))
    if str(id) in cur_data:
        del cur_data[str(id)]
    write_json(cur_data, 'cur_data.json')

def store(id, weekDay, activity, s, e):
    #data = {message.from_user.id: {weekDay: {startT: {"endTime": endT, "activity": activity}}}}
    cur_data = json.load(open('cur_data.json'))
    if len(cur_data)==0:
        cur_data = {id: {weekDay: {s: {"endTime": e, "activity": activity}}}}
        print("huuuh")
    else:
        if id not in cur_data:
            cur_data[id] = {weekDay: {s: {"endTime": e, "activity": activity}}}
        else:
            if weekDay not in cur_data[id]:
                cur_data[id][weekDay] = {s: {"endTime": e, "activity": activity}}
            else:
                temp = []
                for startTime in cur_data[id][weekDay]:
                    startTemp = startTime
                    startTime = int(startTime)
                    if (s<startTime and e<=startTime) or (s>=cur_data[id][weekDay][startTemp]["endTime"] and e>cur_data[id][weekDay][startTemp]["endTime"] ):
                        continue
                    else:
                        temp.append(startTemp)

                for each in temp:
                    del cur_data[id][weekDay][each]

                cur_data[id][weekDay][s] = {"endTime": e, "activity": activity}
    for each in range(0,3):
        insert_to_queue(convertToSec(each, weekDay, s), int(id), "You have " + activity + " after 20 minutes")
    write_json(cur_data)
    bot.send_message(id, "Your request is recorded")


def initial_case_step(message):
    log(message)
    m = message
    t1 = m.text.split("-")
    t1[0] = "".join(t1[0].split())
    bot.send_chat_action(message.from_user.id, 'typing')
    answer=""
    if message.text == "/start":
        start_function(message)
        return
    elif message.text == "/end":
        end_function(message)
        return
    elif  message.text == "/add_single":
        add_single_function(message)
    elif  message.text == "/reset":
        reset_function(message)
    elif  message.text == "/music_for_study":
        music_for_study_function(message)
    elif  message.text == "/add_several":
        add_several_function(message)
    elif  message.text == "/math":
        math_function(message)
    elif  message.text == "/my_timeTable":
        my_timeTable_function(message)
    elif message.text == "/add_notification":
        add_notification_function(message)
    elif  message.text == "/finish":
        start_function(message)
    elif message.text == "Hello" or message.text == "Привет" or message.text == "Пока" or message.text == "Bye":
        answer = message.text
    elif len(t1) == 4 and (t1[0]=="Monday" or t1[0]=="monday" or t1[0]=="Tuesday" or t1[0]=="tuesday" or t1[0]=="Wednesday" or t1[0]=="wednesday" or t1[0]=="Thursday" or t1[0]=="thursday" or
                                          t1[0] == "Friday" or t1[0] == "friday" or t1[0] == "Saturday" or t1[0] == "saturday" or t1[0] == "Sunday" or t1[0] == "sunday"):
        add_helper(message)
        print("ssss")
        add_several_function(message)

    elif len(t1) < 4 or len(t1) > 4:
        bot.send_message(message.from_user.id, constants.tryagain_message)
    else:
        bot.send_message(message.from_user.id, constants.tryagain_message)


#-----------------------

@bot.message_handler(commands=['add_notification'])
def add_notification_function(message):
    msg = bot.send_message(message.from_user.id, "Enter the day - time and message to show, Ex: Monday-09:00- Wake Up!")
    bot.register_next_step_handler(msg, notification_helper)


def notification_helper(message):
    print("Hello!")
    textList = message.text.split("-")
    if(len(textList) < 3):
        bot.send_message(message.from_user.id, constants.error_message)
        return
    else:
        clock = textList[1].split(':')
        if(len(clock) != 2):
            bot.send_message(message.from_user.id, constants.error_message)
            return
        dayTime = int(clock[0])*3600 + int(clock[1])*60
        textMessage = "Notification: ";
        for each in range(2, len(textList)):
            textMessage += textList[each]
    insert_to_queue(convertToSec(0, textList[0], dayTime), message.from_user.id, textMessage)
    bot.send_message(message.from_user.id, "The Notification is Successfully added!")


def insert_cur_data(id, weekDay, cur_data, average):
    if weekDay in cur_data[id]:
        for each in cur_data[id][weekDay]:
            subject = cur_data[id][weekDay][each]["activity"]
            sublist = subject.split(' ')
            if sublist[len(sublist) - 1] == "Homework":
                continue
            for i in range(1, 6):
                newDay = getNewWeek(weekDay, i)
                stdDev = average
                if newDay in cur_data[id]:
                    stdDev = abs(len(cur_data[id][newDay]) - average)
                if stdDev < 2:
                    if newDay not in cur_data[id]:
                        cur_data[id][newDay] = {}
                    diff = 60*20
                    endDate = 9*3600
                    for each in cur_data[id][newDay]:
                        endDate = cur_data[id][newDay][each]["endTime"]
                    print(endDate)
                    if endDate + diff > 82800:
                        continue
                    cur_data[id][newDay][endDate+diff] = {"endTime":endDate + diff + 2700, "activity": (subject + " Homework") }
                    break





def getNewWeek(weekDay, x):
    idx = constants.dayInIdx[weekDay] - x
    if idx < 0:
        idx += 7
    return constants.idxInDay[idx]

def getAverage(cur_data, id):
    sum = 0
    for each in cur_data[id]:
        sum += len(cur_data[id][each])
    return int((sum*2)/7)

@bot.message_handler(commands=['generate_homework'])
def addTimeforHomework(message):
    cur_data = json.load(open('cur_data.json'))
    id = str(message.from_user.id)
    if id not in cur_data:
        return

    for eachDay in cur_data[id]:
        temp = []
        for eachTime in cur_data[id][eachDay]:
            strlist = cur_data[id][eachDay][eachTime]['activity'].split(" ")
            if strlist[len(strlist)-1] == "Homework":
                temp.append(eachTime)

        for each in temp:
            del cur_data[id][eachDay][each]

    average = getAverage(cur_data, id)

    for weekDay in constants.idxInDay:
        if weekDay in cur_data[id]:
            insert_cur_data(id, weekDay, cur_data, average)
    write_json(cur_data)
    bot.send_message(message.from_user.id, "The Time for doing homework is generated successfully!")



def polling_function(n):
    print("No")
    bot.polling(none_stop=True)



if __name__ == '__main__':
    p1 = Process(target=polling_function, name="Poll", args=(10,))
    p1.start()
    while 1:
        time.sleep(0.2)
        #p1.terminate()
        send_notification()


