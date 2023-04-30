import time
import pprint
import scrapping3 as scr

import can
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

bus1 = can.interface.Bus(bustype='vector', channel="0, 1", bitrate='500000')
# bus1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
# bus2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')


class ThreadWorker(QThread):
    sig = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        flowControl = False
        temp = []
        while True:
            a = str(bus1.recv()).split()
            # self.sig.emit(a)
            if a[3] == '18daf141':
                print(a)
                if flowControl:
                    temp.append(a)
                if a[8] == '10':
                    temp.append(a)
                    message = can.Message(arbitration_id=0x18da41f1, data=[0x30, 0x00, 0x00, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA])
                    bus1.send(message)
                    print("flow control")
                    flowControl = True
            if len(temp) == 10:
                self.sig.emit(temp)
                flowControl = False
                temp = []


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 700, 500)

        self.text = QPlainTextEdit(self)
        self.text.move(80, 80)
        self.text.resize(500, 100)
        self.text.setReadOnly(True)
        # self.worker.timeout.connect(self.timeout)

        self.btn1 = QPushButton("0x19 01", self)
        self.btn2 = QPushButton("0x19 02", self)
        self.btn3 = QPushButton("textbox clear", self)
        self.btn1.move(20, 20)
        self.btn2.move(50, 50)
        self.btn3.move(200, 50)
        self.btn1.clicked.connect(self.btn_clicked1)
        self.btn2.clicked.connect(self.btn_clicked2)
        self.btn3.clicked.connect(self.text_clear)

        self.worker = ThreadWorker(self)
        self.worker.sig.connect(self.sig)
        self.worker.start()

    def btn_clicked1(self):
        print("19 01 service")
        message = can.Message(arbitration_id=0x18da41f1, data=[0x03, 0x19, 0x01, 0x09, 0xFF, 0xFF, 0xFF, 0xFF])
        bus1.send(message)

    def btn_clicked2(self):
        print("19 02 service")
        message = can.Message(arbitration_id=0x18da41f1, data=[0x03, 0x19, 0x02, 0x09, 0xFF, 0xFF, 0xFF, 0xFF])
        bus1.send(message)

    def text_clear(self):
        self.text.clear()

    @pyqtSlot(list)
    def sig(self, li):
        print('emit success')
        scr.scr(li)
        for i in li:
            self.text.appendPlainText(str(i))


#
#
# class MyApp(QMainWindow, windowForm):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)
#
#
# class threadWorker1(QThread):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent = parent
#
#     def run(self):
#         for num in range(10):
#             text = f'thread1 count + {str(num)}'
#             self.parent.textBrowser1.append(text)
#
#         self.quit()
#         self.wait(5000)
#
# class threadWorker2(QThread):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent() = parent
#
#     def run(self):
#
#
#
# class MyWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.worker = threadWorker()
#
#     def btn_clicked(self):
#         self.close()
#
#
# def good():
#
#     # Use a breakpoint in the code line below to debug your script.
#     bus1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
#     bus2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')
#     print(bus2)
#
#     ign_message = can.Message(arbitration_id=0x18ff8621, data=[0x97, 0x7a, 0xdf, 0xff, 0xfa, 0xff, 0xff, 0xff])
#
#     i = 0
#     print(bus1.recv())
#     while True:
#         print(bus1.recv())
#         print('aaa')
#         app = QApplication(sys.argv)
#         mywindow = MyWindow()
#         mywindow.show()
#
#         app.exec_()
#
#         a = str(bus1.recv()).split()
#         bus1.send(ign_message)
#         if a[3] == '18ffd741':
#             message = can.Message(arbitration_id=0x18ffa57f, data=[int(a[9], 16), 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
#             bus1.send(message)
#             print(i, a)
#         i += 1
#


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()

