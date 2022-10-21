import json

import serial
import adafruit_fingerprint

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


print('Tentando conexão com o leitor biometrico')
#  Faz a conexão com o leitor biometrico
uart = serial.Serial("ttyUSB1", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
print('Conexão -- OK')

print('Tentando conexão com o Arduino')
ser = serial.Serial()
ser.port = "ttyUSB0"
ser.baudrate = 9600

ser.open()
print('Coxexão -- OK')


def send_arduino(string):
    string = f'/e{string}'
    ser.write(string.encode('utf-8'))

def atualiza_json(siteid):

    token = requests.post(api_url_base + 'token', data=loguin)

    headers = {
        "Authorization": "Bearer %s" % token.json()['access_token']
        }
    data = {
        'siteid': siteid
    }

    re = requests.get(api_url_base + 'employeebio', params=data, headers=headers)

    if re.reason == 'OK':
        bios = re.json()
        data_dict = {}
        for emp in bios['biometrics']:
            if emp['FingerPrintTemplate']:
                data_dict[emp['ID']] = [list(emp['FingerPrintTemplate']), emp['BadgeNumber']]
            else:
                data_dict[emp['ID']] = [None, emp['BadgeNumber']]
        with open("template.json", "w") as arquivo:
            json.dump(data_dict, arquivo, indent=4)

siteid = 'DEFAULT'
atualiza_json(siteid)

while True:
    def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
        """this is to make sure LED doesn't interfer with example
        running on models without LED support - needs testing"""
        try:
            finger.set_led(color, mode, speed, cycles)
        except Exception as exc:
            print("INFO: Sensor les not support LED. Error:", str(exc))


    while True:

        key = input('Digite seu ID: ')
        if key != '*':
            # print('Abrindo templates')
            with open("template.json", "r") as file:
                data = json.load(file)
                # print('Templates carregados corretamente.')

                if key in data.keys():
                    if data[key]:
                        print("Aguardando pela digital...")
                        set_led_local(color=3, mode=1)
                        while finger.get_image() != adafruit_fingerprint.OK:
                            pass
                        print("Analisando...")
                        if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                            pass

                        finger.send_fpdata(data[key][0], "char", 2)

                        i = finger.compare_templates()

                        if i == adafruit_fingerprint.OK:
                            i = finger.finger_search()
                            set_led_local(color=2, speed=150, mode=6)
                            print(f"Acesso liberado - Usuario: {key} badge = {data[key][1]}.")
                            # send_arduino(data[key][1])
                            # atualiza_json(siteid)  # Pendente
                        elif i == adafruit_fingerprint.NOMATCH:
                            set_led_local(color=1, mode=2, speed=20, cycles=10)
                            print(f"Digital não confere para o usuario: {key}")
                            #atualiza_json(siteid)  # pendente
                        else:
                            print("Other error!")
                    else:
                        print('Digital não cadastrada.')
                else:
                    print('Usuario não cadastrado no sistema i9 procure um administrador')
        elif key == '*':
            atualiza_json(siteid)
