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


def Cadastra(finger, siteid):
    def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
        """this is to make sure LED doesn't interfer with example
        running on models without LED support - needs testing"""
        try:
            finger.set_led(color, mode, speed, cycles)
        except Exception as exc:
            print("INFO: Sensor les not support LED. Error:", str(exc))


    def trata_dados(re):
        if re.reason == 'OK':
            bios = re.json()
            data_dict = {}
            for emp in bios['biometrics']:
                if emp['FingerPrintTemplate']:
                    data_dict[emp['ID']] = list(emp['FingerPrintTemplate'])
                else:
                    data_dict[emp['ID']] = None
            return data_dict


    def add_newdata(id, template):
        resp = requests.post(api_url_base + f'atualizabio', params={'id': id}, json=template, headers=headers)
        return resp


    while True:
        data = {
            'siteid': siteid
        }
        re = requests.get(api_url_base + 'employeebio', params=data, headers=headers)
        data_dict = trata_dados(re)

        set_led_local(color=3, mode=1)
        id = input('Digite o ID do funcionario ou 0 para retornar ao menu anterior: ')

        if id in data_dict.keys() and id != '0':  # Verifica se o usuario esta cadastrado no sistema

            if data_dict[id] is None:   # Verifica se a digital do usuario não esta cadastrado

                for fingerimg in range(1, 6):
                    if fingerimg == 1:
                        print("Coloque o dedo no sensor...", end="", flush=True)
                    else:
                        print("Coloque o mesmo dedo no sensor...", end="", flush=True)

                    while True:
                        i = finger.get_image()
                        if i == adafruit_fingerprint.OK:
                            print("Buscando digital")
                            break
                        if i == adafruit_fingerprint.NOFINGER:
                            print(".", end="", flush=True)
                        elif i == adafruit_fingerprint.IMAGEFAIL:
                            set_led_local(color=1, mode=2, speed=20, cycles=10)
                            print("Não foi possivel ler a digital")
                            return False
                        else:
                            set_led_local(color=1, mode=2, speed=20, cycles=10)
                            print("Erro desconhecido")
                            return False

                    print("Criando template...", end="", flush=True)
                    i = finger.image_2_tz(fingerimg)
                    if i == adafruit_fingerprint.OK:
                        print("Template criado")
                    else:
                        if i == adafruit_fingerprint.IMAGEMESS:
                            set_led_local(color=1, mode=2, speed=20, cycles=10)
                            print("Imagem bagunçada")
                        elif i == adafruit_fingerprint.FEATUREFAIL:
                            set_led_local(color=1, mode=2, speed=20, cycles=10)
                            print("Não foi possivel reconhecer a digital.")
                        elif i == adafruit_fingerprint.INVALIDIMAGE:
                            set_led_local(color=1, mode=2, speed=20, cycles=10)
                            print("Imagem invalida.")
                        else:
                            set_led_local(color=1, mode=2, speed=20, cycles=10)
                            print("Erro")
                        return False

                    if fingerimg == 1:
                        print("Retire o dedo.")
                        while i != adafruit_fingerprint.NOFINGER:
                            i = finger.get_image()

                print("Criando modelo...", end="", flush=True)
                i = finger.create_model()
                if i == adafruit_fingerprint.OK:
                    print("Modelo Criado")
                else:
                    if i == adafruit_fingerprint.ENROLLMISMATCH:
                        set_led_local(color=1, mode=2, speed=20, cycles=10)
                        print("Digitais lidas não são iguais, tente novamente.")
                    else:
                        set_led_local(color=1, mode=2, speed=20, cycles=10)
                        print("Erro desconhecido, tente novamente.")
                    return False

                print("Downloading template...")

                data_new = finger.get_fpdata("char", 1)
                resp = add_newdata(id, data_new)

                set_led_local(color=2, speed=150, mode=6)
                print(resp.status_code)
                if resp.status_code == 200:
                    print(f"Digital cadastrada com sucesso - Funcionario: {id}.\n")
                else:
                    print('não foi possivel cadastrar a digital, tente novamente.')
            else:
                print(f'A digital do funcionario {id} ja esta cadastrada, delete a digital para cadastrar novamente.\n')
        elif id == '0':
            break
        else:
            print(f"Funcionario não cadastrado no sistema i9 -- {id}\n")
