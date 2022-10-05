import serial
import adafruit_fingerprint

import time
import json


import configparser
import cryptocode
import pyodbc

'''Retorna os cribs que estão atrasados a x tempo'''
config = configparser.ConfigParser()
config.read('config.ini')

'''CNX DB - hom'''
server_hom = config.get('dados_banco_hom', 'server')
port_hom = config.get('dados_banco_hom', 'port')
database_hom = config.get('dados_banco_hom', 'database')
uid_hom = config.get('dados_banco_hom', 'uid')
pwd_hom = config.get('dados_banco_hom', 'pwd')

uid_hom = cryptocode.decrypt(uid_hom, "i9brgroup")
pwd_hom = cryptocode.decrypt(pwd_hom, "i9brgroup")


cnxn_hom = pyodbc.connect(
        f'DRIVER=SQL Server;SERVER={server_hom};PORT={port_hom};DATABASE={database_hom};UID={uid_hom};PWD={pwd_hom};')


cursor_dev = cnxn_hom.cursor()


def deleta(siteid):
    def trata_dados(dados):
        data_dict = {}
        for emp in dados:
            data_dict[emp[0]] = emp[1]
        return data_dict


    def deleta_template(id):
        template_none = None
        cursor_dev.execute(f'UPDATE EMPLOYEE SET "FingerPrintTemplate" = ? WHERE "ID" = ?', template_none, id)
        cursor_dev.commit()


    cursor_dev.execute(f"SELECT ID, FingerPrintTemplate FROM EMPLOYEE WHERE EmployeeSiteID = ?", siteid)
    data = cursor_dev.fetchall()
    data_dict = trata_dados(data)

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
                    deleta_template(id)
                else:
                    print("Operação cancelada.\n")
            else:
                print("Esse funcionario não possui digital cadastrada para que possa ser deletada.\n")
        else:
            print(f"Usuario {id} não cadastrado, verifique o id e tente novamente.\n")
