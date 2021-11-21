import sys
import random
import time

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, \
    QLabel, QFrame, QErrorMessage, QMainWindow, QMessageBox, QDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QIcon
from PyQt5 import QtMultimedia, QtWidgets, QtCore, QtGui

import sqlite3
from records import Record


class RecordsDialog(QDialog):
    """ Класс диалогового окна рекордов """

    def __init__(self, name):
        QDialog.__init__(self)
        self.setWindowTitle(name)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 400)
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 380, 380))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Имя", "Время(сек)", "Кол-во ходов"])
        self.tableWidget.setStyleSheet("background-color: white; color: black;")
        try:
            con = sqlite3.connect("records.db")
            req = "SELECT * FROM records ORDER BY time"
            cur = con.cursor()
            res = cur.execute(req).fetchall()
            self.tableWidget.setRowCount(len(res))
            for j, result in enumerate(res):
                s = result[-1]
                result = list(result[1:])
                result.append(s)
                for i, val in enumerate(result):
                    self.tableWidget.setItem(j, i, QTableWidgetItem(str(val)))
        except Exception as e:
            print(e)


class Records(QMainWindow, Record):
    """ Запись в таблицу рекордов """
    def __init__(self, time, count):
        super().__init__()
        self.t = time
        self.c = count
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.apply)
        self.buttonBox.rejected.connect(self.cancel)

    def apply(self):
        try:
            nick = self.lineEdit.text()
            if nick:
                con = sqlite3.connect('records.db')
                cur = con.cursor()

                result_names = cur.execute(f'''SELECT name FROM records''').fetchall()
                names = [j for elem in result_names for j in elem]

                result_id = cur.execute(f'''SELECT id FROM records''').fetchall()
                ids = [j for elem in result_id for j in elem]
                last_id = ids[-1] + 1

                if nick in names:
                    times = cur.execute(f'''SELECT time FROM records WHERE name = '{nick}' ''').fetchall()
                    time = [j for elem in times for j in elem][-1]
                    if self.t < time:
                        cur.execute(f'''UPDATE records SET count = {self.c}, time = {self.t} WHERE name = '{nick}' ''')
                        con.commit()
                        self.showDialog()
                    else:
                        self.showDialog(False)
                else:
                    cur.execute(f'''INSERT INTO records(id, name, time, count) 
                    VALUES ('{last_id}', '{nick}', {self.t}, {self.c})''')
                    con.commit()
                    self.showDialog()
                print(cur.execute(f'''SELECT * FROM records''').fetchall())
                con.close()
            else:
                self.er.showMessage('Вы не ввели ник')
        except Exception as e:
            print(e)

    def cancel(self):
        self.hide()


class Game(QWidget):
    timeout = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.bd = None
        self.flag_win = False

        # загружаем музыку
        self.load_mp3('click.mp3')

        self.time = 0
        self.timeInterval = 1000

        # стандартный размер поля
        self._size = 4

        self.n = 0
        self.create_bd()

        font = QFont('Arial', 10)

        # Кнопка "Новая игра"
        self.btn_new_game = QPushButton('Новая игра', self)
        self.btn_new_game.resize(100, 40)
        self.btn_new_game.move(20, 20)
        self.btn_new_game.setFont(font)
        self.btn_new_game.clicked.connect(self.new_game)

        # Кнопка "Решить"
        self.btn_solve = QPushButton('Рекорды', self)
        self.btn_solve.resize(100, 40)
        self.btn_solve.move(120, 20)
        self.btn_solve.setFont(font)
        self.btn_solve.clicked.connect(self.recshow)

        # Кнопка "Изменить размер"
        self.btn_change_size = QPushButton('Изменить размер', self)
        self.btn_change_size.resize(130, 40)
        self.btn_change_size.move(220, 20)
        self.btn_change_size.setFont(font)
        self.btn_change_size.clicked.connect(self.change_size)

        # label для вывода таймера
        self.time_label = QLabel(self)
        self.time_label.move(370, 10)
        self.time_label.resize(100, 20)
        self.time_label.setFont(QFont('Arial', 20))

        # label для вывода кол-ва шагов
        self.count_label = QLabel(self)
        self.count_label.move(370, 40)
        self.count_label.resize(140, 20)
        self.count_label.setFont(QFont('Arial', 20))
        self.count_label.setText(f'Moves: {self.n}')

        # таймер
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTime)

        # рамка
        self.frame = QFrame(self)
        self.frame.setGeometry(25, 70, 370, 370)
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(5)

        self.setWindowTitle('Fifteen')
        self.setWindowIcon(QIcon('fifteen-web.png'))
        self.setupUI()

    def setupUI(self):
        self.setGeometry(500, 300, 500 + ((self._size - 3) * 30), 500 + ((self._size - 3) * 30))
        self.frame.setGeometry(25, 70, 300 + ((self._size - 3) * 50), 300 + ((self._size - 3) * 50))
        self.play_game()

    # создаёт доску
    def create_bd(self):

        # список с рандомными числами
        self.seq = [str(i) for i in range(1, self._size ** 2)] + ['']

        random.shuffle(self.seq)

        # игровое поле
        self.bd = []
        i = 0
        for r in range(self._size):
            row = []
            for c in range(self._size):
                row.append(self.board_create(r, c, self.seq[i]))
                i += 1
            self.bd.append(row)

        # список с числами для метода solve()
        self.goal_lst = [str(i) for i in range(1, self._size ** 2)] + ['']

        self.goal_bd = []
        for i in range(self._size):
            lst = []
            for j in range(self._size):
                lst.append(self.goal_lst.pop(0))
            self.goal_bd.append(lst)

    def get_square(self, r, c):
        return self.bd[r][c]

    # проверка на правильно сложенную доску пятнашек
    def game_won(self):
        self.goal_lst = [str(i) for i in range(1, self._size ** 2)] + ['']
        i = 0
        for r in range(self._size):
            for c in range(self._size):
                nm, txt, btn = self.bd[r][c]
                if txt != self.goal_lst[i]:
                    return False
                i += 1
        return True

    def board_create(self, row, col, txt):
        self.row = row
        self.col = col
        self.name = 'btn' + str(row) + str(col)
        self.txt = txt
        self.btn = None
        return [self.name, self.txt, self.btn]

    # загрузка медиа
    def load_mp3(self, filename):
        media = QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)

    # новая игра
    def new_game(self):
        self.reset()
        self.timer.start()
        self.n = 0
        self.count_label.setText(f'Moves: {self.n}')
        self.reset_bd()
        self.create_bd()
        self.setupUI()

    # метод для кнопки "Решить игру"
    def recshow(self):
        self.recs = RecordsDialog('Рекорды')
        self.recs.show()

    # метод для кнопки "Изменить размер"
    def change_size(self):
        size, ok_pressed = QInputDialog.getInt(
            self, 'Введите размер поля', 'Какое поле размером n*n вы хотите?',
            4, 3, 8, 1)
        if ok_pressed:
            self.reset_bd()
            self._size = size
            self.reset()
            self.timer.start()
            self.n = 0
            self.count_label.setText(f'Moves: {self.n}')
            self.create_bd()
            self.setupUI()

    def displayTime(self):
        self.time += 1
        self.settimer(self.time)

    def settimer(self, int):
        self.time = int
        self.time_label.setText(
            time.strftime('%M:%S', time.gmtime(self.time)))

    # сброс таймера
    def reset(self):
        self.time = 0
        self.settimer(self.time)

    # удаляет доску
    def reset_bd(self):
        try:
            for r in range(self._size):
                for c in range(self._size):
                    nm, txt, btn = self.bd[r][c]
                    btn.deleteLater()
                    btn = None
                    self.bd[r][c] = [nm, txt, btn]
            self.bd = []
        except Exception as e:
            print(e)

    def show_bd(self):
        if self.flag_win:
            self.rc = Records(self.time, self.n)
            self.rc.show()

    # создаёт кнопки
    def play_game(self):
        try:
            objx = 29  # позиция x в рамке
            objy = 74  # позиция y в рамке
            width = self.frame.width() // self._size - 1
            height = self.frame.height() // self._size - 1

            for r in range(self._size):
                for c in range(self._size):
                    nm, txt, btn = self.bd[r][c]
                    game_btn = QPushButton(txt, self)
                    game_btn.move(objx, objy)
                    game_btn.resize(width, height)
                    game_btn.clicked.connect(lambda ch, name=nm: self.clicked(name))
                    button_font = QFont('Arial', 14)
                    game_btn.setFont(button_font)
                    game_btn.show()
                    objx += width
                    self.bd[r][c] = [nm, txt, game_btn]
                objx = 28
                objy += height

        except Exception as e:
            print(e)

    # метод для кнопок игрового поля
    def clicked(self, nm):
        try:
            # dialog для неправильного хода
            error_dialog = QErrorMessage(self)
            error_dialog.setWindowTitle('Error')

            # координаты поля
            r, c = int(nm[3]), int(nm[4])
            nm_fr, txt_fr, btn_fr = self.bd[r][c]

            if not txt_fr:
                error_dialog.showMessage("Вы нажали на пустую плитку")
                return

            # возможные ходы
            adjs = [(r - 1, c), (r, c - 1), (r, c + 1), (r + 1, c)]
            for x, y in adjs:
                if 0 <= x <= self._size - 1 and 0 <= y <= self._size - 1:
                    nm_to, txt_to, btn_to = self.bd[x][y]
                    if not txt_to:
                        nm, txt, btn = self.bd[x][y]
                        self.bd[x][y] = [nm, txt_fr, btn]
                        nm2, txt2, btn2 = self.bd[r][c]
                        self.bd[r][c] = [nm2, txt_to, btn2]
                        btn_to.setText(txt_fr)
                        btn_fr.setText(txt_to)
                        self.player.play()
                        self.n += 1
                        self.count_label.setText(f'Moves: {self.n}')
                        if self.game_won():
                            self.timer.stop()
                            self.flag_win = True
                            self.show_bd()
                        return

            error_dialog.showMessage("Вы не можете двигать эту плитку")
            return
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    ex.show()
    sys.exit(app.exec())