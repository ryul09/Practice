import os
import time
import datetime
import atexit
import threading

from PyQt5 import QtWidgets, QtCore, QAxContainer

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# 실시간 데이터 저장용 클래스
class RealData:
    DATA_FULL_SIZE =1000 # 데이터가 계속 추가되다 크기가 DATA_FULL_SIZE되면 자동 저장을 실시한다.
    
    def __init__(self, code: str, name: str, market: str):
        # 종목코드, 종목명, 시장타입 설정
        self.code   = code
        self.name   = name
        if market == '': # ETN은 공백이 넘어옴
            self.market = 'ETN'
        else:
            self.market = market
        
        self.tick_count = 0
        
        # '주식체결' 데이터 저장용
        self.체결시간         = []
        self.현재가           = []
        self.전일대비         = []
        self.등락율           = []
        self.최우선매도호가   = []
        self.최우선매수호가   = []
        self.거래량           = []
        self.누적거래량       = []
        self.누적거래대금     = []
        self.시가             = []
        self.고가             = []
        self.저가             = []
        self.전일대비기호     = []
        self.전일거래량대비   = []
        self.거래대금증감     = []
        self.전일거래량대비율 = []
        self.거래회전율       = []
        self.거래비용         = []
        self.체결강도         = []
        self.시가총액         = []
        self.장구분           = []
        self.KO접근도         = []
        self.상한가발생시간   = []
        self.하한가발생시간   = []

    def append(self, 체결시간: str, 현재가: str, 전일대비: str, 등락율: str, 최우선매도호가: str, 최우선매수호가: str, 거래량: str, 누적거래량: str, 누적거래대금: str, 시가: str, 고가: str, 저가: str, 전일대비기호: str, 전일거래량대비: str, 거래대금증감: str, 전일거래량대비율: str, 거래회전율: str, 거래비용: str, 체결강도: str, 시가총액: str, 장구분: str, KO접근도: str, 상한가발생시간: str, 하한가발생시간: str) -> None:
        '''
        실시간 데이터를 추가하는 함수
        '''
        self.체결시간.append(체결시간)
        self.현재가.append(현재가)
        self.전일대비.append(전일대비)
        self.등락율.append(등락율)
        self.최우선매도호가.append(최우선매도호가)
        self.최우선매수호가.append(최우선매수호가)
        self.거래량.append(거래량)
        self.누적거래량.append(누적거래량)
        self.누적거래대금.append(누적거래대금)
        self.시가.append(시가)
        self.고가.append(고가)
        self.저가.append(저가)
        self.전일대비기호.append(전일대비기호)
        self.전일거래량대비.append(전일거래량대비)
        self.거래대금증감.append(거래대금증감)
        self.전일거래량대비율.append(전일거래량대비율)
        self.거래회전율.append(거래회전율)
        self.거래비용.append(거래비용)
        self.체결강도.append(체결강도)
        self.시가총액.append(시가총액)
        self.장구분.append(장구분)
        self.KO접근도.append(KO접근도)
        self.상한가발생시간.append(상한가발생시간)
        self.하한가발생시간.append(하한가발생시간)

        RowCount = len(self.체결시간)
        if RowCount >= RealData.DATA_FULL_SIZE:
            self.save_data(True)
        
    def __len__(self) -> None:
        '''
        입력된 데이터 수를 반환
        #'''
        return len(self.체결시간)
        
    def save_data(self, bRemovePrev: bool=True):
        '''
        파일 저장은 IO작업이므로 스레드을 이용하여 저장하여 실행 효율을 높인다.
        
        ※ 참고: 단순 코딩으로 concurrent.futures를 이용하지 않았음
        '''
        t = threading.Thread(target = self._save_data, args = (bRemovePrev, ))
        t.start()

    def _save_data(self, bRemovePrev: bool=True) -> None:
        '''
        현재 저장된 데이터를 저장한다.
        
        bRemoveRrev를 True로 설정하면 현재까지의 데이터를 저장하고, 이전 데이터는 비운다.
        '''
        RowCount = len(self.체결시간)
        
        체결시간         = self.체결시간
        현재가           = self.현재가
        전일대비         = self.전일대비
        등락율           = self.등락율
        최우선매도호가   = self.최우선매도호가
        최우선매수호가   = self.최우선매수호가
        거래량           = self.거래량
        누적거래량       = self.누적거래량
        누적거래대금     = self.누적거래대금
        시가             = self.시가
        고가             = self.고가
        저가             = self.저가
        전일대비기호     = self.전일대비기호
        전일거래량대비   = self.전일거래량대비
        거래대금증감     = self.거래대금증감
        전일거래량대비율 = self.전일거래량대비율
        거래회전율       = self.거래회전율
        거래비용         = self.거래비용
        체결강도         = self.체결강도
        시가총액         = self.시가총액
        장구분           = self.장구분
        KO접근도         = self.KO접근도
        상한가발생시간   = self.상한가발생시간
        하한가발생시간   = self.하한가발생시간

        if bRemovePrev:
            self.체결시간         = []
            self.현재가           = []
            self.전일대비         = []
            self.등락율           = []
            self.최우선매도호가   = []
            self.최우선매수호가   = []
            self.거래량           = []
            self.누적거래량       = []
            self.누적거래대금     = []
            self.시가             = []
            self.고가             = []
            self.저가             = []
            self.전일대비기호     = []
            self.전일거래량대비   = []
            self.거래대금증감     = []
            self.전일거래량대비율 = []
            self.거래회전율       = []
            self.거래비용         = []
            self.체결강도         = []
            self.시가총액         = []
            self.장구분           = []
            self.KO접근도         = []
            self.상한가발생시간   = []
            self.하한가발생시간   = []
            
        #FileName = f"{self.market}_{self.code}_{self.name}.csv"
        FileName = f"{self.code}.csv"
        DirName = 'C:\\Datas\\Data_Kiwoom'
        DirFileName = f"{DirName}\\{FileName}"
            
        if os.path.isfile(DirFileName):
            DataString = ""
        else:
            DataString = "체결시간,현재가,전일대비,등락율,최우선매도호가,최우선매수호가,거래량,누적거래량,누적거래대금,시가,고가,저가,전일대비기호,전일거래량대비,거래대금증감,전일거래량대비율,거래회전율,거래비용,체결강도,시가총액,장구분,KO접근도,상한가발생시간,하한가발생시간\n"
            
        for i in range(RowCount):
            DataString = f"{DataString}{체결시간[i]},{현재가[i]},{전일대비[i]},{등락율[i]},{최우선매도호가[i]},{최우선매수호가[i]},{거래량[i]},{누적거래량[i]},{누적거래대금[i]},{시가[i]},{고가[i]},{저가[i]},{전일대비기호[i]},{전일거래량대비[i]},{거래대금증감[i]},{전일거래량대비율[i]},{거래회전율[i]},{거래비용[i]},{체결강도[i]},{시가총액[i]},{장구분[i]},{KO접근도[i]},{상한가발생시간[i]},{하한가발생시간[i]}\n"
    
        if not os.path.isdir(DirName):
            os.mkdir(DirName)
            
        # 상위폴더가 없을 때 바로 폴더를 만들면 오류가 발생한다.
        # 상위폴더를 확인해 가면서(만들어가면서) 최종 폴더를 만든다.
        dirlist = DirName.split('\\')
        
        for i in range(2, len(dirlist) + 1):
            currpath = '\\'.join(dirlist[:i])
            if not os.path.isdir(currpath):
                os.mkdir(currpath)
            
        try:
            with open(DirFileName, "a") as f:
                f.write(DataString)
                
            print(f"File writting complete : {FileName} [{self.market}:{self.name}]")
        except Exception as e:
            print(f"File writting error : {e}")


# 사용자 이벤트용 클래스
class SignalHandler(QtCore.QObject):
    '''
    QtWidgets 상속 클래스에서는 시그널을 생성하여 사용못한다.
    대신 시그널 생성 가능 객체를 만들어서 인스턴스 변수에 바인딩하여 사용한다.
    '''
    msg_draw_graph    = QtCore.pyqtSignal(str) # 그래프 그리기 이벤트


class MyWindow(QtWidgets.QMainWindow):
    '''
    메인 윈도우
    UI는 내부에서 직접 작성하여 대응함
    '''
    
    @classmethod
    def setHiDpi(cls):
        '''
        해상도에 따라 레이아웃이 깨지는 문제에 대응하는 코드
        QApplication 객체 생성 이전에 실행해야 한다.
        '''
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) # Enable highdpi scaling
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) # Use highdpi icons
        
    def __init__(self):
        super().__init__()
        
        self.tick_count = 0 # 참고용, 실행시킨 이후 수신받은 틱 수
        
        self.SelectedIndex = -1 # 종목코드 콤보 선택 위치 확인용
        
        self.codes = [] # 확인할 종목코드
        self.names = [] # 종목코드에 대한 이름 저장용
        self.datas = {} # 실시간 수신 데이터 저장용, key는 종목코드, 값은 RealData형식
        
        self.today = datetime.datetime.now().strftime("%Y%m%d") # 실시간 데이터는 날짜 정보가 없음, 날짜 정보 추가용
        
        # 키움 객체 및 사용자 이벤트용 객체
        self.objKiwoom = QAxContainer.QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.objSignal = SignalHandler()
        
        self.initUI() # UI를 구성한다.
        self.initSignalSlot() # 시그널/슬롯 설정
        
        atexit.register(self.__del__) # 종료 버튼으로 종료할 때 실행시킨다. __del__ 실행을 보장하기 위해서 사용
        
        # 로그인을 실행한다.
        self.objKiwoom.dynamicCall("CommConnect()")
        
    def __del__(self):
        '''
        종료시 실행할 작업
        '''
        self.objKiwoom.dynamicCall("SetRealRemove(str, str)", "ALL", "ALL")
        
    ###############################################
    #
    # 사용자 함수
    #
    ###############################################
    
    def initUI(self):
        '''
        UI 생성 및 초기화
        '''
        # 메인 윈도우 설정 ---------------------------------------------
        self.setWindowTitle("Kiwoom Data Collector Sample")
        self.resize(425, 500)
        self.centralwidget = QtWidgets.QWidget(self)
        
        # 상태표시줄 설정 ---------------------------------------------
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready...")
        
        # 종목 에디트 위젯 설정 ---------------------------------------------
        self.stockCodeEdit = QtWidgets.QLineEdit(self)
        
        # 콤보 위젯 설정 ---------------------------------------------
        self.combo = QtWidgets.QComboBox(self)
        
        # 저장 버튼 설정
        self.saveCurrButton = QtWidgets.QPushButton("Save Current", self.centralwidget)
        self.saveAllButton = QtWidgets.QPushButton("Save All", self.centralwidget)
        
        # 로그인 전까지 버튼을 사용할 수 없게 한다.
        self.saveCurrButton.setEnabled(False)
        self.saveAllButton.setEnabled(False)
        
        # 종료 버튼 설정
        self.exitButton = QtWidgets.QPushButton("Exit", self.centralwidget)
        
        # 그래프 그리기 준비 ---------------------------------------------
        self.figure = Figure()
        self.ax     = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        
        # matplotlib에서 한글 처리를 위한 루틴
        font_name = matplotlib.font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        matplotlib.rc("font", family = font_name)
        
        # matplotlib에서 (-)표기를 위한 루틴
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        # 레이아웃 배치 ---------------------------------------------
        self.vertLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        
        self.codeLayout = QtWidgets.QHBoxLayout()
        self.codeLayout.addWidget(self.stockCodeEdit)
        self.codeLayout.addWidget(self.combo)
        self.codeLayout.setStretch(0,0)
        self.codeLayout.setStretch(1,1)
        
        self.vertLayout.addLayout(self.codeLayout)
        
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.saveCurrButton)
        self.buttonLayout.addWidget(self.saveAllButton)
        self.buttonLayout.addWidget(self.exitButton)
        self.vertLayout.addLayout(self.buttonLayout)
        
        self.vertLayout.addWidget(self.canvas)
        
        # 레이아웃 설정
        self.vertLayout.setStretch(0, 0)
        self.vertLayout.setStretch(1, 0)
        self.vertLayout.setStretch(2, 1)
        self.setCentralWidget(self.centralwidget)
        
        self.canvas.draw()
        
    def initSignalSlot(self):
        '''
        시그널/슬롯 연결 설정
        '''
        # 수신 이벤트 연결
        self.objKiwoom.OnEventConnect.connect(self.myOnEventConnect)
        self.objKiwoom.OnReceiveRealData.connect(self.myOnReceiveRealData)
        
        # 위젯 이벤트 연결
        self.stockCodeEdit.returnPressed.connect(self.stockCodeEditReturnPressed)
        self.combo.currentIndexChanged.connect(self.combo_currentIndexChanged)
        self.saveCurrButton.clicked.connect(self.saveCurrButton_clicked)
        self.saveAllButton.clicked.connect(self.saveAllButton_clicked)
        self.exitButton.clicked.connect(self.exitButton_clicked)
        
        # 사용자 이벤트 연결
        self.objSignal.msg_draw_graph.connect(self.myOnDrawGraph)
        
    def regRealItem(self):
        '''
        self.codes에 저장되어 있는 종목코드를 실시간 등록한다.
        '''
        # 키움은 스크린번호당 100개까지 등록 가능
        # --> 한 스크린 번호당 100개씩 등록한다.
        nLength   = len(self.codes) # 전체 종목수
        nReqScrNo = int(nLength / 100) + 1 # 100개 단위 필요 스크린 수, +1 --> 100개 단위를 모으고 남은 자투리 항목용
        
        for i in range(nReqScrNo):
            sScreenNo = f"7{i:03}" # 스크린 이름, 이름은 서로 구분만 되면 됨
            start = i*100
            end = start + 100
            sCodes = ";".join(self.codes[start:end]) # 100개의 종목 문자열을 하나의 문자열로 만든다.
            
            sFidList = '20;10;11;12;27;28;15;13;14;16;17;18;25;26;29;30;31;32;228;311;290;691;567;568'                
            
            self.objKiwoom.dynamicCall("SetRealReg(str, str, str, str)", sScreenNo, sCodes, sFidList, "0") # 20:체결시간, 10:현재가, 11:전일대비, 15:거래량
            
        self.statusBar.showMessage("실시간 등록 완료")
        
    ###############################################
    #
    # 수신 Evnet 함수
    #
    ###############################################
    
    def myOnEventConnect(self, nErrCode):
        '''
        로그인 이벤트
        
        로그인 성공시 실시간 등록을 실행한다(실시간 등록 함수는 로그인 되어야 사용가능).
        로그인 실패시 종료한다.
        '''
        if nErrCode == 0:
            self.statusBar.showMessage("로그인 OK")
            
            self.saveCurrButton.setEnabled(True)
            self.saveAllButton.setEnabled(True)
            
            # 코드 리스트를 초기화 한다.
            self.setCodeList("ALL")
            
            # 각 종목코드에 대한 저장 클래스의 객체를 만든다.
            for code in self.codes:
                name   = self.objKiwoom.dynamicCall("GetMasterCodeName(str)", code)
                market = self.objKiwoom.dynamicCall("KOA_Functions(str, str)", "GetMasterStockInfo", code).split(";")[0].split("|")[1]
                
                self.datas[code] = RealData(code, name, market)
                self.names.append(name)
                
                self.combo.addItem(f"{code} {name}") # 종목 선택 콤보 리스트에 항목 추가

            # 종목코드나 종목명 입력시 자동 완성 기능을 적용한다.
            # 단, PyQt에서는 초성 검색까진 지원하지 않는다.
            # 약간 불편하지만 없는 것 보단 편리
            completer = QtWidgets.QCompleter(self.codes + self.names)
            self.stockCodeEdit.setCompleter(completer)
                
            self.regRealItem()
            
        else: # 로그인 실패시 --> 종료시켜 버림
            self.statusBar.showMessage(f"Error[{nErrCode}]")
            
            QtCore.QCoreApplication.instance().quit()
        
    def setCodeList(self, option: str) -> None:
        '''
        코드 리스트를 설정한다.
        
            option
                "ALL"    : 모든 KOSPI와 KOSDAQ종목을 등록한다.
                "KOSPI"  : 모든 KOSPI종목을 등록한다.
                "KOSDAQ" : 모든 KOSDAQ종목을 등록한다.
                "code"   : 코드 한개를 등록한다.
                "code0;code1;code2;...;coden" : 복수개의 코드를 등록한다. 코드간 ";"로 구분한다.
        '''
        if option == "ALL":
            codeText = self.objKiwoom.dynamicCall("GetCodeListByMarket(str)", "0") + self.objKiwoom.dynamicCall("GetCodeListByMarket(str)", "10")
            self.codes = codeText[:-1].split(";")
        elif option == "KOSPI":
            codeText = self.objKiwoom.dynamicCall("GetCodeListByMarket(str)", "0")
            self.codes = codeText[:-1].split(";")
        elif option == "KOSDAQ":
            codeText = self.objKiwoom.dynamicCall("GetCodeListByMarket(str)", "10")
            self.codes = codeText[:-1].split(";")
        else:
            try:
                self.codes = option.split(";")
            except:
                self.codes = [option]
        
    def myOnReceiveRealData(self, sCode, sRealType, sRealData):
        '''
        실시간 수신 이벤트
        
        '주식 체결'만 데이터를 저장한다. '주식 시세'는 고려하지 않음
        '''
        if sRealType == "주식체결":
            try:
                체결시간         = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '20')  # HHMMSS
                현재가           = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '10')
                전일대비         = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '11')
                등락율           = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '12')
                최우선매도호가   = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '27')
                최우선매수호가   = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '28')
                거래량           = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '15')
                누적거래량       = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '13')
                누적거래대금     = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '14')
                시가             = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '16')
                고가             = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '17')
                저가             = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '18')
                전일대비기호     = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '25')
                전일거래량대비   = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '26')  # 계약,주
                거래대금증감     = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '29')
                전일거래량대비율 = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '30')  # 비율
                거래회전율       = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '31')
                거래비용         = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '32')
                체결강도         = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '228')
                시가총액         = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '311') # 억
                장구분           = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '290') # 1:장전시간외, 2:장중 3:장후시간외
                KO접근도         = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '691')
                상한가발생시간   = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '567')
                하한가발생시간   = self.objKiwoom.dynamicCall("GetCommRealData(str, int)", sCode, '568')
                    
                체결시간 = f"{self.today}{체결시간}"
                
                self.tick_count += 1
                self.datas[sCode].tick_count += 1
                
                self.statusBar.showMessage(f"All Ticks: {self.tick_count} / {self.datas[sCode].name}: {self.datas[sCode].tick_count}")
                
                # 데이터를 추가한다.
                self.datas[sCode].append(체결시간, 현재가, 전일대비, 등락율,
                                         최우선매도호가, 최우선매수호가, 거래량, 누적거래량, 누적거래대금,
                                         시가, 고가, 저가, 전일대비기호, 전일거래량대비, 거래대금증감, 전일거래량대비율, 
                                         거래회전율, 거래비용, 체결강도,
                                         시가총액, 장구분, KO접근도,
                                         상한가발생시간, 하한가발생시간)
                
                self.objSignal.msg_draw_graph.emit(sCode) # code에 해당하는 그래프 그리기를 요청
            except Exception as e:
                '''
                일반 TR을 전송해도 전송한 코드에 대해 실시간 등록을 하지 않아도 Real이벤트가 발생한다.
                따라서 해당 코드에 대해 처리되지 않으면 오류가 발생한다.
                이를 걸러 주기 위해 예외로 대응함
                #'''
                print(f"{e}")
        
    ###############################################
    #
    # Slot 함수
    #
    ###############################################
    
    @QtCore.pyqtSlot(str)
    def myOnDrawGraph(self, sCode):
        '''
        그래프 그리기 요청에 대한 처리
        '''
        code = self.codes[self.SelectedIndex]
        if code == sCode: # 콤보 리스트에서 선택된 종목코드와 실시간 수신된 종목코드가 같으면 그래프를 그린다.
            self.ax.clear() # 그래프를 지운다.
            
            # 실시간 데이터 plot
            # x값은 생략, y값만 plot한다.
            GraphData = [abs(int(x)) for x in self.datas[sCode].현재가]
            
            self.ax.plot(GraphData, c = 'r', lw = 0.5, label = self.datas[sCode].name)
            self.ax.grid() # 눈금 표시
            self.ax.legend(fontsize = 8, loc = "upper left") # 범례 표시
        
            self.canvas.draw() # 화면 갱신
        
    def stockCodeEditReturnPressed(self):
        '''
        종목코드나 종목명을 입력 후 엔터키를 눌렀을 때 실행
        '''
        inputText = self.stockCodeEdit.text()
        
        try: # 종목코드가 입력된 경우인지 판별
            index = self.codes.index(inputText)
        except:
            index = -1
            
        if index == -1:
            try: # 종목명이 입력된 경우인지 판별
                index = self.names.index(inputText)
            except:
                index = -1
            
        if index != -1:
            self.combo.setCurrentIndex(index)
            self.stockCodeEdit.setText(self.names[index])
        
    @QtCore.pyqtSlot()
    def saveCurrButton_clicked(self):
        '''
        저장 버튼 클릭시 현재 선택된 종목을 저장
        '''
        if self.SelectedIndex != -1:
            code = self.codes[self.SelectedIndex]
            self.datas[code].save_data()
        
    @QtCore.pyqtSlot()
    def saveAllButton_clicked(self):
        '''
        모든 종목 저장
        '''
        for realData in self.datas.values():
            realData._save_data() # 스레드 제한 문제 예상으로 한 파일씩...
        
    @QtCore.pyqtSlot()
    def exitButton_clicked(self):
        '''
        Exit 버튼을 클릭시 실행
        
        프로그램을 종료한다.
        '''
        QtCore.QCoreApplication.instance().quit()
        
    def combo_currentIndexChanged(self, index: int) -> None:
        self.SelectedIndex = index
        
        code = self.codes[index]
        name = self.names[index]
        
        self.stockCodeEdit.setText(name)
        
        self.objSignal.msg_draw_graph.emit(code) # code에 해당하는 그래프 그리기를 요청


if __name__ == "__main__":
    import sys
    
    MyWindow.setHiDpi()

    app = QtWidgets.QApplication(sys.argv)
    
    myWindow = MyWindow()
    myWindow.show()
    
    app.exec_()
