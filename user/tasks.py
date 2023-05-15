from celery import Celery
from random import randint
from redis import Redis

import requests
import os

API_KEY = os.environ.get('API_KEY')
app = Celery('task', broker='redis://localhost:6379')

redis_connection = Redis(host='localhost', port=6379, db=0, decode_responses=True, charset='UTF-8')



@app.task()
def send_otp(phone_number,verification_code):
    
    redis_connection.set(phone_number, verification_code, ex=120)


    url = "https://api.sms.ir/v1/send/verify/"
    data = {
        "mobile": phone_number,
        "templateId": 10000,
        "parameters": [
            {
                "name": "Code",
                "value": verification_code
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain",
        "x-api-key": API_KEY
    }
    requests.post(url, json=data, headers=headers)
