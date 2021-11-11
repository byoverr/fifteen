import sys
import random
import time

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QLabel, QFrame, QMessageBox
from PyQt5.QtCore import QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QFont


class Board:
    def __init__(self):

        # стандартный размер поля
        self.size = 4

        self.create_bd()

        # список с числами для метода solve()
        self.goal = [str(i) for i in range(1, self.size ** 2)] + ['']

    def create_bd(self):

        # список с рандомными числами
        self.seq = [str(i) for i in range(1, self.size ** 2)] + ['']

        random.shuffle(self.seq)

        # игровое поле
        self.bd = []
        i = 0
        for r in range(self.size):
            row = []
            for c in range(self.size):
                row.append(Square(r, c, self.seq[i]))
                i += 1
            self.bd.append(row)

    def get_item(self, r, c):
        return self.bd[r][c].get()

    def get_square(self, r, c):
        return self.bd[r][c]

    def game_won(self):
        i = 0
        for r in range(self.size):
            for c in range(self.size):
                nm, txt, btn = self.get_item(r, c)
                if txt != self.goal[i]:
                    return False
                i += 1
        return True


class Square:
    def __init__(self, row, col, txt):
        self.row = row
        self.col = col
        self.name = 'btn' + str(row) + str(col)
        self.txt = txt
        self.btn = None

    def get(self):
        return [self.name, self.txt, self.btn]

    def set_btn(self, btn):
        self.btn = btn

    def set_txt(self, txt):
        self.txt = txt


class Game(QWidget, Board):
    timeout = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.playable = False
        self.bd = None

        self.time = 0
        self.timeInterval = 1000


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
        self.frame.setGeometry(25, 70, 300 + ((self.size - 3) * 50), 300 + ((self.size - 3) * 50))
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(5)

        self.initUI()

    def initUI(self):
        self.setGeometry(50, 50, 500 + ((self.size - 3) * 50), 500 + ((self.size - 3) * 50))
        self.setWindowTitle('Fifteen')

        self.play_game()

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
            self.create_bd()

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
        try:
            self.bd = Board()
            print(self.bd)
            objx = 28  # позиция x в рамке
            objy = 73  # позиция y в рамке
            width = self.frame.width() // self.size - 2
            height = self.frame.height() // self.size - 2

            for r in range(self.size):
                for c in range(self.size):
                    nm, txt, btn = self.bd.get_item(r, c)
                    game_btn = QPushButton(txt, self)
                    game_btn.move(objx, objy)
                    game_btn.resize(width, height)
                    game_btn.clicked.connect(lambda ch, name=nm: self.clicked(name))
                    button_font = QFont('Arial', 14)
                    game_btn.setFont(button_font)
                    objx += width
                    sq = self.bd.get_square(r, c)
                    sq.set_btn(game_btn)
                objx = 28
                objy += height

        except Exception as e:
            print(e)

    def clicked(self, nm):
        r, c = int(nm[3]), int(nm[4])
        nm_fr, txt_fr, btn_fr = self.bd.get_item(r, c)

        if not txt_fr:
            print('вы нажали на пустую плитку')
            return

        adjs = [(r - 1, c), (r, c - 1), (r, c + 1), (r + 1, c)]
        for x, y in adjs:
            if 0 <= x <= self.size - 1 and 0 <= y <= self.size - 1:
                nm_to, txt_to, btn_to = self.bd.get_item(x, y)
                if not txt_to:
                    sq = self.bd.get_square(x, y)
                    sq.set_txt(txt_fr)
                    sq = self.bd.get_square(r, c)
                    sq.set_txt(txt_to)
                    btn_to.setText(txt_fr)
                    btn_fr.setText(txt_to)
                    if self.bd.game_won():
                        print('вы выйграли!')
                    return

        print('вы не можете двигать эту плитку')
        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    ex.show()
    sys.exit(app.exec())