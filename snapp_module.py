import requests
import logging
import uuid

base_headers = {
    "accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8,ar;q=0.7,zh-CN;q=0.6,zh;q=0.5",
    "App-Version": "pwa",
    "Content-Length": "125",
    "Content-Type": "application/json",
    "locale": "fa-IR",
    "Sec-Ch-Ua": "\"Not A(Brand\";v=\"99\", \"Google Chrome\";v=\"121\", \"Chromium\";v=\"121\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Linux\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "X-App-Name": "passenger-pwa",
    "X-App-Version": "v18.13.1"
}

def login(phone_number):

    headers = base_headers.copy()
    
    headers['origin'] = 'https://app.snapp.taxi'  
    headers['referer'] = 'https://app.snapp.taxi/login'  

    payload = {
        "cellphone":f"+98{phone_number}",
        "attestation":{
            "method":"skip",
            "platform":"skip"
        },
        "extra_methods":[
            
        ]
    }

    url = 'https://app.snapp.taxi/api/api-passenger-oauth/v3/mutotp'

    resp = requests.post(url=url, headers=headers, json=payload)

    if resp.ok:
        return resp.json() 
    
    else:

        logging.error(resp.text)
        raise Exception(resp.content)


def otp(phone_number, token):

    headers = base_headers.copy()
    headers["origin"]= "https://app.snapp.taxi"
    headers["referer"]= f'https://app.snapp.taxi/verify-cellphone-otp/?cellphone=0{phone_number}'
    
    url = 'https://app.snapp.taxi/api/api-passenger-oauth/v3/mutotp/auth'


    payload ={
        "attestation":{
            "method":"skip",
            "platform":"skip"
        },
        "grant_type":"sms_v2",
        "client_id":"ios_sadjfhasd9871231hfso234",
        "client_secret":"23497shjlf982734-=1031nln",
        "cellphone": f"+98{phone_number}",
        "token":token,
        "referrer":"pwa",
        "device_id": uuid.uuid4().hex,
        
    }


    resp = requests.post(url=url, headers=headers, json=payload)
    
    if resp.ok:
        return resp.json()
        
    else:
        logging.error(resp.content)
        raise Exception(resp.content)

