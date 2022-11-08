import time

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QWidget, QHBoxLayout, QFormLayout, QGridLayout, QVBoxLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QRunnable, Qt, QThreadPool
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
import sys
import os

import requests
import json
import serial
import adafruit_fingerprint
import configparser
import random
import logging

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(format="%(message)s", level=logging.INFO)

api_url_base = 'https://'+config.get('dados_api', 'server')+':'+config.get('dados_api', 'port') + '/'
print(api_url_base)


loguin = {
    "username": config.get('dados_api', 'uid'),
    "password": config.get('dados_api', 'pwd'),
    "method": "OAuth2PasswordBearer",
}

# print(os.name)

siteid = 'DEFAULT'


dir_linux = os.listdir('/dev/')

for i in dir_linux:
    if i.startswith('ttyUSB'):
        try:
            print('Tentando conexão com o leitor biometrico')
            #  Faz a conexão com o leitor biometrico
            os.system('sudo chmod a+rw /dev/' + i)  # só funciona quando executado no cmd
            uart = serial.Serial(f"/dev/{i}", baudrate=57600, timeout=1)  # /dev/ttyUSB0  -- COM4
            finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
            print('Conexão -- OK')
            break
        except:
            print("Leitor Biometrico não encontrado... Tentando novamente")
            pass

# uart = serial.Serial(f"COM4", baudrate=57600, timeout=1)  # /dev/ttyUSB0  -- COM4
# finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# print('Tentando conexão com o Arduino')
# ser = serial.Serial()
# ser.port = "/dev/ttyUSB1"
# ser.baudrate = 9600
#
# ser.open()
# print('Coxexão -- OK')


def StyleLabel(cor='black'):
    command = "QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color:"+cor+"; text-align:center; padding :15px}"
    return command


class Janela(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.setLayout(layout)

        """ Botãoes """

        self.limpar = QPushButton('Limpar', self)
        self.limpar.resize(500, 75)  # Define o tamanho do botão
        self.limpar.setStyleSheet('QPushButton {background-color: #f1f1f1; font:bold; font-size:20px; padding :10px}')  # estetica do botão
        self.limpar.clicked.connect(self.LimpaCampo)  # conecta o botão  com a função que ele vai rodar quando cicado




        """Labels"""
        self.label_1 = QLabel(self)  # Self Indica que a janela criada no Carregar Janela é que sera iniciada
        self.label_1.resize(500, 100)  # Largura x Altura
        self.label_1.setStyleSheet(StyleLabel())



        """Caixa Texto"""
        topLayout = QFormLayout()
        self.caixa_texto = QLineEdit(self)
        self.caixa_texto.resize(500, 100)   # Largura x Altura
        self.caixa_texto.setStyleSheet('padding :15px')

        # codigo abaixo altera o tamanho da fonte
        self.fonte = self.caixa_texto.font()
        self.fonte.setPointSize(50)
        self.caixa_texto.setFont(self.fonte)

        # Chama função qando adiciona um id e aperta enter
        self.caixa_texto.returnPressed.connect(self.BuscaDigital)

        """ Layouts """

        layout.addRow(self.caixa_texto)
        layout.addWidget(self.label_1)
        layout.addWidget(self.limpar)

        """ Timers """
        self.timer_busca = QTimer(self)
        self.timer_limpa = QTimer(self)
        self.timer_busca.timeout.connect(self.ValidaDigital)
        self.timer_limpa.timeout.connect(self.LimpaLabel)
        self.timerDigital = QTimer(self)

        self.key = ''

        """ inicia Janela principal """

        self.CarregarJanela()  # Inicia a Tela
        self.AtualizaJson()  # Atualiza o Json na abertura do programa

    # def startAnimation(self):
    #     self.movie.start()
    #
    # def stopAnimation(self):
    #     self.movie.stop()

    def AtualizaJson(self):

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
                    data_dict[emp['ID']] = [list(emp['FingerPrintTemplate']), emp['BadgeNumber'], emp['acess']]
                else:
                    data_dict[emp['ID']] = [None, emp['BadgeNumber'], emp['acess']]
            with open("template.json", "w") as arquivo:
                json.dump(data_dict, arquivo, indent=4)
            self.ImprimeLabel1('Biometrias atualizadas com sucesso.', 'green')
            # self.timer1.stop()

        else:
            print('Conexão APi falhou')

    def ConfereAtualiza(self):
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


                        if data[key][2]:
                            print(f"Acesso liberado - Usuario: {key}  Aguardando Atualização")
                            print(data[key])


                            self.label_1.setStyleSheet(
                                'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: green}')
                            self.label_1.setText(f"Acesso liberado - Usuario: {key} - Aguardando Atualização")

                            time.sleep(1)
                            self.AtualizaJson()
                            self.caixa_texto.clear()

                            time.sleep(2)

                            self.label_1.setStyleSheet(
                                'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: green}')
                            self.label_1.setText(f"Acesso liberado - Usuario: {key} - Aguardando Atualização")
                        else:
                            self.label_1.setStyleSheet(
                                'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                            self.label_1.setText(f"Acesso negado - Usuario: {key} -"
                                                 f" Você não possui autorização para esta ação.")


                    elif i == adafruit_fingerprint.NOMATCH:
                        set_led_local(color=1, mode=2, speed=20, cycles=10)
                        print(f"Digital não confere para o usuario: {key}")

                        self.label_1.setStyleSheet(
                            'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                        self.label_1.setText(f"Digital não confere para o usuario: {key} - Não foi possivel atualizar")

                        # atualiza_json(siteid)  # pendente
                    else:
                        print("Other error!")
                        self.label_1.setStyleSheet(
                            'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                        self.label_1.setText("Other error!")
                else:
                    print('Digital não cadastrada.')
                    self.ImprimeLabel1('')
                    self.label_1.setStyleSheet(
                        'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                    self.label_1.setText('Digital não cadastrada.')
            else:
                self.ImprimeLabel1('')
                print('Usuario não cadastrado no sistema i9 procure um administrador')
                self.label_1.setStyleSheet(
                    'QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color: red}')
                self.label_1.setText('Usuario não cadastrado no sistema i9 procure um administrador')

    # def send_arduino(self, key):
    #     string = f'/e{key}'
    #     print(string)
    #     ser.write(string.encode('utf-8'))

    def BuscaDigital(self):
        self.key = self.caixa_texto.text()
        # Verificação visual
        if self.key:
            if self.key == "*/*":
                self.ImprimeLabel1('Atualizando as digitais.', 'yellow')
                self.AtualizaJson()
                # self.timer1.start(1000)

            else:

                with open("template.json", "r") as file:
                    self.data = json.load(file)
                if self.key in self.data.keys():
                    if self.data[self.key][0]:
                        self.ImprimeLabel1('Aguardando pela digital', 'yellow')
                        self.timer_busca.start(1)
                    else:
                        # print('Digital não cadastrada.')
                        self.ImprimeLabel1('Digital não cadastrada.', 'red')
                        self.caixa_texto.clear()
                else:
                    # print('Usuario não cadastrado no sistema i9 procure um administrador')
                    self.ImprimeLabel1('Usuario não cadastrado no sistema i9 procure um administrador', 'red')
                    self.caixa_texto.clear()

    def ValidaDigital(self):
        def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
            """this is to make sure LED doesn't interfer with example
            running on models without LED support - needs testing"""
            try:
                finger.set_led(color, mode, speed, cycles)
            except Exception as exc:
                print("INFO: Sensor les not support LED. Error:", str(exc))

        set_led_local(color=3, mode=1)
        limit = 50
        count = 0
        while finger.get_image() != adafruit_fingerprint.OK:  # espera um digital entrar no leitor
            if count <= limit:
                count += 1
                pass
            else:
                break

        if finger.image_2_tz(1) != adafruit_fingerprint.OK:  # espera por uma digital valida
            pass

        finger.send_fpdata(self.data[self.key][0], "char", 2)

        i = finger.compare_templates()

        if i == adafruit_fingerprint.OK:
            # i = finger.finger_search()
            set_led_local(color=2, speed=150, mode=6)
            self.ImprimeLabel1(
                f'Acesso liberado - Usuario: {self.key} badge = {self.data[self.key][1]}.', 'green')

            # self.send_arduino(data[key][1])

            self.caixa_texto.clear()

        elif i == adafruit_fingerprint.NOMATCH:
            set_led_local(color=1, mode=2, speed=20, cycles=10)

            self.ImprimeLabel1(f'Digital não confere para o usuario: {self.key}', 'red')
            self.caixa_texto.clear()

        else:
            self.ImprimeLabel1('Other error!', 'red')
            self.caixa_texto.clear()

        self.timer_busca.stop()

    def LimpaCampo(self):
        self.caixa_texto.clear()

    def LimpaLabel(self):
        self.ImprimeLabel1('Digite seu id no campo a cima e pressione ENTER.')
        self.timer_limpa.stop()

    def ImprimeLabel1(self, text, color='black'):
        self.label_1.setStyleSheet(StyleLabel(color))
        self.label_1.setText(text)
        print(text)
        self.timer_limpa.start(1000)

    def CarregarJanela(self):
        # self.setGeometry(self.esquerda, self.topo, self.largura, self.altura)
        # self.setWindowTitle(self.titulo)
        self.showFullScreen()
        self.show()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    j = Janela()
    j.show()
    sys.exit(App.exec_())