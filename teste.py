from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QToolTip, QLabel, QLineEdit
import sys


class Janela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.topo = 100    #Altura que a janela vai aparecer
        self.esquerda = 100
        self.largura = 800
        self.altura = 600
        self.titulo = 'CMBio'


        """Botãoes"""
        botao1 = QPushButton('Botão 1', self)
        botao1.move(250, 250)  # define a posição do botão
        botao1.resize(150, 150)  # Define o tamanho do botão
        botao1.setStyleSheet('QPushButton {background-color: #f1f1f1; font:bold; font-size:20px}')  # estetica do botão
        botao1.clicked.connect(self.botao1_click)

        botao2 = QPushButton('Botão 2', self)
        botao2.move(500, 250)  # define a posição do botão
        botao2.resize(150, 150)  # Define o tamanho do botão
        botao2.setStyleSheet('QPushButton {background-color: #f1f1f1; font:bold; font-size:20px}')  # estetica do botão
        botao2.clicked.connect(self.botao2_click)  # conecta o botão  com a função que ele vai rodar quando cicado



        """Labels"""
        self.label_1 = QLabel(self)  # Self Indica que a janela criada no Carregar Janela é que sera iniciada
        self.label_1.setText('HelloWord')
        self.label_1.move(50, 50)
        self.label_1.resize(150, 150)  # Largura x Altura
        self.label_1.setStyleSheet('QLabel {background-color: #f1f1f1; font:bold; font-size:20px}')


        """Caixa Texto"""
        self.caixa_texto = QLineEdit(self)
        self.caixa_texto.move(50, 25)
        self.caixa_texto.resize(250, 50)  # Largura x Altura

        #iniciaJanela principal
        self.CarregarJanela()

    def LeTexto(self):
        conteudo = self.caixa_texto.text()

        print(conteudo)

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
sys.exit(aplicacao.exec_())