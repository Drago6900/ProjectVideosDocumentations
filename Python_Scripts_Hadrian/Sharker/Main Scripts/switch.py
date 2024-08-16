import json
import time
import hashlib
import hmac
import base64
import uuid
import requests

HUB = 'FBB047F20CD5'
SWITCHBOT_BACK_ON = 'D5742165BD00'
SWITCHBOT_BACK_OFF = 'FFBB7C5768B7'
SWITCHBOT_OFF = 'FAFA7E14BAD4'
SWITCHBOT_ON = 'DAC1679E238F'
ENDPOINT = 'https://api.switch-bot.com/v1.1/'

def generate_api_header():
    apiHeader = {}
    # open token
    token = '56dc0c2978ac3c083b29cd7805115790642b123060238381ef121a797b501e733d6adffe4179fd3ea82699eca9d78def' # copy and paste from the SwitchBot app V6.14 or later
    # secret key
    secret = 'd17167f43134bbdf5c9842edef2c8189' # copy and paste from the SwitchBot app V6.14 or later
    nonce = uuid.uuid4()
    t = int(round(time.time() * 1000))
    string_to_sign = '{}{}{}'.format(token, t, nonce)

    string_to_sign = bytes(string_to_sign, 'utf-8')
    secret = bytes(secret, 'utf-8')

    sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
    #Build api header JSON
    apiHeader['Authorization']=token
    apiHeader['Content-Type']='application/json'
    apiHeader['charset']='utf8'
    apiHeader['t']=str(t)
    apiHeader['sign']=str(sign, 'utf-8')
    apiHeader['nonce']=str(nonce)

    return apiHeader

def send_command(device_id, command):
    apiHeader = generate_api_header()
    url = ENDPOINT + 'devices/' + device_id + '/commands'
    response = requests.post(url, headers=apiHeader, data=json.dumps(command))
    print(response.content)

def turn_on_switch():
    on_command = {'command': 'turnOn', "parameter": "default", "commandType": "command"}
    send_command(SWITCHBOT_ON, on_command)
    send_command(SWITCHBOT_BACK_ON, on_command)

def turn_off_switch():
    off_command = {'command': 'turnOn', "parameter": "default", "commandType": "command"}
    send_command(SWITCHBOT_OFF, off_command)
    send_command(SWITCHBOT_BACK_OFF, off_command)