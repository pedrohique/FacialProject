import serial
import adafruit_fingerprint

import time
import json

import configparser
import cryptocode
import pyodbc
import requests


config = configparser.ConfigParser()
config.read('config.ini')


api_url_base = 'http://'+config.get('dados_api', 'server')+':'+config.get('dados_api', 'port') + '/'


loguin = {
    "username": config.get('dados_api', 'uid'),
    "password": config.get('dados_api', 'pwd'),
    "method": "OAuth2PasswordBearer",
}

token = requests.post(api_url_base + 'token', data=loguin)
headers = {
           "Authorization": "Bearer %s" % token.json()['access_token']
}

def compara(finger, siteid):

    def trata_dados(re):
        if re.reason == 'OK':
            bios = re.json()
            data_dict = {}
            for emp in bios['biometrics']:
                if emp['FingerPrintTemplate']:
                    data_dict[emp['ID']] = emp['FingerPrintTemplate']
                else:
                    data_dict[emp['ID']] = None
            return data_dict

    data = {
        'siteid': siteid
    }
    re = requests.get(api_url_base + 'employeebio', params=data, headers=headers)
    data_dict = trata_dados(re)

    def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
        """this is to make sure LED doesn't interfer with example
        running on models without LED support - needs testing"""
        try:
            finger.set_led(color, mode, speed, cycles)
        except Exception as exc:
            print("INFO: Sensor les not support LED. Error:", str(exc))

    while True:
        key = input('Digite o ID do funcionario ou 0 para retornar ao menu anterior: ')
        if key in data_dict.keys():
            if data_dict[key]:
                print("Aguardando pela digital...")
                set_led_local(color=3, mode=1)
                while finger.get_image() != adafruit_fingerprint.OK:
                    pass
                print("Analisando...")
                if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                    return False

                finger.send_fpdata(list(data_dict[key]), "char", 2)

                i = finger.compare_templates()

                if i == adafruit_fingerprint.OK:  # i==0
                    i = finger.finger_search()
                    set_led_local(color=2, speed=150, mode=6)
                    print(f"Digital localizada - Usuario: {key}.")
                    break
                if i == adafruit_fingerprint.NOMATCH:
                    set_led_local(color=1, mode=2, speed=20, cycles=10)
                    print(f"Digital não confere para o usuario: {key}")
                else:
                    print("Other error!")

                break
            else:
                print(f"Digital não cadastrada para o funcionario: {key}")
        else:
            print("Funcionario não cadastrado no sistema i9\n")
