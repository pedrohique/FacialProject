"""Objetivo do projeto é criar um sistema que ira permitir cadastrar,
ler e excluir digitais alem de permitir um loguin de adm"""

import serial
import adafruit_fingerprint

import funcs


#  Faz a conexão com o leitor biometrico
uart = serial.Serial("COM4", baudrate=57600, timeout=1)
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

