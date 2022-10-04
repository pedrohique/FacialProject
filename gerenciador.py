"""Objetivo do projeto é criar um sistema que ira permitir cadastrar,
ler e excluir digitais alem de permitir um loguin de adm"""

import time
import json

import serial
import adafruit_fingerprint

import funcs
# from funcs import cadastra, compara, exclui

#  Faz a conexão com o leitor biometrico
uart = serial.Serial("COM3", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)




while True:
    opcao = input("\nDigite o numero da opção desejada:\n"
                  "1 - CADASTRAR NOVA DIGITAL\n"
                  "2 - LOCALIZAR CADASTRO\n"
                  "3 - DELETAR DIGITAL\n")

    if opcao == '1':
        funcs.cadastra.Cadastra(finger)

    elif opcao == '2':
        funcs.compara.compara(finger)

    elif opcao == '3':
        funcs.exclui.deleta()

