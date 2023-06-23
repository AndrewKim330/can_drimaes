import threading

from PyQt5 import QtGui


class MainWindow(QtGui.QMainWindow):
    #all the code needed to build the GUI
    thread_mythread = threading.Thread(target = self.updateText, args = ())
    thread_mythread.start()

    def clearText(self):
        self.TextEdit.clear()

    def updateText(self):
        self.trigger.connect(self.clearText)

        self.my_thread = QThread()
        self.handler = MyWorker()
        self.handler.moveToThread(self.my_thread)
        self.handler.clear.connect(self.clearText)
        self.handler.update_text_signal.connect(self.update_line_edit)
        self.handler.finished.connect(self.my_thread.quit)
        # Start Thread
        self.my_thread.start()

        @pyqtSlot(str)
        def update_line_edit(self, text):
            self.TextEdit.append(text)

        QMetaObject.invokeMethod(self.handler, 'update_text',
                                 Qt.QueuedConnection,
                                 Q_ARG(list, string_list))



