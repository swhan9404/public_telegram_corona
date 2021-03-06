# :star: 서비스 기능 

- 텔레그램 봇 이름 : seungwoon_bot1

1. 봇에 대한 채팅 명령어에 따라 실시간 답변
2. 코로나 확진자 수 실시간 알림
   - 08:00 ~ 13:00 까지 6분 간격으로 질병관리본부 사이트를 크롤링하여 변경시 텔레그램에 알림

![image-20210416011106209](readme.assets/image-20210416011106209.png)

# :mag: 서비스 구성

![](readme.assets/serviceArchitecture.png)

1. 텔레그램 봇 구성

   web hook을 활용하여, amazon API gateway 에서 그 신호를 받고 amazon Lambda를 실행하여 발생할 수 있는 요금을 최소화하여 구성

2. 데이터 베이스

   Firebase Realtime DataBase

   - 코로나 알림을 받을 사용자들 id, 전날 코로나 확진자수 내용 저장

3. 스케쥴 작업

   heroku 에서 APScheduler를 활용하여 특정시간에 함수가 작동할 수 있도록 구성



## :pushpin: 만든 방법 정리본

[howTomake.md](https://github.com/swhan9404/public_telegram_corona/blob/master/howToMake.md)



# :eyes: ​고민한 사항

- telegram bot을 상시 활동상태로 만들기 위해 여러가지 방법이 있었다. 

  1. getUpdates()를 주기적으로 호출(loop) 하면서 새로운 메세지가 도착했는지 확인(teleport, python-telegram-bot 라이브러리 활용)

     프로그램 코드를 올릴 '서버'가 필요 - EC2 , 라즈베리파이, Digital Ocean같은 곳의 VPS 등

     - 단점 : 챗봇과 메세지를 주고 받을 때보다 안그럴 때가 많다면 자원 낭비가 심하다

  2. 웹훅 - 메시지가 도착했을 때 주소를 호출

     AWS API Gateway - 웹훅할 주소 생성 및 lambda 실행 연결

     AWS Lambda - 서버없이 서비스를 구현할 수 있도록 만든 서비스

     - 메시지가 도착했을 때만 실행 - 자원 낭비 최소화



# :pencil: 파일의 구성

개발환경 : python 3.6.12

- amazonLambda : aws lambda에 올릴 파일

  - RootDirectory를 압축해서 zip파일 업로드 해서 작동
    - lambda_function.py : 실제 작동 파일
    - 그 외는 환경 및 필요 키파일 등을 가지고 있음

- heroku : heroku에서 실시간 코로나 정보 알림을 작동하는 파일 부분

  - 이 부분만 때서 git push heroku master 로 배포작업을 하면됨

  - main.py : 실제 핵심 작동로직

  - requirements.txt : 작동하는데 필요한 라이브러리 모음 리스트

    - pip install -r requirements.txt 

      로 개인 환경에 환경 세팅할 수 있음

  - runtime.py : python 버전 명시

  - Profile : Schduler에 특정시간에 주기적으로 process 실행시키기 위함

- telegrambot : 로컬환경에서 개인적으로 텔레그램봇을 건드릴 때 쓰는 파일

  - amazonLambda 의 파일을 작성하기 전 로컬에서 로직 실험해보는 용도로 사용
  - telepot 과 firebase 사용





# :fire: 서비스 후 발생한 이슈

[이슈확인하기](https://github.com/swhan9404/public_telegram_corona/issues?q=is%3Aissue+is%3Aclosed)

## 2021.01.22 

- 이슈

  - 증가확진자 수에 살짝의 오차가 있음

- 원인

  - 현재 증가 확진자 수 계산법

    = 이전 누적확진자 수 - 오늘 누적확진자 수

  - 질병관리본부 발표에서 각 지자체에서 정보를 받아 추합 후 발표자료를 내는데, 이전 자료에서 오차가 있을 경우 그 부분에 대해 수정을 하여 누적확진자 수를 발표함

- 해결

  - 증가확진자 수 계산 방식을 바꿈

    누적 확진자 수를 크롤링해올 때 증가확진자 수도  같이 크롤링하여 데이터 베이스에 계속 저장되어있도록 바꿈

## 2021.02.21

- 이슈

  - 9시에 1번, 9시 42분에 1번 정보가 전달됨

- 원인

  - 2021.02.20 에 특별발표로 오후 2시경에 비정규적으로 확진자 수에 대한 발표가 있었고 9시에 한 발표에 2명의 누적확진자가 증가했었음.

  - 9시(heroku 스케줄러 작동시작시간) - 전날 오후 2시에 대한 발표 전달

    9시 42분 - 2021.02.21 발표자료 전달

    을 했기 때문에 하루에 2번이나 알림이 오게됨

- 해결

  - 비정기적 발표에 대한 대응을 하기위해  14, 15, 16, 18, 22 시에 작업 돌아가도록 스케줄 추가

## 2021.02.29

- 이슈
  - 챗봇의 답변이 멈춰버림
- 원인
  - public_corona repo를 만들고 공개를 하다가 amazon lambda쪽에 올린 파일 중 하나의 키가 노출되서 작동을 멈춤
- 해결
  - 일단 api gateway 주소도 노출되어 있어서 혹시 몰라 새로운 api gateway를 만들어서 다시 구성
  - telegram bot api key를 재발급받고 그에 맞추어 코드들을 수정함



## 2021.04.03

- 이슈
  - 누적 확진자와 증가 확진자 표기가 반대로 되어있는 등 자잘한 표기 에러
- 해결
  - 표기에 대한 부분을 의미에 알맞게 바꿈
    - 누적확진자 : 내용
    - 증가확진자 : 내용
- 챗봇 추가 기능 구현
  - 기능 : 오늘 확진자가 몇 명인지 물어보면 답할 수 있도록
  - 기능 구현을 위한 바꾼 내용
    - firebase 내에 누적확진자 밖에 기록하지 않았는데, 증가확진자도 기록하는 것으로 수정
    - amazon lambda 내에 기능구현을 위한 코드 추가

## 2021.07.11

- 이슈
  - 확진자 수가 1000명이 넘어갈 경우 1,000 처럼 쉼표가 생겨서 int로 변환하는데 에러가 발생해서 2~3일 동안 제대로 작동을 안함
- 해결
  - 누적 확진자 수를 받을 때 처럼 replace를 이용해서 , 를 제거해주고 int 변환하게 바꿈
