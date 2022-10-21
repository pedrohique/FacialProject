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

def deleta(siteid):
    def trata_dados(re):
        if re.reason == 'OK':
            bios = re.json()
            data_dict = {}
            for emp in bios['biometrics']:
                print(emp)
                if emp['FingerPrintTemplate']:
                    data_dict[emp['ID']] = list(emp['FingerPrintTemplate'])
                else:
                    data_dict[emp['ID']] = None
            return data_dict


    def deleta_template(id):
        resp = requests.post(api_url_base + f'deletebio', params={'id': id}, headers=headers)
        return resp

    data = {
        'siteid': siteid
    }
    re = requests.get(api_url_base + 'employeebio', params=data, headers=headers)
    data_dict = trata_dados(re)

    while True:
        id = input('Digite o id que deseja deletar ou 0 para retornar ao menu anterior: ')
        if id == '0':
            break
        if id in data_dict.keys():
            if data_dict[id] is not None:
                confirm = input(f'Você tem certeza que deseja deletar a digital do usuario: {id}\n'
                                f'1 - SIM\n'
                                f'2 - NÃO\n')

                if confirm == '1':
                    resp = deleta_template(id)
                    if resp.status_code == 200:
                        print("Digital deletada com sucesso.")
                    else:
                        print("Não foi possivel deletar a digital, tente novamente.")
                else:
                    print("Operação cancelada.\n")
            else:
                print("Esse funcionario não possui digital cadastrada para que possa ser deletada.\n")
        else:
            print(f"Usuario {id} não cadastrado, verifique o id e tente novamente.\n")
