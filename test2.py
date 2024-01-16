a = dict()
a[0] = [1,2,3]
a[1] = "b"
a[2] = "c"

print(a.values())
#
# print(a)
# print(a.keys())
# #
# # def test1():
# #     print(a)
# #
# # import test
# #
# #
# # def test(init=True):
# #     if init:
# #         print(init)
# #         init = False
# #
# # for i in range(5):
# #     test()
# #
# # test.test1()
# # master_set_c = dict()
# #
# # master_set_c[0x0CFE6C17] = {
# #     "mess_name": "IC_TC01", "data_set": [{"name": "IC_TachographVehicleSpeed", "bit_st_pos": 48, "bit_len": 16}]}
# #
# # print(master_set_c)
# #
#
#
# import sys
# from PyQt5 import QtGui, QtCore
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
#
# class Window(QMainWindow):
#     def __init__(self):
#         super(Window, self).__init__()
#         self.setGeometry(50, 50, 500, 300)
#         self.setWindowTitle("SciCalc")
#         self.setWindowIcon(QtGui.QIcon('atom.png'))
#         self.home()
#
#     def home(self):
#         self.btn = QPushButton("Physics", self)
#         self.btn.clicked.connect(QtCore.QCoreApplication.instance().quit)
#         self.btn.resize(100, 100)
#         self.show()
#
#     def resizeEvent(self, event):
#         self.btn.move(self.rect().center()-self.btn.rect().center())
#         QMainWindow.resizeEvent(self, event)
#
#
# def run():
#     app = QApplication(sys.argv)
#     GUI = Window()
#     sys.exit(app.exec_())
#
#
# run()