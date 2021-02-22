import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import requests
from bs4 import BeautifulSoup

import time
from apscheduler.schedulers.blocking import BlockingScheduler

class Crawling :
    def getData(self) :
        # 2. 크롤링
        url = 'http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=11&ncvContSeq=&contSeq=&board_id=&gubun='
        res = requests.get(url).text
        bs = BeautifulSoup(res, 'html.parser')
        # 현재 환자수
        now_patient = int((bs.select_one('#content > div > div.caseTable > div:nth-of-type(1) > ul > li:nth-of-type(1) > dl > dd').text).replace(',',''))
        today_patient = int((bs.select_one('#content > div > div.caseTable > div:nth-of-type(1) > ul > li:nth-of-type(2) > dl > dd > ul > li:nth-of-type(1) > p').text).lstrip("+ "))
        
        return now_patient, today_patient
        
    # 3. 텔레그램 연동
    def telegram(self, before_patient, now_patient, today_patient, chat_ids) : 
        token = '15토큰값:AAH토큰값'
        api_url =f'https://api.telegram.org/bot{token}'
        chat_id_url = f'{api_url}/getUpdates'
        #response = requests.get(chat_id_url).json()

        #chat_ids = set(map(lambda x: x['message']['chat']['id'], response['result'])) # 메세지 보낸 모든 사람들
        #chat_ids ={0 : 1544010213}
        text= f'증가 확진자 수 : {today_patient}\n현재 확진자 수 : {now_patient}'

        for chat_id in chat_ids : 
            message_url = f'{api_url}/sendMessage?chat_id={chat_id}&text={text}'
            response = requests.get(message_url).json()
        
        return

    def sendMessageTest(self, text) :
        token = '15토큰값:AAH토큰값'
        api_url =f'https://api.telegram.org/bot{token}'
        chat_id = 1544010213

        message_url = f'{api_url}/sendMessage?chat_id={chat_id}&text={text}'
        response = requests.get(message_url).json()

        return


class Firebase :
    cred = credentials.Certificate("./asset/firebase키.json") # 키 파일
    firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://covid-patient-d2452-default-rtdb.firebaseio.com/' #데이터베이스 주소 입력
    })

    def getData(self) :
        dir = db.reference('patient')
        # 데이터 베이스 참조 이전 환자수
        before_patient = dir.get() 
        return before_patient

    # 1-1. 데이터베이스 접근 후 내용 변경
    def updateDataBase(self, now_patient) :
        dir = db.reference()
        dir.update({
            "patient" : now_patient
        })
        return

    def getChatIds(self) :
        dir=db.reference('chat_ids')
        return dir.get()

    def updateChatIds(self, nowIds) :
        dir=db.reference('chat_ids')
        dir.update({
            'chat_ids' : nowIds
        })


crawling = Crawling()
firebase = Firebase()

crawling.sendMessageTest("heroku시작 : "+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='*', hour='9-11', minute='*/6')
def scheduled_job():
    #crawling.sendMessageTest("작업시작 : "+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    before_patient=0
    now_patient=0
    today_patient =0

    before_patient = firebase.getData()
    now_patient, today_patient = crawling.getData()

    # 조건 확인 후 전송
    if now_patient != before_patient :
        chat_ids = firebase.getChatIds()
        
        crawling.telegram(before_patient, now_patient, today_patient, chat_ids)
        firebase.updateDataBase(now_patient)
        #crawling.sendMessageTest("작업끝 : "+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

sched.start()




