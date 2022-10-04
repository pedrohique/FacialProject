import serial
import adafruit_fingerprint

import time
import json


# #Faz a conexão com o leitor biometrico
# uart = serial.Serial("COM3", baudrate=57600, timeout=1)
# finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)





def compara(finger):

    def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
        """this is to make sure LED doesn't interfer with example
        running on models without LED support - needs testing"""
        try:
            finger.set_led(color, mode, speed, cycles)
        except Exception as exc:
            print("INFO: Sensor les not support LED. Error:", str(exc))


    with open("template.json", "r") as file:
        data = json.load(file)  # file.read()
        while True:
            key = input('Digite o ID do funcionario ou 0 para retornar ao menu anterior: ')

            print("Aguardando pela digital...")
            set_led_local(color=3, mode=1)
            while finger.get_image() != adafruit_fingerprint.OK:
                pass
            print("Analisando...")
            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                return False

            inicio = time.time()

            finger.send_fpdata(list(data[key]), "char", 2)

            i = finger.compare_templates()

            if i == adafruit_fingerprint.OK:  # i==0
                i = finger.finger_search()
                print(key)
                set_led_local(color=2, speed=150, mode=6)
                print(f"Digital localizada - Usuario: {key}.")
                break
            if i == adafruit_fingerprint.NOMATCH:
                set_led_local(color=1, mode=2, speed=20, cycles=10)
                print(f"Digital não confere para o usuario: {key}")
            else:
                print("Other error!")

            final = time.time()
            print(final - inicio)
            break


