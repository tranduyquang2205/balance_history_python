import json
import time
import base64
import hashlib
from datetime import datetime, timezone
import websocket
import requests
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5
import base64
# Your RSA key (Replace with the actual key)
key = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0+B5KsZ/Q4c252WDMHVf4TPtoWwfTiikKu7NGkGaleBWZbDTyql4Cxf6aTMrIyqfYShGCVFWhJgNSmAbqkzvRr9BJVbyTVXppbTbeCKplpFso6IoMBXMizq3P+5VyvS+YFhPrCzDv5iFvMgnmkjlRm3rUZ0Nd22UdIh1Rvb3A/AnnzHR1PEqyYaS4/kzHgwKO0H404QTTA8Js67pA/WC4Bv/6fnE/GXMwsoWzZXwPeofSBkXFNsj2nrXROUfDzUmUQaMZT4monOt1ihzyRiF7+yHk6jmtFNU8KgrX2rnkqtpSCl524zFR9fztZplq2VqvpuefQNuBy3y5Ss1EnY24wIDAQAB\n-----END PUBLIC KEY-----"

def Ht(e, key):
    # Load the RSA key from the key string (in PEM format)
    rsa_key = RSA.import_key(key)

    # Encrypt the message using PKCS1 padding
    cipher = PKCS1_v1_5.new(rsa_key)

    ciphertext = cipher.encrypt(e.encode('utf-8'))

    # Encode the ciphertext as base64
    return base64.b64encode(ciphertext).decode('utf-8')

def convert_date_to_milliseconds(date_string):
    date_obj = datetime.strptime(date_string, "%d/%m/%Y")
    timestamp_seconds = int(date_obj.timestamp())
    timestamp_milliseconds = timestamp_seconds * 1000
    return timestamp_milliseconds

def generate_random_string(length=10):
    import random
    import string
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
class Namabank:
    def __init__(self):
        self.timeout_seconds = 15
        
    def login(self,username, password,session_token):
        global key
        password = Ht(hashlib.md5(password.encode()).hexdigest(), key)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://ops.namabank.com.vn/',
            'Content-Type': 'application/json',
            'session-token': session_token,
            'device-info': 'Windows%3A10%3AEdge%3A11%3AUnknown',
            'app-version': '2.0.0.0:Web',
            'device-id': '',
            'browserId': '2.2.6.0',
            'checking': 'c02a9c51a0c86ea241edaff3d8f106c0',
            'Origin': 'https://ops.namabank.com.vn',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        data = {
            'username': username,
            'password': password,
        }
        
        response = requests.post('https://ops-api.namabank.com.vn/auth/personal/v3/login', headers=headers, json=data)
        response_data = response.json()
        if response_data.get('data') and response_data.get('code') == 2000 and response_data['data'].get('auth') and response_data['data']['auth'].get('token'):
            response_data['token']=response_data['data']['auth']['token']
            response_data['deviceID']=response_data['data']['auth']['deviceID']
            return response_data
        else:
            return response_data

    def check_history(self,device_id, token, account_number, from_date, to_date, limit):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://ops.namabank.com.vn',
            'Pragma': 'no-cache',
            'Referer': 'https://ops.namabank.com.vn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'checking': '05afd4d8e446c3cadf1460eb9830876c',
            'device-id': device_id,
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': 'Android',
            'token': token
        }
        
        data = {
            'accountNumber': account_number,
            'fromDate': from_date,
            'toDate': to_date,
            'page': 1,
            'size': limit,
            'txnTypes': []
        }
        
        response = requests.post('https://ops-api.namabank.com.vn/user/transactions', headers=headers, json=data)
        return (response.text)

    def get_transaction(self,username,password,account_number,from_date,to_date,limit):
        username = username
        password = password
        account_number = account_number
        from_date = convert_date_to_milliseconds(from_date)
        to_date = convert_date_to_milliseconds(to_date) + 86400000 - 36000
        a = int(time.time() * 1000)
        session_token = f"WEB-USER({hashlib.md5(f'{a}{generate_random_string(20)}{a}'.encode()).hexdigest()})WEB-USER"
        sign = hashlib.sha256(f"{session_token}e6c20ecaeea12da7026972d6452f88b6".encode()).hexdigest()
        socket_info = {
                'socketName': session_token,
                'sign': sign
            }
        login_info = self.login(username, password,session_token)
        if not ( login_info.get('data') and login_info.get('code') == 2000 and login_info['data'].get('auth') and login_info['data']['auth'].get('token')):
            if 'code' in login_info and 'messages' in login_info:
                if login_info['code'] == 4022:
                        return {
                        'code': 444,
                        'success': False,
                        'message': login_info['messages']
                        }
                else:
                    return {
                        'code': 400,
                        'success': False,
                        'message': login_info['messages']
                        }
            return {
            'code': 520,
            'success': False,
            'message': "Unknown Error!"
        }
        device_id = login_info['deviceID']
        token = login_info['token']
        ws = websocket.WebSocket()
        ws.connect('wss://ops-socket.namabank.com.vn/intelin')
        ws.send(json.dumps(socket_info))
        step = 1
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout_seconds:
                return {'code': 408, 'success': False, 'message': 'Timeout occurred'}
            message = ws.recv()
            
            if message and step == 1:
                self.check_history(device_id, token, account_number, from_date, to_date, limit)
                step += 1
            else:
                message_data = json.loads(message)
                if 'data' in message_data and 'txnInfoUser' in message_data['data'] and message_data['code'] == 2735:
                    ws.close()
                    for account in message_data['data']['txnInfoUser']:
                        if account['accountNumber'] == account_number:
                            return  {'code':200,'success': True, 'message': 'Thành công',
                                    'data':{
                                        'transactions':account['timeline'],
                            }}
                    return {'code':404,'success': False, 'message': 'account_number not found!'} 

                else:
                    step += 1
    def get_balance(self,username,password,account_number):
        username = username
        password = password
        account_number = account_number
        a = int(time.time() * 1000)
        session_token = f"WEB-USER({hashlib.md5(f'{a}{generate_random_string(20)}{a}'.encode()).hexdigest()})WEB-USER"
        sign = hashlib.sha256(f"{session_token}e6c20ecaeea12da7026972d6452f88b6".encode()).hexdigest()
        socket_info = {
                    'socketName': session_token,
                    'sign': sign
                }
        ws = websocket.WebSocket()
        ws.connect('wss://ops-socket.namabank.com.vn/intelin')
        ws.send(json.dumps(socket_info))
        step = 1
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout_seconds:
                return {'code': 408, 'success': False, 'message': 'Timeout occurred'}
            message = ws.recv()
            if message and step == 1:
                login_info = self.login(username, password,session_token)
                if not ( login_info.get('data') and login_info.get('code') == 2000 and login_info['data'].get('auth') and login_info['data']['auth'].get('token')):
                    if 'code' in login_info and 'messages' in login_info:
                        if login_info['code'] == 4022:
                                return {
                                'code': 444,
                                'success': False,
                                'message': login_info['messages']
                                }
                        else:
                            return {
                                'code': 400,
                                'success': False,
                                'message': login_info['messages']
                                }
                    return {
                    'code': 520,
                    'success': False,
                    'message': "Unknown Error!"
                }
                step += 1
            else:
                message_data = json.loads(message)
                if 'data' in message_data and 'account' in message_data['data']:
                    ws.close()
                    for account in message_data['data']['account']:
                        if account['accountNumber'] == account_number:
                            del account['accountNumber']
                            result =  {'code':200,'success': True, 'message': 'Thành công',
                                    'data':{
                                        'account_number': account_number,
                            }}
                            
                            result['data'].update(account)
                            return result
                        
                    return {'code':404,'success': False, 'message': 'account_number not found!'} 
                    break
                else:
                    step += 1

# nab = Namabank()
# balance = nab.get_balance('0935718805','Dvan7979#','401224973500001')
# print(balance)
# transaction = nab.get_transaction('0935718805','Dvan7979#','401224973500001',"13/04/2024","13/04/2024",1)

# print(transaction)
