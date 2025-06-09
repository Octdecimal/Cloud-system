from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioSendMessage, VideoSendMessage

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

baseurl = '你的NGROK網址/static/'  #靜態檔案網址

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    if mtext == '@傳送聲音':
        try:
            message = AudioSendMessage(
                original_content_url=baseurl + 'mario.m4a',  #聲音檔置於static資料夾
                duration=20000  #聲音長度20秒
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

    elif mtext == '@傳送影片':
        try:
            message = VideoSendMessage(
                original_content_url=baseurl + 'robot.mp4',  #影片檔置於static資料夾
                preview_image_url=baseurl + 'robot.jpg'
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

if __name__ == '__main__':
    app.run()
