import telepot
from telepot.loop import MessageLoop

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

TOKEN_MAIN = '토큰값'
StartMsg="""
BOT 기본 명령어
1. /help : 도움말
2. /코로나 알림 등록 
"""

# 특정 명령어에 따른 행동
def execommand(message, chat_id) :
    command = message
    
    if command == '/help' or '/start':
        send(chat_id, StartMsg)
    elif command == '/코로나 알림 등록' :
        corona_apply(chat_id)
    else :
        send(chat_id, "잘못된 명령어 입니다")

# 메세지 오는거 듣고 똑같이 대답
def echoserver(message, chat_id, target) :
    command = message
    # print(f"command : {command}")

    send(chat_id, f'안녕하세요~ {target["last_name"]}님')

# 메시지 텔레그램으로 전송
def send(chat_id, message) :
    bot.sendMessage(chat_id, message)

def corona_apply(chat_id) :
    cred = credentials.Certificate("./asset/json형식키파일") # 키 파일
    firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://covid-patient-d2452-default-rtdb.firebaseio.com/' #데이터베이스 주소 입력
    })

    dir=db.reference('chat_ids')
    chat_ids= dir.get()

    if chat_id not in chat_ids :
        dir.update({
            len(chat_ids) : chat_id
        })
        send(chat_id, '코로나 알림 등록이 완료되었습니다.\n08시~13시 사이에 신규 내용이 코로나정보가 발표되면 알림이 보내집니다.')
    else :
        send(chat_id, '이미 코로나 알림이 등록되어있습니다.')

# 봇 구동 알고리즘
def handler(msg) :
    # 메세지에 대한 "제목" 정보 추출, long으로 받으면 상세하게 데이터가 옴
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True) 
    
    #print(msg)
    '''
    {'message_id': 63, 
    'from': {'id': 1544010213, 
        'is_bot': False, 
        'first_name': '한', 
        'last_name': '승운', 
        'language_code': 'ko'}, 
    'chat': {'id': 1544010213, 
        'first_name': '한', 
        'last_name': '승운', 
        'type': 'private'}, 
    'date': 1610862128, 
    'text': 'ㅁㅁ'}
    '''

    #print(f'content_type :{content_type},\nchat_type: {chat_type}, \nchat_id : {chat_id}, \nmsg_date : {msg_date}, \nmsg_id : {msg_id}')
    '''
    content_type :text,
    chat_type: private,
    chat_id : 1544010213,
    msg_date : 1610862128,
    msg_id : 63
    '''
    
    if content_type == 'text' :
        _message = msg['text'] # ???
        if _message[0:1] == '/' : # 명령어
            execommand(_message, chat_id)
        else :
            echoserver(_message, chat_id, msg['from'])

bot = telepot.Bot(TOKEN_MAIN)
bot.message_loop(handler, run_forever=True)


