import serial
import adafruit_fingerprint

import time
import json


def deleta():
    filename = "template.json"
    with open(filename, "r+", encoding='utf-8') as f:
        data = json.load(f)
        while True:
            id = input('Digite o id que deseja deletar ou 0 para retornar ao menu anterior: ')

            if id == '0':
                break
            if id in data.keys():
                confirm = input(f'Você tem certeza que deseja deletar a digital do usuario: {id}\n'
                                f'1 - SIM\n'
                                f'2 - NÃO\n')

                if confirm == '1':
                    data.pop(id)
                    with open(filename, 'w+', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                else:
                    print("Operação cancelada.\n")
            else:
                print(f"Usuario {id} não cadastrado, verifique o id e tente novamente.\n")

