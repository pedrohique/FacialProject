import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QWidget, QHBoxLayout, QFormLayout, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import sys
import os

import requests
import json
import serial
import adafruit_fingerprint
import configparser
import logging

dir_local = '/maquina/'


logging.basicConfig(filename= dir_local + '/logs/biometria.log', level=logging.DEBUG, filemode='a+',
                    format='%(asctime)s - %(levelname)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

# logging = setup_logger('biometria', dir_local + '/logs/biometria.log')


# Buscando dados de login
try:
    logging.info('Buscando arquivo de configuracao.')
    config = configparser.ConfigParser()
    config.read(dir_local + 'config.ini')
    user = config.get('dados_api', 'uid')
    password = config.get('dados_api', 'pwd')
    siteid = config.get('dados_api', 'siteid')
    if user and password and siteid:
        logging.info('Dados de configuração -- ok')
        loguin = {
            "username": user,
            "password": password,
            "method": "OAuth2PasswordBearer",
        }
    else:
        logging.warning('Arquivo de configuracao incompleto.')
except OSError as e:
    logging.error(e)

# buscando dados de servidor.
try:
    logging.info('Buscando dados de conexao no arquivo de configuracao')
    config = configparser.ConfigParser()
    config.read(dir_local + 'config.ini')
    server = config.get('dados_api', 'server')
    port = config.get('dados_api', 'port')
    if server and port:
        api_url_base = 'https://' + server + ':' + port + '/'
    else:
        logging.warning('Informações do servidor não disponiveis no config.')
except OSError as e:
    logging.error(e)


lista_sensores = []

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
                logging.info(f'Leitor biometrico encontrado. -- {i}')
                lista_sensores.append(i)
                return finger
            except OSError as e:
                print("Leitor Biometrico não encontrado... Tentando novamente")
                pass
            except RuntimeError as run_err:
                print("Leitor Biometrico não encontrado... Tentando novamente")
                pass

def busca_arduino(dir_linux):
    """Essa função faz a conexão com o arduino"""
    print('Tentando conexão com o arduino')
    # logging.info('Tentando conexão com o arduino')
    for i in dir_linux:
        if i.startswith('ttyUSB'):
            if i not in lista_sensores:
                try:
                    #  Faz a conexão com o leitor biometrico
                    os.system('sudo chmod a+rw /dev/' + i)  # só funciona quando executado no cmd
                    ser = serial.Serial(f"/dev/{i}", baudrate=9600, timeout=1)
                    print('Conexão -- OK')
                    logging.info(f'Arduino encontrado. -- {i}')
                    return ser
                except OSError as e:
                    print("Arduino não encontrado... Tentando novamente")
                    pass
                except RuntimeError as run_err:
                    print("Arduino não encontrado... Tentando novamente")
                    pass

logging.info('Buscando dispositivos.')
logging.info('Tentando conexão com o leitor biometrico')
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
        logging.error(e)
        pass
    except RuntimeError as run_err:
        print(run_err)
        logging.error(run_err)
        pass

logging.info('Tentando conexão com o arduino')
while True:
    try:
        dir_linux = os.listdir('/dev/')
        ser = busca_arduino(dir_linux)
        if ser:
            break
        time.sleep(1)
    except OSError as e:
        logging.error(e)
        pass
    except RuntimeError as run_err:
        logging.error(run_err)
        pass




def StyleLabel(cor='black'):
    command = "QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color:"+cor+"; text-align:center; padding :15px}"
    return command


class Janela(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QFormLayout()
        layout_butons = QHBoxLayout()
        grid = QGridLayout()

        widget = QWidget()

        widget.setLayout(grid)

        """ Botãoes """

        self.limpar = QPushButton('Limpar', self)
        self.limpar.resize(500, 75)  # Define o tamanho do botão
        self.limpar.setStyleSheet('QPushButton {background-color: #f1f1f1; font:bold; font-size:20px; padding :10px}')  # estetica do botão
        self.limpar.clicked.connect(self.LimpaCampo)  # conecta o botão  com a função que ele vai rodar quando cicado

        self.ok_but = QPushButton('Ok', self)
        self.ok_but.resize(500, 75)  # Define o tamanho do botão
        self.ok_but.setStyleSheet('QPushButton {background-color: #f1f1f1; font:bold; font-size:20px; padding :10px}')  # estetica do botão
        self.ok_but.clicked.connect(self.BuscaDigital)  # conecta o botão  com a função que ele vai rodar quando cicado

        """LOGO"""
        self.label_image = QLabel(self)
        self.pixmap = QPixmap(dir_local + 'logoi9.png')
        self.label_image.setPixmap(self.pixmap)
        self.label_image.resize(200,
                          200)


        """Labels"""
        self.label_1 = QLabel(self)  # Self Indica que a janela criada no Carregar Janela é que sera iniciada
        self.label_1.resize(500, 300)  # Largura x Altura
        self.label_1.setStyleSheet(StyleLabel())
        self.label_1.setStyleSheet('padding :15px')
        self.label_1.setAlignment(QtCore.Qt.AlignCenter)



        """Caixa Texto"""
        self.caixa_texto = QLineEdit(self)
        self.caixa_texto.resize(500, 300)   # Largura x Altura
        self.caixa_texto.setStyleSheet('padding :15px')

        # codigo abaixo altera o tamanho da fonte
        self.fonte = self.caixa_texto.font()
        self.fonte.setPointSize(50)
        self.caixa_texto.setFont(self.fonte)

        # Chama função qando adiciona um id e aperta enter
        self.caixa_texto.returnPressed.connect(self.BuscaDigital)

        """ Layouts """

        grid.addWidget(self.label_image, 0, 0)
        layout.addRow(self.caixa_texto)
        grid.addWidget(self.label_1, 2, 0)
        layout_butons.addWidget(self.ok_but, 0)
        layout_butons.addWidget(self.limpar, 0)
        grid.addLayout(layout, 1, 0)
        grid.addLayout(layout_butons, 3, 0)

        grid.setContentsMargins(50, 50, 50, 50)
        grid.setSpacing(10)
        self.setCentralWidget(widget)

        """ Timers """
        self.timer_busca = QTimer(self)
        self.timer_limpa = QTimer(self)
        self.timer_busca.timeout.connect(self.ValidaDigital)
        self.timer_limpa.timeout.connect(self.LimpaLabel)
        self.timerDigital = QTimer(self)

        self.key = ''

        """ inicia Janela principal """
        logging.info('iniciando interface')
        self.CarregarJanela()  # Inicia a Tela

        self.AtualizaJson()  # Atualiza o Json na abertura do programa


    def AtualizaJson(self):
        logging.info('Atualizando Json com biometrias')
        try:
            if api_url_base and loguin:
                token = requests.post(api_url_base + 'token', data=loguin, verify=False)
                if token:
                    headers = {
                        "Authorization": "Bearer %s" % token.json()['access_token']
                    }

                    data = {
                        'siteid': siteid
                    }

                    re = requests.get(api_url_base + 'employeebio', params=data, headers=headers, verify=False)
                    if re:
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
                            self.ImprimeLabel1('Biometrias atualizadas.', 'green')
                            logging.info('Biometrias atualizadas com sucesso.')

                        else:
                            logging.error('Biometrias atualizadas com sucesso.')
            else:
                logging.warning('Endereço do servidor ausente -- nao foi possivel atualizar as digitais')
        except OSError as oe:
            logging.error(oe)
            pass
        except RuntimeError as run_err:
            logging.error(run_err)
            pass
        except TypeError as te:
            logging.error(te)
            pass
        except ConnectionError as ce:
            logging.error(ce)
            pass
    def send_arduino(self, key):
        logging.info('Tentando enviar string para o arduino')
        try:
            string = f'/e{key}'
            print(string)
            if key and ser:
                ser.write(string.encode('utf-8'))
                logging.info('String enviada com sucesso.')
            else:
                logging.warning('Badge ou arduino ausente')
        except OSError as e:
            logging.error(e)
            pass
        except RuntimeError as run_err:
            logging.error(run_err)
            pass

    def BuscaDigital(self):
        self.key = self.caixa_texto.text()
        # Verificação visual
        if self.key:
            if self.key == "*/*":
                self.ImprimeLabel1('Atualizando as digitais.')
                self.AtualizaJson()
                # self.timer1.start(1000)

            else:

                with open("template.json", "r") as file:
                    self.data = json.load(file)
                if self.key in self.data.keys():
                    if self.data[self.key][0]:
                        self.ImprimeLabel1('Coloque sua DIGITAL.')
                        self.timer_busca.start(1)
                    else:
                        # print('Digital não cadastrada.')
                        self.ImprimeLabel1('Digital não cadastrada.', 'red')
                        self.caixa_texto.clear()
                else:
                    # print('Usuario não cadastrado no sistema i9 procure um administrador')
                    self.ImprimeLabel1('Usuario não cadastrado no sistema i9,'
                                       '\n procure um administrador', 'red')
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
                f'Acesso liberado - Usuario: {self.key}.', 'green')

            self.send_arduino(self.data[self.key][1])

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
        self.ImprimeLabel1('Digite seu id no campo a cima\n e pressione ENTER.')
        self.timer_limpa.stop()

    def ImprimeLabel1(self, text, color='black'):
        self.label_1.setStyleSheet(StyleLabel(color))
        self.label_1.setText(text)
        print(text)
        self.timer_limpa.start(2500)

    def CarregarJanela(self):
        # self.setGeometry(self.esquerda, self.topo, self.largura, self.altura)
        # self.setWindowTitle(self.titulo)
        self.showFullScreen()
        self.show()


if __name__ == "__main__":
    logging.info('Abrindo instancia.')
    try:
        App = QApplication(sys.argv)
    except Exception as exc:
        logging.error(exc)
    try:
        logging.info('Abrindo Janela')
        j = Janela()
    except Exception as exc:
        logging.error(exc)
    try:
        logging.info('Mostrando janela.')
        j.show()
    except Exception as exc:
        logging.error(exc)
    sys.exit(App.exec_())
