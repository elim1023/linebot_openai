from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global gpt_reply_count
    # user_id = event.source.user_id
    text1=event.message.text

    if user_id not in user_message_count:
        user_message_count[user_id] = 0
        
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": "你是一個親切、友善、理性，但偶爾會用表情符號的助手"},
            {"role": "user", "content": text1}
        ],
        model="gpt-5-nano",
        temperature = 1,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
        # user_message_count[user_id] += 1
        gpt_reply_count += 1
    except:
        ret = '發生錯誤！'

    # save_data(user_message_count)
    # count = user_message_count[user_id]
    reply_text = f"{ret}\n\nGPT已回覆：{gpt_reply_count} 則訊息"
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))

if __name__ == '__main__':
    app.run()
