

from PyQt5 import QtCore, QtGui, QtWidgets

LETTERS = "abcdefghijklmnopqrstuvwxyz"
NUMBERS = "1234567890"
LUT = {
    "a": QtCore.Qt.Key_A,
    "b": QtCore.Qt.Key_B,
    "c": QtCore.Qt.Key_C,
    "d": QtCore.Qt.Key_D,
    "e": QtCore.Qt.Key_E,
    "f": QtCore.Qt.Key_F,
    "g": QtCore.Qt.Key_G,
    "h": QtCore.Qt.Key_H,
    "i": QtCore.Qt.Key_I,
    "j": QtCore.Qt.Key_J,
    "k": QtCore.Qt.Key_K,
    "l": QtCore.Qt.Key_L,
    "m": QtCore.Qt.Key_M,
    "n": QtCore.Qt.Key_N,
    "o": QtCore.Qt.Key_O,
    "p": QtCore.Qt.Key_P,
    "q": QtCore.Qt.Key_Q,
    "r": QtCore.Qt.Key_R,
    "s": QtCore.Qt.Key_S,
    "t": QtCore.Qt.Key_T,
    "u": QtCore.Qt.Key_U,
    "v": QtCore.Qt.Key_V,
    "w": QtCore.Qt.Key_W,
    "x": QtCore.Qt.Key_X,
    "y": QtCore.Qt.Key_Y,
    "z": QtCore.Qt.Key_Z,
    "Del": QtCore.Qt.Key_Delete,
    "Shift": QtCore.Qt.Key_Shift,
    "Enter": QtCore.Qt.Key_Enter,
    "Space": QtCore.Qt.Key_Space,
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
    ".": QtCore.Qt.Key_Period,
    "'": QtCore.Qt.Key_Apostrophe,
}


class KeyBoard(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        letters = LETTERS[: len(LETTERS) // 2], LETTERS[len(LETTERS) // 2 :]
        numbers = NUMBERS + ".'"

        grid_layout = QtWidgets.QGridLayout(self)

        for i, (a, b) in enumerate(zip(*letters)):
            for j, letter in enumerate((a, b)):
                button = QtWidgets.QToolButton(
                    text=letter,
                    clicked=self.onClicked,
                    focusPolicy=QtCore.Qt.NoFocus,
                )
                button.setFixedSize(40, 35)
                grid_layout.addWidget(button, j, i)

        for i, number in enumerate(numbers):
            button = QtWidgets.QToolButton(
                text=number,
                clicked=self.onClicked,
                focusPolicy=QtCore.Qt.NoFocus,
            )
            button.setFixedSize(40, 35)
            grid_layout.addWidget(button, 2, i)

        for i, text in enumerate(("Del", "Shift")):
            button = QtWidgets.QToolButton(
                text=text, clicked=self.onClicked, focusPolicy=QtCore.Qt.NoFocus
            )
            button.setFixedSize(40, 35)
            grid_layout.addWidget(button, i, 13)

        button = QtWidgets.QToolButton(
            text="Enter", clicked=self.onClicked, focusPolicy=QtCore.Qt.NoFocus
        )
        button.setFixedSize(85, 35)
        grid_layout.addWidget(button, 2, 12, 1, 2)

        button = QtWidgets.QToolButton(
            text="Space", clicked=self.onClicked, focusPolicy=QtCore.Qt.NoFocus
        )
        button.setFixedSize(100, 35)
        grid_layout.addWidget(
            button, 3, 0, 1, 13, alignment=QtCore.Qt.AlignCenter
        )
        self.setFixedSize(self.sizeHint())

    @QtCore.pyqtSlot()
    def onClicked(self):
        button = self.sender()
        if button is None:
            return
        widget = QtWidgets.QApplication.focusWidget()

        text = button.text()
        key = LUT[text]
        if text in ("Del", "Shift", "Enter", "Space"):
            if text in ("Shift", "Enter"):
                text = ""
            elif text == "Space":
                text = " "
            elif text == "Del":
                text = chr(0x7F)
        event = QtGui.QKeyEvent(
            QtCore.QEvent.KeyPress, key, QtCore.Qt.NoModifier, text
        )
        QtCore.QCoreApplication.postEvent(widget, event)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        font = QtGui.QFont("Arial", 16)

        user_id_label = QtWidgets.QLabel("User ID:", font=font)
        user_id_lineedit = QtWidgets.QLineEdit(font=font)

        pass_id_label = QtWidgets.QLabel("Pass:", font=font)
        pass_id_lineedit = QtWidgets.QLineEdit(font=font)

        keyboard = KeyBoard()

        flay = QtWidgets.QFormLayout(central_widget)
        flay.addRow(user_id_label, user_id_lineedit)
        flay.addRow(pass_id_label, pass_id_lineedit)
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(keyboard, alignment=QtCore.Qt.AlignCenter)
        flay.addRow(lay)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

