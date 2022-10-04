import time
import json

import serial
import adafruit_fingerprint


import funcs

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


while True:
    def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
        """this is to make sure LED doesn't interfer with example
        running on models without LED support - needs testing"""
        try:
            finger.set_led(color, mode, speed, cycles)
        except Exception as exc:
            print("INFO: Sensor les not support LED. Error:", str(exc))

    print('Abrindo templates')
    with open("template.json", "r") as file:
        data = json.load(file)
        print('Templates carregados corretamente.')
        while True:
            key = input('Digite seu ID: ')
            if key in data.keys():
                print("Aguardando pela digital...")
                set_led_local(color=3, mode=1)
                while finger.get_image() != adafruit_fingerprint.OK:
                    pass
                print("Analisando...")
                if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                    pass

                finger.send_fpdata(list(data[key]), "char", 2)

                i = finger.compare_templates()

                if i == adafruit_fingerprint.OK:
                    i = finger.finger_search()
                    set_led_local(color=2, speed=150, mode=6)
                    print(f"Acesso liberado - Usuario: {key}.")
                    send_arduino(key)
                    time.sleep(4)
                elif i == adafruit_fingerprint.NOMATCH:
                    set_led_local(color=1, mode=2, speed=20, cycles=10)
                    print(f"Digital não confere para o usuario: {key}")
                else:
                    print("Other error!")
            else:
                print('Digital não cadastrada procure um administrador')

