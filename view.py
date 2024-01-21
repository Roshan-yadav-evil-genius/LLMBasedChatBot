from flask import Flask, render_template,request,jsonify
from DBPipeline import DBInstance
from telepot import Bot
import os
from dotenv import load_dotenv



app = Flask(__name__)


@app.route("/")
def home(passeduserid=None):
    db = DBInstance()
    ids = db.getUserIds()
    users = []
    chat = []
    user = None
    for id in ids:
        name = db.get_username_by_userid(id)
        users.append({"id": id, "name": name})
    if ids:
        if passeduserid:
            chat = db.getChatHistoryByUserID(passeduserid)
            user = db.get_username_by_userid(passeduserid)
        else:
            chat = db.getChatHistoryByUserID(ids[0])
            user = db.get_username_by_userid(ids[0])
    print(chat)
    return render_template("home.html", users=users, chat=chat, user={"id": passeduserid if passeduserid else ids[0], "name": user})


@app.route("/userid/<int:id>")
def get_item(id):
    return home(id)


@app.route('/receive_message', methods=['POST'])
def receive_message():
    db=DBInstance()
    data = request.get_json()
    # print(request.js)

    # Extract values from JSON
    user_id = data.get('id')
    message = data.get('msg')
    print(f"Sending message for User ID {user_id}: {message}")

    db.insertChatHistory(user_id,db.get_username_by_userid(user_id),'assistant',message)
    Bot(os.environ["client_tele_bot_token"]).sendMessage(user_id,message)

    return jsonify({"status": "Message received successfully!"})


def StartChatServer():
    app.run(port=5000)

if __name__ == "__main__":
    app.run(port=5000)
