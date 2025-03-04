import requests
from linebot import LineBotApi, WebhookHandler
from linebot.models import *
from flask import Flask, request

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = 'JqWb+rUi9IgDDUl8reBVeullXw24+XpiwaZ+GvmG0EeJexrjGfeQREnFbycPhkM6G1KxX0F00f6b6jRzgllmEltErl6tM2NpURMYlRnAyZD3TxreoMYUuy0h971ZyVEZ09wd3E+HxIkLXcdFu8fU+AdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'bd7a05f10673581455d69031e6781a43'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

PREDICTION_API_URL = "https://e2-t7wz.onrender.com/predict"

user_data = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text

    if message_text.lower() == "prediction":
        user_data[user_id] = {} 
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Let's start predicting! Please provide the following details.")
        )
        ask_bill_length(event)
    
    elif user_id in user_data:
        if "bill_length_mm" not in user_data[user_id]:
            user_data[user_id]["bill_length_mm"] = message_text
            ask_bill_depth(event)
        elif "bill_depth_mm" not in user_data[user_id]:
            user_data[user_id]["bill_depth_mm"] = message_text
            ask_flipper_length(event)
        elif "flipper_length_mm" not in user_data[user_id]:
            user_data[user_id]["flipper_length_mm"] = message_text
            ask_body_mass(event)
        elif "body_mass_g" not in user_data[user_id]:
            user_data[user_id]["body_mass_g"] = message_text
            ask_sex(event)
        elif "sex" not in user_data[user_id]:
            user_data[user_id]["sex"] = message_text
            ask_island(event)
        elif "island" not in user_data[user_id]:
            user_data[user_id]["island"] = message_text
            confirm_data(event)
        elif "confirm" not in user_data[user_id]:
            if message_text.lower() in ["yes", "confirm"]:
                send_prediction(event, user_id)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Let's start over. Type 'Prediction' to begin again.")
                )


def ask_bill_length(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="What's the bill length (in mm)?")
    )


def ask_bill_depth(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="What's the bill depth (in mm)?")
    )


def ask_flipper_length(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="What's the flipper length (in mm)?")
    )


def ask_body_mass(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="What's the body mass (in g)?")
    )


def ask_sex(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="What's the sex of the penguin? (Male/Female)")
    )


def ask_island(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Which island is the penguin from? (Biscoe, Dream, or Torgersen)")
    )


def confirm_data(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text="Please confirm your data: \n" +
                 f"Bill Length: {user_data[event.source.user_id]['bill_length_mm']} mm\n" +
                 f"Bill Depth: {user_data[event.source.user_id]['bill_depth_mm']} mm\n" +
                 f"Flipper Length: {user_data[event.source.user_id]['flipper_length_mm']} mm\n" +
                 f"Body Mass: {user_data[event.source.user_id]['body_mass_g']} g\n" +
                 f"Sex: {user_data[event.source.user_id]['sex']}\n" +
                 f"Island: {user_data[event.source.user_id]['island']}\n\n" +
                 "Is this correct? Type 'Yes' to confirm or 'No' to restart."
        )
    )


def send_prediction(event, user_id):
    data = {
        "bill_length_mm": float(user_data[user_id]["bill_length_mm"]),
        "bill_depth_mm": float(user_data[user_id]["bill_depth_mm"]),
        "flipper_length_mm": float(user_data[user_id]["flipper_length_mm"]),
        "body_mass_g": float(user_data[user_id]["body_mass_g"]),
        "sex": user_data[user_id]["sex"],
        "island": user_data[user_id]["island"]
    }

    response = requests.post(PREDICTION_API_URL, json=data)

    if response.status_code == 200:
        prediction = response.json().get("prediction", "Unable to predict")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"The predicted penguin species is: {prediction}")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Sorry, there was an error with the prediction.")
        )


if __name__ == "__main__":
    app.run(debug=True)
