from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("Kiwoom 클래스 입니다")

        #### evnet loop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()

        #################################
        #### 스크린 번호
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"
        #### 변수 모음
        self.account_num = None
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        #################################

        #### 종목 분석용
        self.calcul_data = []


        #### 계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5


        self.get_ocx_instance()   #OCX, 응용 프로그램에서 open API를 실행할 수 있게 한거다, 제어 가능!
        self.event_slot()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info() # 예수금 가져오기
        self.detail_account_mystock() # 계좌평가 잔고 요청
        self.not_concludede_account() # 미체결 요청

        self.screen_calculator_fnc()  # 종목 분석용, 임시용으로 실행

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  ##응용 프로그램 제어!

    def event_slot(self):
        self.OnEventConnect.connet(self.login_slot)
        self.OnreceiveTrData.connect(self.trdata_slot)

    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit()

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()  ## 종료 안되게끔!!! One Thread loop에서 작업 충돌을 막기 위해 필요!!

    def get_acount_info(self):
        account_list = self.dynamicCall("GetLogininfo(String)", "ACCNO")

        self.account_num = account_list.split(";")[0]

        print("나의 보유 계좌번호 %s", self.account_num)

    def detail_account_info(self):
        print("예수금을 요청하는 부분")

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매채구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()  ##예수금 요청 하는 동안에 block 처리, event loop 동시성 처리 필요

        #### Screen No. --> 총 200개까지 가능 한 screen no.에 100개 항목까지 저장 가능
    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가 잔고내역 요청, 연속조회 %s" % sPrevNext)
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매채구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def not_concludede_account(self, sPrevNext="0"):
        print("미체결 요청" )
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def trdata_slot(self, sScNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        tr요청을 받는 구역이다! 슬롯이다!
        :param sScNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청 id, tr코드
        :param sRecordName: 사용 안함
        :param sPrevNext: 다음 페이지가 있는지
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode, sRQName, 0, "예수금")
            print("예수금 %s" % type(deposit))
            print("예수금 형변환 %s" % int(deposit))

            self.use_money = int(deposit) * self.use_money_percent  ##예수금은 계속 사용하는 변수이므로 추가 등록 후 관리
            self.use_money = self.use_money / 4

            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode, sRQName, 0, "출금가능금액")
            print("출금 가능 금액 %s" % ok_deposit)
            print("예수금 형변환 %s" % int(ok_deposit))

            self.detail_account_info_event_loop.exit()  ###event loop 종료, 다음 작업 할 수 있도록

        if sRQName == "계좌평가잔고내역요청" :
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("총매입금액 %s " % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)

            print("총수익률(%s) : %s" % ("%", total_profit_loss_rate_result)  # % 중복으로 인한 별도 표시 필요, 참고!

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                ## A : 장내주식, J : ELW 종목, Q : ETN 종목
                code=code.strip()[1:]  ##  ex. "A2309" [1:] = "2309", [:1] = "A"
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입급액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price)
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1

            print("계좌 보유 종목 Count %s" % cnt)
            print("계좌에 가지고 있는 종목 %s" % self.account_stock_dict)
            ## sPervNext : 주식 종목 수가 20개까지 표시되기 때문에 다음 페이지 존재 유무, 계좌 평가 잔고 내역 시그널!

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()

        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") # 접수, 확인, 체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문구분") # -매도, +매수, -매도정정
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip(). lstrip('+'). lstrip('-')  ## '+', '-' 기호때문에 오류 날 가능성 배제
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                nasd = self.not_account_stock_dict[order_no]
                ## self.not_account_stock_dict[code].update({"체결량":ok_quantity})
                ## -> 주소 찾는데 시간이 오래걸리므로 주소값(self.not_account_stock_dict[order_no] -> nasd.update({"체결량":ok_quantity}))을 하나로 묶어서 시간을 줄이고 편리성

                nasd.update({"종목코드": code})
                nasd.update({"종목명": code_nm})
                nasd.update({"주문번호": order_no})
                nasd.update({"주문상태": order_status})
                nasd.update({"주문수량": order_quantity})
                nasd.update({"주문가격": order_price})
                nasd.update({"주문구분": order_gubun})
                nasd.update({"미체결수량":not_quantity})
                nasd.update({"체결량":ok_quantity})

                print("미체결 종목 : %s" % self.not_account_stock_dict[order_no])
            self.detail_account_info_event_loop.exit()
        if sRQName == "주식일봉차트조회":

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString", sTrCode, sRQName) #GetRepeatCnt가 다음 창 혹은 주가창 확대 버튼~!
            print("데이터 일수 %s" % cnt)
            # data = self.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName)
            # [['', '현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가', ''], [''...]...]

            #한 번 조회하면 600일치까지 일봉 데이터를 받을 수 있다.
            for i in range(cnt): []:  # in range -> 범위값 [ 0, ..., 599]
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 000070
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data,copy())
            print(self.calcul_data)


                ## if절 밑에 하기와 같이 적으면 600개 data 한번에 가져올 수 있음
                ## Get CommDataEx
                ## []



            if sPrevNext == "2":
                self.day_kiwoon_db(code=code, sPrevNext=sPrevNext)

            else:
                print("총 일수 %s" %len(self.calcul_data))
                pass_success = False

                # 120일 이평선의 그릴만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    # 120일 이상 되면은

                    total_price = 0
                    for value in self.calcul_data[:120]:  # [오늘, 하루전, 하루하루전, ..., 119일전]
                        total_price +=int(value[1])
                    moving_average_price = total_price / 120

                    # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인
                    bottom_stock_price = False
                    check_price = None
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        print("오늘 주가 120일 이평선에 걸쳐있는 것 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])

                    # 과거 일봉들이 120일 이평선보다 밑에 있는지 확인,
                    # 그렇게 확인을 하다가 일봉이 120일 이평선보다 위에 있으면 계산 진행
                    prev_price = None #과거의 일봉 저가
                    if bottom_stock_price == True:
                        moving_average_price_prev = 0
                        price_top_moving = False

                        idx =1
                        while True:
                            if len(self.calcul_data[idx:])<120: # 120일 치가 있는지 계속 확인
                                print("120일치가 없음!")
                                break
                            total_price = 0
                            for value in self.calcul_data[idx: 120+idx]: # 과거 일자부터 120일간 data
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <=int(self.calcul_data[idx][6]) and idx <= 20:
                                print("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7])> moving_average_price_prev and idx > 20:
                                print("20일 이평선 위에 있는 일봉 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break
                            idx +=1 # 성립 안하면 idx 1로 올린다!

                        #해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                print("포착된 이평선의 가격이 오늘자(최근일자) 이평선 가격보다 낮은 것 확인됨")
                                print("포착된 부분의 일볼 저가가 오늘자 일봉의 고가보다 낮은지 확인됨")
                                pass_success = True

                if pass_success == True:
                    print("조건부 통과됨")

                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                    f = open("files/condition_stock.txt", "a", encoding="utf8")  # "a":data 누적 "w" :data 새로고침(앞을 지우고 새로 쓴다)
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                    print("조건부 통과 못함함")

                self.calcul_data.clear()
                self.calclator_event_loop.exit()
            



    def get_code_list_by_market(self, market code):
        '''종목 코드들 반환
        :param market_code:
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]  # 분리 및 마지막 값 삭제

        return code_list

    def calculator_fnc(self):
        '''종목 분석 실행용 함수
        :return:
        '''
        code_list = self.get_code_list_by_market("10")
        print("코스닥 개수 %s" % len(code_list))

        for idx, code in enumerate(code_list):# enumerate로 해야 data랑 index값 같이 준다!
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock ) # screen 번호를 한번이라도 요청하면 그룹이 만들어 짐! -> 그래서 끊어줌(개인의선택)

            pring("%s / %s : KOSDAQ Stock Code : %s in updating.." % (idx+1, len(code_list), code))
            self.day_kiwwom_db(code=code)


    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):

        QTest.qWait(3600)
        ## 위에가 없으면 무조건 error 가 발생한다!! 이유는 빠르게 tr 조회하면 연결 끊김(과도 조회), 1 thread의 한계 --> 시간텀을 주고 천천히 하도록 해야한다
        ## 엄청 고마움!!! 한달짜리 코드임!

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)  #Tr 서버로 전송 - Transaction

        self.calculator_event_loop.exec()


