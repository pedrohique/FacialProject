from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QWidget, QHBoxLayout
import sys


import requests
import json
import serial
import adafruit_fingerprint
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


api_url_base = 'https://'+config.get('dados_api', 'server')+':'+config.get('dados_api', 'port') + '/'
print(api_url_base)


loguin = {
    "username": config.get('dados_api', 'uid'),
    "password": config.get('dados_api', 'pwd'),
    "method": "OAuth2PasswordBearer",
}


siteid = 'DEFAULT'

print('Tentando conexão com o leitor biometrico')
#  Faz a conexão com o leitor biometrico
uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)  # /dev/ttyUSB0  -- COM4
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
print('Conexão -- OK')


class Janela(QWidget):
    def __init__(self):
        super().__init__()
        self.topo = 10   #Altura que a janela vai aparecer
        self.esquerda = 0
        self.largura = 640
        self.altura = 480
        self.titulo = 'CMBio'



        """Botãoes"""
        atualizar = QPushButton('Atualizar', self)
        atualizar.move(100, 250)  # define a posição do botão
        atualizar.resize(200, 150)  # Define o tamanho do botão
        atualizar.setStyleSheet('QPushButton {background-color: #f1f1f1; font:bold; font-size:20px}')  # estetica do botão
        atualizar.clicked.connect(self.atualiza_json)

        loguin = QPushButton('Loguin', self)
        loguin.move(350, 250)  # define a posição do botão
        loguin.resize(200, 150)  # Define o tamanho do botão
        loguin.setStyleSheet('QPushButton {background-color: #f1f1f1; font:bold; font-size:20px}')  # estetica do botão
        loguin.clicked.connect(self.ConfereDigital)  # conecta o botão  com a função que ele vai rodar quando cicado



        """Labels"""
        self.label_1 = QLabel(self)  # Self Indica que a janela criada no Carregar Janela é que sera iniciada
        self.label_1.setText('Digite seu id no campo a cima.')
        self.label_1.move(150, 150)
        self.label_1.resize(500, 100)  # Largura x Altura
        self.label_1.setStyleSheet('QLabel {background-color: #f1f1f1; font:bold; font-size:20px}')


        """Caixa Texto"""
        self.caixa_texto = QLineEdit(self)
        self.caixa_texto.move(100, 50)
        self.caixa_texto.resize(500, 100)   # Largura x Altura

        #iniciaJanela principal

        self.CarregarJanela()

    def atualiza_json(self):

        token = requests.post(api_url_base + 'token', data=loguin, verify=False)

        headers = {
            "Authorization": "Bearer %s" % token.json()['access_token']
        }
        data = {
            'siteid': siteid
        }

        re = requests.get(api_url_base + 'employeebio', params=data, headers=headers, verify=False)

        if re.reason == 'OK':
            bios = re.json()
            data_dict = {}
            for emp in bios['biometrics']:
                if emp['FingerPrintTemplate']:
                    data_dict[emp['ID']] = [list(emp['FingerPrintTemplate']), emp['BadgeNumber']]
                else:
                    data_dict[emp['ID']] = [None, emp['BadgeNumber']]
            with open("template.json", "w") as arquivo:
                json.dump(data_dict, arquivo, indent=4)
            self.label_1.setStyleSheet('QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: green}')
            self.label_1.setText('Biometrias atualizadas com sucesso.')
        else:
            print('Conexão APi falhou')


    def ConfereDigital(self):

        key = self.caixa_texto.text()
        print(key)

        def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
            """this is to make sure LED doesn't interfer with example
            running on models without LED support - needs testing"""
            try:
                finger.set_led(color, mode, speed, cycles)
            except Exception as exc:
                print("INFO: Sensor les not support LED. Error:", str(exc))


        with open("template.json", "r") as file:
            data = json.load(file)
            if key in data.keys():
                if data[key][0]:
                    print("Aguardando pela digital...")
                    self.label_1.setText("Aguardando pela digital")
                    set_led_local(color=3, mode=1)
                    while finger.get_image() != adafruit_fingerprint.OK:
                        pass
                    print("Analisando...")
                    self.label_1.setText("Analisando")

                    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                        pass

                    finger.send_fpdata(data[key][0], "char", 2)
                    i = finger.compare_templates()



                    if i == adafruit_fingerprint.OK:
                        i = finger.finger_search()
                        set_led_local(color=2, speed=150, mode=6)
                        print(f"Acesso liberado - Usuario: {key} badge = {data[key][1]}.")

                        self.label_1.setStyleSheet(
                            'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: green}')
                        self.label_1.setText(f"Acesso liberado - Usuario: {key} badge = {data[key][1]}.")

                        # send_arduino(data[key][1])
                        # atualiza_json(siteid)  # Pendente
                    elif i == adafruit_fingerprint.NOMATCH:
                        set_led_local(color=1, mode=2, speed=20, cycles=10)
                        print(f"Digital não confere para o usuario: {key}")

                        self.label_1.setStyleSheet(
                            'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                        self.label_1.setText(f"Digital não confere para o usuario: {key}")

                        # atualiza_json(siteid)  # pendente
                    else:
                        print("Other error!")
                        self.label_1.setStyleSheet(
                            'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                        self.label_1.setText("Other error!")
                else:
                    print('Digital não cadastrada.')
                    self.label_1.setStyleSheet(
                        'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                    self.label_1.setText('Digital não cadastrada.')
            else:
                print('Usuario não cadastrado no sistema i9 procure um administrador')
                self.label_1.setStyleSheet(
                    'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                self.label_1.setText('Usuario não cadastrado no sistema i9 procure um administrador')

    def CarregarJanela(self):
        self.setGeometry(self.esquerda, self.topo, self.largura, self.altura)
        self.setWindowTitle(self.titulo)
        self.show()

    def botao1_click(self):
        conteudo = self.caixa_texto.text()

        print(conteudo)
        self.label_1.setStyleSheet('QLabel {background-color: blue; font:bold; font-size:20px}')

    def botao2_click(self):
        print('ola 2')
        self.label_1.setStyleSheet('QLabel {background-color: red; font:bold; font-size:20px}')

aplicacao = QApplication(sys.argv)
j = Janela()
j.show()
sys.exit(aplicacao.exec_())