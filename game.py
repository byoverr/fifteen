import sys
import random
import time

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QLabel, QFrame, QGridLayout, QSizePolicy
from PyQt5.QtCore import QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QFont


class Game(QWidget):
    timeout = pyqtSignal()

    def __init__(self):
        super().__init__()

        # стандартный размер поля
        self.size = 4

        self.playable = False
        self.bd = None

        self.time = 0
        self.timeInterval = 1000

        # список с рандомными числами
        self.seq = list(range(1, self.size ** 2))
        random.shuffle(self.seq)

        # создаём пустое поле
        self.empty_num = ' '
        self.seq.append(self.empty_num)

        # список с числами для метода solve()
        self.goal = list(range(1, self.size ** 2))

        self.grid_layoutWidget = QWidget(self)
        self.grid_layoutWidget.setGeometry(QRect(20, 80, 400, 400))

        self.grid_layout = QGridLayout(self.grid_layoutWidget)
        self.setLayout(self.grid_layout)

        self.initUI()

    def initUI(self):
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle('Fifteen')

        font = QFont('Arial', 20)

        # Кнопка "Новая игра"
        self.btn_new_game = QPushButton('Новая игра', self)
        self.btn_new_game.resize(100, 40)
        self.btn_new_game.move(20, 20)
        self.btn_new_game.clicked.connect(self.new_game)

        # Кнопка "Решить"
        self.btn_solve = QPushButton('Решить', self)
        self.btn_solve.resize(100, 40)
        self.btn_solve.move(120, 20)
        self.btn_solve.clicked.connect(self.solve)

        # Кнопка "Изменить размер"
        self.btn_change_size = QPushButton('Изменить размер', self)
        self.btn_change_size.resize(130, 40)
        self.btn_change_size.move(220, 20)
        self.btn_change_size.clicked.connect(self.change_size)

        # label для вывода таймера
        self.time_label = QLabel(self)
        self.time_label.move(370, 20)
        self.time_label.resize(100, 40)
        self.time_label.setFont(font)

        # таймер
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTime)

        # рамка
        self.frame = QFrame(self)
        self.frame.setGeometry(25, 70, 300, 300)
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(5)


        #for i in range()

    def new_game(self):
        self.reset()
        self.timer.start()
        self.play_game()


    def solve(self):
        pass

    def change_size(self):
        size, ok_pressed = QInputDialog.getInt(
            self, 'Введите размер поля', 'Какое поле размером n*n вы хотите?',
            4, 3, 8, 1)
        if ok_pressed:
            self.size = size

    def displayTime(self):
        self.time += 1
        self.settimer(self.time)

    def settimer(self, int):
        self.time = int
        self.time_label.setText(
            time.strftime('%M:%S', time.gmtime(self.time)))

    def reset(self):
        self.time = 0
        self.settimer(self.time)

    def play_game(self):
        self.lot = [str(i) for i in range(1, 16)] + ['']

        for r in range(4):
            for c in range(4):
                txt = self.lot[r * c]
                game_btn = QPushButton(txt)
                #game_btn.clicked.connect(self.clicked)
                button_font = QFont('Arial', 14)
                game_btn.setFont(button_font)
                game_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.grid_layout.addWidget(game_btn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    ex.show()
    sys.exit(app.exec())
