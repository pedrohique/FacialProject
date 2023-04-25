from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QWidget, QHBoxLayout, QFormLayout, QGridLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, QSize

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets

import ctypes

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

import requests
import json
import serial
import adafruit_fingerprint
import configparser
import logging


dir_local = '/home/pedro/BiometriaProject/maquina/'
# dir_local = '/home/i9/BiometriaProject/maquina/'


logging.basicConfig(filename= dir_local + '/logs/biometria.log', level=logging.DEBUG, filemode='a+',
                    format='%(asctime)s - %(levelname)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')




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
# while True:
#     try:
#         # logging.info('Buscando dispositivos conectados')
#         dir_linux = os.listdir('/dev/')
#         finger = busca_sensor(dir_linux)
#         if finger:
#             break
#         time.sleep(1)
#     except OSError as e:
#         print(e)
#         logging.error(e)
#         pass
#     except RuntimeError as run_err:
#         print(run_err)
#         logging.error(run_err)
#         pass
#
# logging.info('Tentando conexão com o arduino')
# while True:
#     try:
#         dir_linux = os.listdir('/dev/')
#         ser = busca_arduino(dir_linux)
#         if ser:
#             break
#         time.sleep(1)
#     except OSError as e:
#         logging.error(e)
#         pass
#     except RuntimeError as run_err:
#         logging.error(run_err)
#         pass


LETTERS1 = "qwertyuiop"
LETTERS2 = "asdfghjkl"
LETTERS3 = "zxcvbnm"
NUMBERS = "1234567890"
LUT = {
    "1": QtCore.Qt.Key_1,
    "2": QtCore.Qt.Key_2,
    "3": QtCore.Qt.Key_3,
    "4": QtCore.Qt.Key_4,
    "5": QtCore.Qt.Key_5,
    "6": QtCore.Qt.Key_6,
    "7": QtCore.Qt.Key_7,
    "8": QtCore.Qt.Key_8,
    "9": QtCore.Qt.Key_9,
    "0": QtCore.Qt.Key_0,
    "←": QtCore.Qt.Key_Backspace,

    "q": QtCore.Qt.Key_Q,
    "w": QtCore.Qt.Key_W,
    "e": QtCore.Qt.Key_E,
    "r": QtCore.Qt.Key_R,
    "t": QtCore.Qt.Key_T,
    "y": QtCore.Qt.Key_Y,
    "u": QtCore.Qt.Key_U,
    "i": QtCore.Qt.Key_I,
    "o": QtCore.Qt.Key_O,
    "p": QtCore.Qt.Key_P,
    "p": QtCore.Qt.Key_P,
    "'": QtCore.Qt.Key_Apostrophe,

    "a": QtCore.Qt.Key_A,
    "s": QtCore.Qt.Key_S,
    "d": QtCore.Qt.Key_D,
    "f": QtCore.Qt.Key_F,
    "g": QtCore.Qt.Key_G,
    "h": QtCore.Qt.Key_H,
    "j": QtCore.Qt.Key_J,
    "k": QtCore.Qt.Key_K,
    "l": QtCore.Qt.Key_L,

    "z": QtCore.Qt.Key_Z,
    "x": QtCore.Qt.Key_X,
    "c": QtCore.Qt.Key_C,
    "v": QtCore.Qt.Key_V,
    "b": QtCore.Qt.Key_B,
    "n": QtCore.Qt.Key_N,
    "m": QtCore.Qt.Key_M,

    "Q": QtCore.Qt.Key_Q,
    "W": QtCore.Qt.Key_W,
    "E": QtCore.Qt.Key_E,
    "R": QtCore.Qt.Key_R,
    "T": QtCore.Qt.Key_T,
    "Y": QtCore.Qt.Key_Y,
    "U": QtCore.Qt.Key_U,
    "I": QtCore.Qt.Key_I,
    "O": QtCore.Qt.Key_O,
    "P": QtCore.Qt.Key_P,
    "'": QtCore.Qt.Key_Apostrophe,

    "A": QtCore.Qt.Key_A,
    "S": QtCore.Qt.Key_S,
    "D": QtCore.Qt.Key_D,
    "F": QtCore.Qt.Key_F,
    "G": QtCore.Qt.Key_G,
    "H": QtCore.Qt.Key_H,
    "J": QtCore.Qt.Key_J,
    "K": QtCore.Qt.Key_K,
    "L": QtCore.Qt.Key_L,

    "Z": QtCore.Qt.Key_Z,
    "X": QtCore.Qt.Key_X,
    "C": QtCore.Qt.Key_C,
    "V": QtCore.Qt.Key_V,
    "B": QtCore.Qt.Key_B,
    "N": QtCore.Qt.Key_N,
    "M": QtCore.Qt.Key_M,

    ".": QtCore.Qt.Key_Period,

    "Del": QtCore.Qt.Key_Delete,
    "Shift": QtCore.Qt.Key_Shift,
    "Enter": QtCore.Qt.Key_Enter,
    "Space": QtCore.Qt.Key_Space,
    "Caps": QtCore.Qt.Key_CapsLock,
}




def StyleLabel(cor='black'):
    command = "QLabel {background-color: #f1f1f1; font:bold; font-size:20px; color:"+cor+"; text-align:center; padding :15px}"
    return command

class Janela(QMainWindow):
    def __init__(self, app, parent=None):
        super().__init__(parent)

        layout = QFormLayout()
        self.App = app

        self.layout_butons = QHBoxLayout()
        self.grid = QGridLayout()

        widget = QWidget()
        widget.setLayout(self.grid)

        """ Botãoes """

        self.limpar = QPushButton('Limpar', self)
        # self.limpar.resize(500, 75)  # Define o tamanho do botão
        self.limpar.setStyleSheet('QPushButton {background-color: #f1f1f1; font:bold; font-size:20px; padding :10px}')  # estetica do botão
        self.limpar.clicked.connect(self.LimpaCampo)  # conecta o botão  com a função que ele vai rodar quando cicado

        self.ok_but = QPushButton('Ok', self)
        # self.ok_but.resize(500, 75)  # Define o tamanho do botão
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
        # self.label_1.resize(500, 300)  # Largura x Altura
        self.label_1.setStyleSheet(StyleLabel())
        self.label_1.setStyleSheet('padding :15px')
        self.label_1.setAlignment(QtCore.Qt.AlignCenter)




        """Caixa Texto"""
        self.caixa_texto = QLineEdit(self)
        # self.caixa_texto.resize(500, 300)   # Largura x Altura
        self.caixa_texto.setStyleSheet('padding :15px')
        self.caps = False


        self.caixa_texto.mousePressEvent = self.click_caixa_texto

        # codigo abaixo altera o tamanho da fonte
        self.fonte = self.caixa_texto.font()
        self.fonte.setPointSize(50)
        self.caixa_texto.setFont(self.fonte)

        # Chama função qando adiciona um id e aperta enter
        self.caixa_texto.returnPressed.connect(self.BuscaDigital)

        """ Layouts """

        self.grid.addWidget(self.label_image, 0, 0, alignment=QtCore.Qt.AlignTop)
        layout.addRow(self.caixa_texto)
        self.grid.addWidget(self.label_1, 2, 0)
        self.layout_butons.addWidget(self.ok_but, 2)
        self.layout_butons.addWidget(self.limpar, 2)

        self.grid.addLayout(layout, 1, 0, alignment=QtCore.Qt.AlignCenter)
        self.grid.addLayout(self.layout_butons, 3, 0, alignment=QtCore.Qt.AlignCenter)


        self.grid.setContentsMargins(50, 50, 50, 50)
        self.grid.setSpacing(1)
        self.setCentralWidget(widget)


        """ Timers """
        self.timer_busca = QTimer(self)
        self.timer_limpa = QTimer(self)
        self.timer_busca.timeout.connect(self.ValidaDigital)
        self.timer_limpa.timeout.connect(self.LimpaLabel)
        self.timerDigital = QTimer(self)

        self.key = ''

        self.grid_layout = QtWidgets.QGridLayout(self)
        self.fileira_1 = QHBoxLayout()
        self.fileira_2 = QHBoxLayout()
        self.fileira_3 = QHBoxLayout()
        self.numbers_layout = QHBoxLayout()
        self.frame = QtWidgets.QFrame(self)
        # self.frame.setMinimumSize(QSize(50, 50))
        # self.frame.setSizePolicy(
        #     QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)


        """ inicia Janela principal """
        logging.info('iniciando interface')
        self.CarregarJanela()  # Inicia a Tela

        self.AtualizaJson()  # Atualiza o Json na abertura do programa
        self.keyboard()




    def click_caixa_texto(self, mouseEvent):
        # self.ImprimeLabel1('caixa de texto clicada')
        self.frame.show()



    def keyboard(self):
        letters = (LETTERS1, LETTERS2, LETTERS3)
        sp = QSizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Fixed)
        sp.setVerticalPolicy(QSizePolicy.Fixed)
        # sp.setHorizontalPolicy(QSizePolicy.Expanding)
        # sp.setVerticalPolicy(QSizePolicy.Expanding)




        numbers = NUMBERS # + "←"
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.fileira_1 = QHBoxLayout()
        self.fileira_2 = QHBoxLayout()
        self.fileira_3 = QHBoxLayout()
        # self.teclado_layout = QtWidgets.QGridLayout(self)
        self.numbers_layout = QHBoxLayout()
        self.frame = QtWidgets.QFrame()
        self.style_board = """width: 100%;
                            Height: 70%;
                            padding:1px
                            
                            """

        width = 1366
        height = 768
        # app = self.App
        # screen_resolution = app.desktop().screenGeometry()
        # width, height = screen_resolution.width(), screen_resolution.height()
        width = ((width/100)*90)
        height = ((height/100)*30)





        for i, letter in enumerate(LETTERS1):
            j = 1
            if self.caps:
                letter = letter.upper()
            button = QtWidgets.QToolButton(
                text=letter,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
            )

            self.fonte_teclado = button.font()
            self.fonte_teclado.setPointSize(25)

            button.setFixedWidth(round(width/(len(LETTERS1) + 3)))
            button.setFixedHeight(round(height/(4 + 1)))


            button.setFont(self.fonte_teclado)
            # button.setSizePolicy(sp)

            self.fileira_1.addWidget(button, 2)
        self.grid_layout.addLayout(self.fileira_1, 1, 0, 1, len(numbers))  # ,  alignment=QtCore.Qt.AlignCenter)

        for i, letter in enumerate(LETTERS2):
            j = 2
            if self.caps:
                letter = letter.upper()
            button = QtWidgets.QToolButton(
                text=letter,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
            )

            #button.setStyleSheet(self.style_board)

            self.fonte_teclado = button.font()
            self.fonte_teclado.setPointSize(25)
            button.setFixedWidth(round(width/(len(LETTERS2) + 3)))
            button.setFixedHeight(round(height/(4 + 1)))

            button.setFont(self.fonte_teclado)
            button.setSizePolicy(sp)


            self.fileira_2.addWidget(button, 2)
            # self.grid_layout.addWidget(button, j, i, 1, 1)
        self.grid_layout.addLayout(self.fileira_2 , 2, 0, 1, len(numbers))# , alignment=QtCore.Qt.AlignCenter)

        for i, letter in enumerate(LETTERS3):
            j = 3
            if self.caps:
                letter = letter.upper()
            button = QtWidgets.QToolButton(
                text=letter,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
            )
            self.fonte_teclado = button.font()
            self.fonte_teclado.setPointSize(25)
            button.setFixedWidth(round(width/(len(LETTERS3) + 3)))
            button.setFixedHeight(round(height/(4 + 1)))

            button.setFont(self.fonte_teclado)
            button.setSizePolicy(sp)

            self.fileira_3.addWidget(button, 2)
        self.grid_layout.addLayout(self.fileira_3, 3, 0, 1, len(numbers))# , alignment=QtCore.Qt.AlignCenter)

        for i, number in enumerate(numbers):
            j=0
            button = QtWidgets.QToolButton(
                text=number,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
            )
            self.fonte_teclado = button.font()
            self.fonte_teclado.setPointSize(25)

            button.setFont(self.fonte_teclado)
            button.setFixedWidth(round(width/(len(numbers) + 3)))
            button.setFixedHeight(round(height/(4 + 1)))

            button.setSizePolicy(sp)
            self.numbers_layout.addWidget(button, 2)


        button_backspace = QtWidgets.QToolButton(
                text="←",
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
            )

        button_backspace.setFixedWidth(round(width / (len(numbers))))
        button_backspace.setFixedHeight(round(height / (4 + 1)))

        self.fonte_teclado = button_backspace.font()
        self.fonte_teclado.setPointSize(25)


        button_backspace.setFont(self.fonte_teclado)
        button_backspace.setSizePolicy(sp)


        self.grid_layout.addLayout(self.numbers_layout, 0, 0, 1, len(numbers))# , alignment=QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(button_backspace, 0, len(numbers)+1, 1, 2) #.addWidget(button_backspace, 2)
        for i, text in enumerate(("Del", "Shift")):
            i += 1
            button = QtWidgets.QToolButton(
                text=text, clicked=self.onClicked, focusPolicy=QtCore.Qt.NoFocus
            )
            # button.setFixedSize(90, 70)

            self.fonte_teclado = button.font()
            self.fonte_teclado.setPointSize(25)

            button.setFont(self.fonte_teclado)
            button.setSizePolicy(sp)
            button.setFixedWidth(round(width / (len(numbers))))
            button.setFixedHeight(round(height / (4 + 1)))
            # button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            #button.setStyleSheet(self.style_board)
            button.setSizePolicy(sp)
            self.grid_layout.addWidget(button, i, len(numbers)+1)


        button = QtWidgets.QToolButton(
            text="Caps", clicked=self.onClicked, focusPolicy=QtCore.Qt.NoFocus
        )
        self.fonte_teclado = button.font()
        self.fonte_teclado.setPointSize(25)
        # button.setStyleSheet(self.style_board)

        button.setFont(self.fonte_teclado)
        button.setSizePolicy(sp)

        self.grid_layout.addWidget(button, 3, 11)  #, 1, 2
        button.setFixedWidth(round(width / (len(numbers))))
        button.setFixedHeight(round(height / (4 + 1)))

        self.grid_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.frame.setLayout(self.grid_layout)



        self.frame.setMinimumSize(round(width), round(height))
        self.frame.setSizePolicy(sp)

        self.grid.addWidget(self.frame, 4, 0, alignment=QtCore.Qt.AlignHCenter)
        self.frame.hide()


    @QtCore.pyqtSlot()
    def onClicked(self):
        button = self.sender()
        if button is None:
            return
        widget = QtWidgets.QApplication.focusWidget()

        text = button.text()


        key = LUT[text]
        if self.caps:
            text = text.upper()
        if text in ("Del", "Shift", "Enter", "Space", "Caps", "CAPS"):
            if text in ("Shift", "Enter"):
                text = ""
            elif text == "Space":
                text = " "
            elif text == "Del":
                text = chr(0x7F)


            elif text == "Caps":
                self.caps = True
                self.frame.close()
                self.keyboard()
                self.frame.show()
                text = ''
            elif text == 'CAPS':
                self.caps = False
                self.frame.close()
                self.keyboard()
                self.frame.show()
                text = ''



        event = QtGui.QKeyEvent(
            QtCore.QEvent.KeyPress, key, QtCore.Qt.NoModifier, text
        )
        QtCore.QCoreApplication.postEvent(widget, event)

    def remove_teclado(self):
        self.frame.hide()

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
            print(oe)
            logging.error(oe)
            pass
        except RuntimeError as run_err:
            print(run_err)
            logging.error(run_err)
            pass
        except TypeError as te:
            print(te)
            logging.error(te)
            pass
        except ConnectionError as ce:
            print(ce)
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
            if self.key == ".1234.":
                self.ImprimeLabel1('Atualizando as digitais.')
                self.AtualizaJson()
                self.caixa_texto.clear()
                # self.timer1.start(1000)

            else:

                with open("template.json", "r") as file:
                    self.data = json.load(file)
                if self.key in self.data.keys():
                    if self.data[self.key][0]:
                        self.ImprimeLabel1('Coloque sua DIGITAL.')
                        self.timer_busca.start(1)
                        self.remove_teclado()
                    else:
                        # print('Digital não cadastrada.')
                        self.ImprimeLabel1('Digital não cadastrada.', 'red')
                        self.caixa_texto.clear()
                        self.remove_teclado()
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
        self.remove_teclado()

    def LimpaLabel(self):
        self.ImprimeLabel1('Digite seu id no campo a cima e pressione ENTER.')
        self.timer_limpa.stop()

    def ImprimeLabel1(self, text, color='black'):
        self.label_1.setStyleSheet(StyleLabel(color))
        self.label_1.setText(text)
        self.label_1.adjustSize()
        print(text)
        self.timer_limpa.start(2500)

    def CarregarJanela(self):
        self.showFullScreen()
        self.show()


if __name__ == "__main__":
    logging.info('Abrindo instancia.')
    try:
        App = QApplication(sys.argv)
    except Exception as exc:
        logging.error(exc)
        print(exc)
    try:
        logging.info('Abrindo Janela')
        j = Janela(App)
    except Exception as exc:
        logging.error(exc)
        print(exc)
    try:
        logging.info('Mostrando janela.')
        j.show()
    except Exception as exc:
        logging.error(exc)
        print(exc)
    sys.exit(App.exec_())
