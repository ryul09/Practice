from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("Kiwoom 클래스 입니다")

        #### evnet loop 모음
        self.login_event_loop = None
        #################################

        #### 변수 모음
        self.account_num = None
        #################################
        self.get_ocx_instance()
        self.event_slot()
        self.signal_login_commConnect()
        self.get_acount_info()

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  ##응용 프로그램 제어!

    def event_slot(self):
        self.OnEventConnect.connet(self.login_slot)

    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit()

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()  ## 종료 안되게끔!!!

    def get_acount_info(self):
        account_list = self.dynamicCall("GetLogininfo(String)", "ACCNO")

        self.account_num = account_list.split(";")[0]

        print("나의 보유 계좌번호 %s", self.account_num)
