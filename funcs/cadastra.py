import serial
import adafruit_fingerprint

import time
import json







def Cadastra(finger):
    def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
        """this is to make sure LED doesn't interfer with example
        running on models without LED support - needs testing"""
        try:
            finger.set_led(color, mode, speed, cycles)
        except Exception as exc:
            print("INFO: Sensor les not support LED. Error:", str(exc))


    while True:

        set_led_local(color=3, mode=1)

        filename = "template.json"
        with open(filename, "r+", encoding='utf-8') as f:
            data = json.load(f)

        id = input('Digite o ID do funcionario ou 0 para retornar ao menu anterior: ')
        if id not in data.keys() and id != '0':
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
            data[id] = data_new

            with open(filename, 'w+', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

            set_led_local(color=2, speed=150, mode=6)
            print(f"Digital cadastrada com sucesso - Funcionario: {id}.\n")
        elif id == '0':
            break
        else:
            print(f"Digital ja cadastrada para o usuario {id}\n")
