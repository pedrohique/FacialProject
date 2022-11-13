"""Objetivo do projeto é criar um sistema que ira permitir cadastrar,
ler e excluir digitais alem de permitir um loguin de adm"""

import serial
import adafruit_fingerprint

import funcs
import os
import subprocess

# dir = os.listdir('/dev/')
#
# for i in dir:
#     if i.startswith('ttyUSB'):
#         # try:
#             print('Tentando conexão com o leitor biometrico')
#             #  Faz a conexão com o leitor biometrico
#             print('sudo cat /dev/' + i, 'r')
#             # resp = os.system('sudo chmod 777 /dev/' + i)
#             uart = serial.Serial("/dev/" + i, baudrate=57600, timeout=1)  # /dev/ttyUSB0  -- COM4
#             finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
#             print('Conexão -- OK')
        # except:
            # pass


uart = serial.Serial(f"COM3", baudrate=57600, timeout=1)  # /dev/ttyUSB0  -- COM4
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)


siteid = 'DEFAULT'


while True:
    opcao = input("\nDigite o numero da opção desejada:\n"
                  "1 - CADASTRAR NOVA DIGITAL\n"
                  "2 - LOCALIZAR CADASTRO\n"
                  "3 - DELETAR DIGITAL\n")

    if opcao == '1':
        funcs.cadastra.Cadastra(finger, siteid)

    elif opcao == '2':
        funcs.compara.compara(finger, siteid)

    elif opcao == '3':
        funcs.exclui.deleta(siteid)
