from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi('r5g/c+48uHsULz72ndBEiFoLXz1cePj8hW1TMGi5fsy+PhRMk03Fm5XkYp1a8OBLrceHCUsWbmNKbk7la/6PRC4Kd0vB/DhjYAAZ0HWaE9Obtw/IIlN0sbKwAi1wg0kYW6T8SCd91Qw5suk/I3V7FgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('36582c2446eb6708c1f48a559c5ecd96')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

if __name__ == '__main__':
    app.run()
