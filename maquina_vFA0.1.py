from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QWidget, QHBoxLayout, QFormLayout, QGridLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

from PyQt5.QtGui import QPixmap
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets


import ctypes

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

import requests
import json
import serial
import configparser
import logging
import time

# import the opencv library
import cv2
import face_recognition
import base64

# dir_local = '/home/i9/FacialProject/'
dir_local = '/home/pedro/Projetos/FacialProject/'


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



logging.info('Buscando dispositivos.')
logging.info('Tentando conexão com o leitor biometrico')



LETTERS1 = "qwertyuiop"
LETTERS2 = "asdfghjkl"
LETTERS3 = "zxcvbnm←"
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
    "←": QtCore.Qt.Key_Backspace,

    ".": QtCore.Qt.Key_Period,

    "Del": QtCore.Qt.Key_Delete,
    "Shift": QtCore.Qt.Key_Shift,
    "Enter": QtCore.Qt.Key_Enter,
    "Space": QtCore.Qt.Key_Space,
    "Caps": QtCore.Qt.Key_CapsLock,
}




def StyleLabel(cor='black'):
    backgroud_color = '#01556B'
    command = "QLabel {background-color: %s; font:bold; font-size:20px; color:%s ; text-align:center; padding :10px}" % (backgroud_color, cor)
    return command

class Janela(QMainWindow):
    def __init__(self, app, parent=None):
        super().__init__(parent)

        layout = QFormLayout()
        self.App = app
        self.backgroud_color = '#01556B'
        self.text_color = '#F1F1F1'
        self.green_logo = '#9bbb1f'
        self.red_color = '#ED4011'
        self.layout_butons = QHBoxLayout()
        self.grid = QGridLayout()
        self.setStyleSheet(f"background-color: {self.backgroud_color};")


        widget = QWidget()
        widget.setLayout(self.grid)
        self.setCursor(QtCore.Qt.BlankCursor) # esconde o cursor do mouse
        """ Botãoes """

        self.limpar = QPushButton('Limpar', self)
        self.limpar.setStyleSheet('QPushButton {background-color: %s; font:bold; font-size:20px; padding :10px; color:%s}' % (self.backgroud_color, self.text_color))  # estetica do botão
        self.limpar.clicked.connect(self.LimpaCampo)  # conecta o botão  com a função que ele vai rodar quando cicado

        self.ok_but = QPushButton('Ok', self)
        self.ok_but.setStyleSheet('QPushButton {background-color: %s; font:bold; font-size:20px; padding :10px; color:%s}' % (self.backgroud_color, self.text_color))  # estetica do botão
        self.ok_but.clicked.connect(self.BuscaDigital)  # conecta o botão  com a função que ele vai rodar quando cicado

        """LOGO"""
        self.label_image = QLabel(self)
        print(dir_local + 'MOBNOBG.png')
        self.pixmap = QPixmap(dir_local + 'MOBNOBG.png')

        self.label_image.setPixmap(self.pixmap)
        # /home/pedro/Projetos/FacialProject/MOBNOBG.png
        #self.label_image.resize(15,
                          #15)
        # self.label_image.setMaximumHeight(54)


        """Labels"""
        self.label_1 = QLabel(self)  # Self Indica que a janela criada no Carregar Janela é que sera iniciada

        self.label_1.setStyleSheet('padding :10px; background-color: %s' % (self.backgroud_color))
        self.label_1.setAlignment(QtCore.Qt.AlignCenter)
        self.label_1.setMaximumHeight(65)





        """Caixa Texto"""
        self.caixa_texto = QLineEdit(self)
        self.caixa_texto.setFocus()
        self.caixa_texto.setStyleSheet(f'padding :10px; color:{self.text_color}')
        self.caixa_texto.setMaximumHeight(65)


        self.caixa_texto.mousePressEvent = self.click_caixa_texto

        # codigo abaixo altera o tamanho da fonte
        self.fonte = self.caixa_texto.font()
        self.fonte.setPointSize(30)
        self.caixa_texto.setFont(self.fonte)

        # Chama função qando adiciona um id e aperta enter
        self.caixa_texto.returnPressed.connect(self.BuscaDigital)

        """ Layouts """

        self.grid.addWidget(self.label_image, 0, 0)#, alignment=QtCore.Qt.AlignTop)
        layout.addRow(self.caixa_texto)
        self.grid.addWidget(self.label_1, 2, 0)

        
        self.layout_butons.addWidget(self.limpar, 2)
        self.layout_butons.addWidget(self.ok_but, 2)

        self.grid.addLayout(layout, 1, 0, alignment=QtCore.Qt.AlignCenter)
        self.grid.addLayout(self.layout_butons, 3, 0, alignment=QtCore.Qt.AlignCenter)

        self.grid.setSpacing(1)
        self.setCentralWidget(widget)


        """ Timers """
        self.timer_limpa = QTimer(self)
        self.timer_limpa.timeout.connect(self.LimpaLabel)

        self.key = ''

        self.grid_layout = QtWidgets.QGridLayout(self)
        self.fileira_1 = QHBoxLayout()
        self.fileira_2 = QHBoxLayout()
        self.fileira_3 = QHBoxLayout()
        self.numbers_layout = QHBoxLayout()
        self.frame = QtWidgets.QFrame(self)


        """ inicia Janela principal """
        logging.info('iniciando interface')
        self.CarregarJanela()  # Inicia a Tela

        self.AtualizaJson()  # Atualiza o Json na abertura do programa
        self.keyboard()

        self.timer_busca_face = QTimer(self)


        
        


    def click_caixa_texto(self, mouseEvent):
        self.frame.show()



    def keyboard(self):
        sp = QSizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Fixed)
        sp.setVerticalPolicy(QSizePolicy.Fixed)





        numbers = NUMBERS
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.fileira_1 = QHBoxLayout()
        self.fileira_2 = QHBoxLayout()
        self.fileira_3 = QHBoxLayout()
        self.numbers_layout = QHBoxLayout()
        self.frame = QtWidgets.QFrame()

        width = 1024
        height = 600
        width = ((width/100)*90)
        height = ((height/100)*55)

        style_text = 'QToolButton { color:%s}' % (self.text_color)


        for i, letter in enumerate(LETTERS1):
            j = 1

            button = QtWidgets.QToolButton(
                text=letter,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,                
            )
            
            self.fonte_teclado = button.font()
            
            # button.setToolButtonStyle(style_text)
            # self.fonte_teclado.
                       
            
            self.fonte_teclado.setPointSize(25)

            button.setFixedWidth(round(width/(len(LETTERS1))))
            button.setFixedHeight(round(height/(4 + 1)))     
            button.setFont(self.fonte_teclado)
            button.setStyleSheet(style_text)
            

            self.fileira_1.addWidget(button, 2)
        self.grid_layout.addLayout(self.fileira_1, 1, 0, 1, len(numbers) + 1)

        for i, letter in enumerate(LETTERS2):
            j = 2

            button = QtWidgets.QToolButton(
                text=letter,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
            )


            self.fonte_teclado = button.font()
            self.fonte_teclado.setPointSize(25)
            button.setFixedWidth(round(width/(len(LETTERS2))))
            button.setFixedHeight(round(height/(4 + 1)))

            button.setFont(self.fonte_teclado)
            button.setSizePolicy(sp)
            button.setStyleSheet(style_text)


            self.fileira_2.addWidget(button, 2)

        self.grid_layout.addLayout(self.fileira_2 , 2, 0, 1, len(numbers)+ 1)

        for i, letter in enumerate(LETTERS3):
            j = 3
            button = QtWidgets.QToolButton(
                text=letter,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
            )
            self.fonte_teclado = button.font()            
            self.fonte_teclado.setPointSize(25)
            button.setFixedWidth(round(width/(len(LETTERS3))))
            button.setFixedHeight(round(height/(4 + 1)))

            button.setFont(self.fonte_teclado)
            button.setSizePolicy(sp)
            button.setStyleSheet(style_text)

            self.fileira_3.addWidget(button, 2)
        self.grid_layout.addLayout(self.fileira_3, 3, 0, 1, len(numbers) + 1)

        for i, number in enumerate(numbers):
            button = QtWidgets.QToolButton(
                text=number,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
                
            )
            self.fonte_teclado = button.font()
            self.fonte_teclado.setPointSize(25)
            

            button.setFont(self.fonte_teclado)
            button.setFixedWidth(round(width/(len(numbers))))
            button.setFixedHeight(round(height/(4 + 1)))


            button.setSizePolicy(sp)
            button.setStyleSheet(style_text)
            
            self.numbers_layout.addWidget(button, 2)
            





        self.grid_layout.addLayout(self.numbers_layout, 0, 0, 1, len(numbers)+1)#
        button.setFixedWidth(round(width / (len(numbers)+1)))
        button.setFixedHeight(round(height / (4 + 1)))
        button.setStyleSheet(style_text)

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
                                    data_dict[emp['ID']] = [list(emp['FingerPrintTemplate']), emp['BadgeNumber']]
                                else:
                                    data_dict[emp['ID']] = [None, emp['BadgeNumber']]
                            with open("template.json", "w") as arquivo:
                                json.dump(data_dict, arquivo, indent=4)
                            self.ImprimeLabel1('Biometrias atualizadas.', self.green_logo)
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
        if self.key:
            if self.key == "i9brgroup2390":
                self.ImprimeLabel1('Atualizando as digitais.')
                self.AtualizaJson()
                self.LimpaCampo()

            else:

                with open("template.json", "r") as file:
                    self.data = json.load(file)
                if self.key in self.data.keys():
                    self.remove_teclado()
                    self.ImprimeLabel1('Enquadre seu rosto na camera.')
                        
                    self.timer_busca_face.timeout.connect(self.run)
                    self.timer_busca_face.start(1)
                    self.LimpaCampo()
                else:
                    self.ImprimeLabel1('Usuario não cadastrado no sistema i9,'
                                       '\n procure um administrador', self.red_color)
                    self.LimpaCampo()


    

    def LimpaCampo(self):
        self.caixa_texto.clear()
        self.caixa_texto.setFocus()
        # self.remove_teclado()

    def LimpaLabel(self):
        self.ImprimeLabel1(f'Digite sua <b style="color:{self.green_logo};">matrícula</b>.')  # Pressione o campo a cima e 

        self.timer_limpa.stop()

    def ImprimeLabel1(self, text, color= None):
        if not color:
            color = self.text_color
        self.label_1.setStyleSheet(StyleLabel(color))
        # self.label_1.setStyleSheet()
        self.label_1.setText(text)
        self.label_1.adjustSize()
        print(text)
        self.timer_limpa.start(2500)


    def CarregarJanela(self):
        self.showFullScreen()
        self.show()


    def run(self):
            if self.key:
                # capture from web cam
                face_locations = []
                name_img = "foto.jpg"
                cap = cv2.VideoCapture(-1)
                cap.set(3, 240)
                cap.set(4, 120)
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                
                ret, cv_img = cap.read()
                face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
                count = 0
                while ret:
                    ret, cv_img = cap.read()
                    if ret:

                        face_locations = face_cascade.detectMultiScale(
                                cv_img,     
                                scaleFactor=1.3,
                                minNeighbors=5,    
                                minSize=(20, 20)
                            )

                        for (x, y, w, h) in face_locations:
                            # Draw rectangle around the face
                            cv2.rectangle(cv_img, (x, y), (x+w, y+h), (255, 255, 255), 3)

                        cv2.namedWindow("video", cv2.WND_PROP_FULLSCREEN)
                        # cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                        cv2.resizeWindow('video', 640,480)
                        cv2.resize(cv_img, (640, 480))
                        # cv2.moveWindow("video", 0, 300)
                        # cv2.moveWindow("video", 0, 200) 
                        cv2.imshow('video', cv_img)
                        if len(face_locations):
                            cv2.imwrite(name_img, cv_img) 
                            if count > 3:
                                if cap.isOpened():
                                    cap.release()
                                    cv2.destroyAllWindows()
                            else:            
                                count += 1
                        else: 
                            count = 0


                        if cv2.waitKey(1) & 0xFF == ord('q'):

                            if cap.isOpened():
                                cap.release()
                                cv2.destroyAllWindows()


                name_img = "foto.jpg"
                base64_img = None 
                if os.path.isfile(name_img):
                    file = open(name_img,'rb').read()
                    base64_img = base64.b64encode(file)
                        
                if base64_img:
                    url = 'https://www.mobcontrole.com.br/89bunzl9170_api/api/IdentityFace'

                    resp = requests.post(url, data={"matricula": str(self.key),
                                                        "data": base64_img
                                                        }, auth=('api.authentication', 'ApI2017AppcOntrOlE'), verify=False)
                    resp_text = bool(resp.text.replace('"', ''))
                    if resp_text:
                        self.ImprimeLabel1(
                            f'Acesso liberado - Usuario: {self.key}.', self.green_logo)                        
                        # self.send_arduino(self.data[self.key][1])
                        os.remove(name_img) 


                    else:
                        self.ImprimeLabel1(f'Reconhecimento facial não confere para o usuario: {self.key}', self.red_color)     
                        os.remove(name_img)        
                self.key = None
                self.timer_busca_face.stop()

                        



        
        

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
