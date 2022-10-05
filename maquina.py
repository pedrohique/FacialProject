import json

import serial
import adafruit_fingerprint

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




print('Tentando conexão com o leitor biometrico')
#  Faz a conexão com o leitor biometrico
uart = serial.Serial("COM3", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
print('Conexão -- OK')

print('Tentando conexão com o Arduino')
ser = serial.Serial()#
ser.port = 'COM4'
ser.baudrate = 9600

ser.open()
print('Coxexão -- OK')


def send_arduino(string):
    string = f'/e{string}'
    ser.write(string.encode('utf-8'))

def atualiza_json(siteid):
    cursor_dev.execute(f"SELECT ID, FingerPrintTemplate FROM EMPLOYEE WHERE EmployeeSiteID = ?", siteid)
    data = cursor_dev.fetchall()
    data_dict = {}
    for emp in data:
        if emp[1]:
            data_dict[emp[0]] = list(emp[1])
        else:
            data_dict[emp[0]] = emp[1]
    with open("template.json", "w") as arquivo:
        json.dump(data_dict, arquivo, indent=4)

siteid = 'SZNGRP'
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

                        finger.send_fpdata(data[key], "char", 2)

                        i = finger.compare_templates()

                        if i == adafruit_fingerprint.OK:
                            i = finger.finger_search()
                            set_led_local(color=2, speed=150, mode=6)
                            print(f"Acesso liberado - Usuario: {key}.")
                            # send_arduino(key)
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
