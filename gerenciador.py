"""Objetivo do projeto é criar um sistema que ira permitir cadastrar,
ler e excluir digitais alem de permitir um loguin de adm"""

import serial
import adafruit_fingerprint

import funcs
import os
import subprocess
import time

dir = os.listdir('/dev/')

def busca_sensor(dir_linux):
    """Essa função faz a conexão com o leitor biometrico."""
    print('Tentando conexão com o leitor biometrico')
    # logging.info('Tentando conexão com o leitor biometrico')

    for i in dir_linux:
        if i.startswith('ttyUSB'):
            try:
                #  Faz a conexão com o leitor biometrico
                os.system('sudo chmod a+rw /dev/' + i)  # só funciona quando executado no cmd
                uart = serial.Serial(f"/dev/{i}", baudrate=57600, timeout=1)  # /dev/ttyUSB0  -- COM4
                finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
                print('Conexão -- OK')
                # logging.info(f'Leitor biometrico encontrado. -- {i}')
                # lista_sensores.append(i)
                return finger
            except OSError as e:
                print("Leitor Biometrico não encontrado... Tentando novamente")
                pass
            except RuntimeError as run_err:
                print("Leitor Biometrico não encontrado... Tentando novamente")
                pass


while True:
    try:
        # logging.info('Buscando dispositivos conectados')
        dir_linux = os.listdir('/dev/')
        finger = busca_sensor(dir_linux)
        if finger:
            break
        time.sleep(1)
    except OSError as e:
        print(e)
        # logging.error(e)
        pass
    except RuntimeError as run_err:
        print(run_err)
        # logging.error(run_err)
        pass

# uart = serial.Serial(f"COM4", baudrate=57600, timeout=1)  # /dev/ttyUSB0  -- COM4
# finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)


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
