from flask import Flask, request, send_from_directory, send_file, session, redirect, render_template
import random, string
import os
import json, time

#初始化
app = Flask(__name__, template_folder='static')
app.config["DEBUG"] = True
# app.config['SECRET_KEY'] = os.urandom(24)
app.config['SECRET_KEY'] = 'howdoyouturnthison?'

#前端動態腳本
@app.route('/js/<path:path>')
def scriptfile(path):
    return send_from_directory('static/js', path)

#前端樣式表
@app.route('/css/<path:path>')
def stylefile(path):
    return send_from_directory('static/css', path)

#首頁
@app.route('/')
def home():
    return send_file('static/index.html')

#加入一個頻道
@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == "GET":
        return "wrong method"
    else:
        if request.form.get('create'):
            session['name'] = request.form.get('user')
            return redirect('/chat/'+chatIdGen(), code=302)
        elif request.form.get('join'):
            session['name'] = request.form.get('user')
            return redirect('/chat/'+request.form.get('chatid'), code=302)
        else:
            return "wrong arguments"

#隨機產生器，我應該給前端處理這個的
def chatIdGen():
    pre = string.ascii_letters
    pre += string.digits
    pre += "-_"
    return ''.join(random.choice(pre) for i in range(7))

@app.route('/chat/<chatid>')
def chatUI(chatid):
    if 'name' in session:
        return render_template('chat.html', chatId=chatid)
    else:
        return redirect('/', code=302)

# ex: {"chatid": "abcdef", "users": [{"name":"owo", "online": 1012313551, "wait": True}]}
channelStatus = []
# ex: {"chatid": "abcdef", "mid": 0, "content": "Hi there!", "from": "someone"}
lastChatMsg = []

#建立一個新頻道
def newChat(chatid):
    for i in channelStatus:
        if i['chatid'] == chatid:
            return i
    else:
        channelStatus.append({"chatid": chatid, "users": []})
        lastChatMsg.append({"chatid":chatid, "mid": 0, "content":""})
        return channelStatus[len(channelStatus)-1]

#訊息服務
def msgServ(channel):
    for i in lastChatMsg:
        if i["chatid"] == channel["chatid"]:
            return i

#更新狀態
def updateUserStaus(channel, userid):
    for i in channel["users"]:
        if i["name"] == userid:
            i["online"] = time.time()
            i["wait"] = True
            return i
    else:
        channel["users"].append({"name": userid, "online": time.time(), "wait": True})
        return channel["users"][len(channel["users"])-1]

#廣播
def broadcast(channel):
    for i in channel["users"]:
        i["wait"] = False

#線上使用者列表
def getOnlineUsers(channel):
    result = []
    for i in channel["users"]:
        if (time.time() - i["online"]) < 30:
            result.append(i["name"])
    return result

#新訊息
def newMsg(channel, msg, user):
    for i in lastChatMsg:
        if i["chatid"] == channel["chatid"]:
            i["content"] = msg
            i["from"] = user
            i['mid'] += 1

#紀錄
def msgLog(chatid, ip, name, content):
    ip = ip + " "*(15-len(ip))
    name = name + " "*(15-len(name))
    with open("logs/"+chatid+".txt", "a+", encoding="utf-8") as f:
        f.write(time.strftime("%Y/%m/%d %H:%M:%S") + " " + ip + " " + name + " " + content + "\n")

#廣播服務
@app.route('/api/<chatid>', methods=['POST'])
def api(chatid):
    data = request.get_json()
    channel = newChat(chatid)
    status = updateUserStaus(channel, session["name"])
    mid = msgServ(channel)["mid"]
    if data['status'] == 'join':
        broadcast(channel)
        return json.dumps({"online": getOnlineUsers(channel)})
    elif data["status"] == "send":
        msgLog(channel["chatid"], request.remote_addr, status["name"], data["message"])
        newMsg(channel ,data["message"], status["name"])
        broadcast(channel)
        return json.dumps({"online": getOnlineUsers(channel)})
    else:
        for i in range(25):
            time.sleep(1)
            if status['wait'] == False:
                if mid != msgServ(channel)["mid"]:
                    return json.dumps({"online": getOnlineUsers(channel), "message": {"from":msgServ(channel)["from"], "msg": msgServ(channel)["content"] }})
                return json.dumps({"online": getOnlineUsers(channel)})
        return json.dumps({"online": getOnlineUsers(channel)})

#紀錄查看
@app.route("/logs/<chatid>")
def loadLogs(chatid):
    try:
        return send_file("logs/"+chatid+".txt")
    except Exception as e:
        return "this chat not created yet"

if __name__ == "__main__":
    app.run('0.0.0.0', '8000', threaded=True)