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


def compara(finger, siteid):

    def trata_dados(dados):
        data_dict = {}
        for emp in dados:
            data_dict[emp[0]] = emp[1]
        return data_dict

    cursor_dev.execute(f"SELECT ID, FingerPrintTemplate FROM EMPLOYEE WHERE EmployeeSiteID = ?", siteid)
    data = cursor_dev.fetchall()
    data_dict = trata_dados(data)
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
            print("Funcionario não cadastrado no sistema i9\n")
