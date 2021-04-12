from kiwoom.kiwoom import *

import sys
from PyQt5.QtWidgets import *

class UI_class():
    def __init__(self):
        print("Ui_class 입니다")
        self.app = QApplication(sys.argv)

        ## sys.argv = ['파이썬파일경로','추가할옵션']

        self.kiwoom = Kiwoom()
        self.app.exec_()   ## 종료 안되게 끔
