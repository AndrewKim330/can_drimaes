import time

import can
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic


class ThreadWorker(QThread):
    timeout = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.bus1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
        self.bus2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')

    def run(self):
        while True:
            a = str(self.bus1.recv()).split()
            if a[3] == '18ffd741':
                # print(a)
                self.timeout.emit(str(self.bus1.recv()))


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    # #
    #     self.worker = ThreadWorker()
    #     self.worker.start()
    #     self.worker.timeout.connect(self.timeout)
    # #
    #     self.edit = QLineEdit(self)
    #     self.edit.move(10, 10)
    #     self.text_edit = QTextEdit()
        self.btn = QPushButton("ggg", self)
        self.btn.move(20, 20)
        layout = QVBoxLayout()
        # layout.addWidget(self.text_edit)
        self.setLayout(layout)
        #
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_text)
        # self.timer.start(10)

    @pyqtSlot(str)
    def update_text(self, aa):
        self.text_edit.append(f"New text at {str(aa)}")

    @pyqtSlot(int)
    def timeout(self, num):
        self.edit.setText(str(num))


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
    sys.exit(app.exec_())

