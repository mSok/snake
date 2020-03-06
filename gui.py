""" Simple Snake Game - for test GUI QT Widgets
"""

import sys
import random
import logging

from PySide2.QtWidgets import QApplication
from PySide2 import QtGui, QtCore, QtWidgets

logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(name)s — %(message)s', level=logging.INFO)

BGCOLOR = '#A9F5D0'  # css style
SNAKECOLOR = QtGui.QColor(255, 128, 0, 200)
DEFAULT_SPEED = 100
START_POS = ((0, 2), (0, 3), (0, 4))


class Snake(QtWidgets.QWidget):
    def __init__(self):
        super(Snake, self).__init__()
        self.initUI()
        self.snakeArray = list(START_POS)
        self.snakeSize = 12
        self.timer = QtCore.QBasicTimer()
        self.newGame()

    def initUI(self):
        self.highscore = 0
        self.setStyleSheet(f"QWidget {{ background: {BGCOLOR} }}")
        self.setFixedSize(300, 300)
        self.setWindowTitle('Snake')
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawSnake(qp)
        self.drawBoard(qp)
        self.scoreText(qp)
        self.spawnApple(qp)
        qp.end()

    def drawSnake(self, qp: QtGui.QPainter):
        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.setBrush(SNAKECOLOR)
        for i in self.snakeArray:
            qp.drawRect(
                (i[0]) * self.snakeSize,
                (i[1]) * self.snakeSize,
                self.snakeSize,
                self.snakeSize
            )

    def drawBoard(self, qp: QtGui.QPainter):
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QtGui.QColor(25, 80, 0, 160))
        qp.drawRect(0, 0, 300, 24)
        qp.drawRect(0, 300 - 24, 300, 300)

    def scoreText(self, qp: QtGui.QPainter):
        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(8, 17, "SCORE: " + str(self.score))
        qp.drawText(8, 300 - 8, "P - pause game / SPASE - start new game")
        qp.drawText(185, 17, "HIGHSCORE: " + str(self.highscore))

    def direction(self, direction: str):
        if not self.isPaused:
            head = self.snakeArray[-1]
            if direction == 'RIGHT' and self.lastKeyPress != 'LEFT' and not self.collision((head[0] + 1, head[1])):
                self.snakeArray.pop(0)
                head = (head[0] + 1, head[1])
                self.snakeArray.append(head)
                self.lastKeyPress = direction
            elif direction == 'LEFT' and self.lastKeyPress != 'RIGHT' and not self.collision((head[0] - 1, head[1])):
                self.snakeArray.pop(0)
                head = (head[0] - 1, head[1])
                self.snakeArray.append(head)
                self.lastKeyPress = direction
            elif direction == 'UP' and self.lastKeyPress != 'DOWN' and not self.collision((head[0], head[1] - 1)):
                self.snakeArray.pop(0)
                head = (head[0], head[1] - 1)
                self.snakeArray.append(head)
                self.lastKeyPress = direction
            elif direction == 'DOWN' and self.lastKeyPress != 'UP' and not self.collision((head[0], head[1] + 1)):
                self.snakeArray.pop(0)
                head = (head[0], head[1] + 1)
                self.snakeArray.append(head)
                self.lastKeyPress = direction
            if head[0] == self.apple_x and head[1] == self.apple_y:
                self.needApple = True
                self.score += 1
                self.snakeArray.insert(0, self.snakeArray[0])

    def timerEvent(self, event):
        '''Main game thread'''
        if event.timerId() == self.timer.timerId():
            self.direction(self.lastKeyPress)
            self.repaint()
        else:
            QtGui.QFrame.timerEvent(self, event)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        if not self.isPaused:
            if e.key() == QtCore.Qt.Key_P:
                self.pause()
            elif e.key() == QtCore.Qt.Key_Up:
                self.direction('UP')
            elif e.key() == QtCore.Qt.Key_Down:
                self.direction('DOWN')
            elif e.key() == QtCore.Qt.Key_Left:
                self.direction('LEFT')
            elif e.key() == QtCore.Qt.Key_Right:
                self.direction('RIGHT')
            self.repaint()
        else:
            if e.key() == QtCore.Qt.Key_Space:
                self.newGame()
            elif e.key() == QtCore.Qt.Key_P:
                self.unPause()

    def newGame(self):
        self.isPaused = False
        self.snakeArray = list(START_POS)
        self.lastKeyPress = 'RIGHT'
        self.timer.start(DEFAULT_SPEED, self)
        self.score = 0
        self.needApple = True

    def spawnApple(self, qp: QtGui.QPainter):
        if self.needApple:
            self.apple_x = random.randrange(0, 23)
            self.apple_y = random.randrange(2, 23)
            logging.info(f'spawn apple ({self.apple_x}, {self.apple_y})')
            self.needApple = False

        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.setBrush(QtGui.QColor(220, 20, 60, 255))
        if self.apple_x is not None and self.apple_y is not None:
            qp.drawRect(
                self.apple_x * self.snakeSize,
                self.apple_y * self.snakeSize,
                self.snakeSize,
                self.snakeSize
            )

    def collision(self, head: tuple):
        if head[0] < 0 or head[0] > 24:
            logging.info(f'collision {head}')
            self.pause(True)
            return True
        elif head[1] < 2 or head[1] > 22:
            logging.info(f'collision {head}')
            self.pause(True)
            return True
        elif head in self.snakeArray:
            logging.info(f'collision {head}')
            self.pause(True)
            return True

    def unPause(self):
        if self.isOver:
            return
        self.isPaused = False
        self.timer.start(DEFAULT_SPEED, self)

    def pause(self, isOver=False):
        self.isPaused = True
        self.isOver = isOver
        if isOver:
            self.highscore = max(self.highscore, self.score)
        self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Snake()
    sys.exit(app.exec_())
