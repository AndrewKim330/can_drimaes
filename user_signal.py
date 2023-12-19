from PyQt5 import uic
from PyQt5.QtWidgets import *


class UserSignal(QDialog):

    def __init__(self, base_dir, main_obj):
        super().__init__()
        self.signal_ui = uic.loadUi(base_dir + r"./src/can_basic_user_signal_ui.ui", self)
        self.setWindowTitle("User Defined Signal for E-51 IVI CAN Simulator")
        self.show()

        self.main_obj = main_obj

        self.tx_name_set = set()
        self.default_item = "--Select signal--"
        self.comboBox_user_signal.addItem(self.default_item)

        self.signal_list = []

        self.signal_list_flag = True

        self.prev_list_num = 0

        # self.label_message_id.setStyleSheet(f"color: {color}")
        # self.lineEdit_message_id.setEnabled(flag)
        # self.btn_arbitrary_send.setEnabled(flag)

    def user_signal_list(self, tx_name, tx_channel, tx_id):
        prev_num = len(self.tx_name_set)
        self.tx_name_set.add(tx_name)
        next_num = len(self.tx_name_set)
        if next_num - prev_num != 0:
            self.comboBox_user_signal.addItem(tx_name)
        if self.comboBox_user_signal.currentText() == tx_name:
            self.user_signal_sender(tx_channel=tx_channel, tx_id=tx_id)

    def user_signal_sender(self, tx_channel, tx_id):
        self.main_obj.user_signal_worker._isRunning = True
        self.main_obj.user_signal_worker.start()
        self.main_obj.user_signal_worker.bus_selector = tx_channel
        self.main_obj.user_signal_worker.send_id = tx_id

        print(self.lineEdit_data_0.text)

        # if self.comboBox_user_filter.currentText() != self.default_item:
        #     if len(self.filtered_list) == 0:
        #         self.filtered_list.append(self.comboBox_user_filter.currentText())
        #     else:
        #         temp_list = self.filtered_list[:]
        #         append_flag = True
        #         for elem in temp_list:
        #             if self.comboBox_user_filter.currentText() == elem:
        #                 append_flag = False
        #         if append_flag:
        #             self.filtered_list.append(self.comboBox_user_filter.currentText())
        # self.user_filter_chkbox(self.filtered_list)
        # for i in range(len(self.filtered_list)):
        #     if tx_name == self.filtered_list[i]:
        #         return self.user_filter_chkbox(self.filtered_list, chkbox_num=i)
        # return False

    # def user_filter_chkbox(self, li, chkbox_num=1000):
    #     present_list_num = len(li)
    #     if self.prev_list_num != present_list_num:
    #         self.filter_list_init = True
    #         mywindow.console_text_clear("tx_console_clear")
    #     self.prev_list_num = len(li)
    #     if len(li) == 0:
    #         self.chkbox_1st.setVisible(False)
    #         self.chkbox_2nd.setVisible(False)
    #         self.chkbox_3rd.setVisible(False)
    #         self.chkbox_4th.setVisible(False)
    #         self.chkbox_5th.setVisible(False)
    #     elif self.comboBox_user_filter.currentText() == self.default_item:
    #         self.chkbox_1st.setVisible(False)
    #         self.chkbox_2nd.setVisible(False)
    #         self.chkbox_3rd.setVisible(False)
    #         self.chkbox_4th.setVisible(False)
    #         self.chkbox_5th.setVisible(False)
    #         self.filtered_list = []
    #     else:
    #         if len(li) == 1 or chkbox_num == 0:
    #             if self.filter_list_init:
    #                 self.chkbox_1st.setVisible(True)
    #                 self.chkbox_1st.setChecked(True)
    #                 self.filter_list_init = False
    #                 self.chkbox_1st.setText(li[0])
    #             else:
    #                 if self.chkbox_1st.isChecked():
    #                     return True
    #                 else:
    #                     return False
    #         if len(li) == 2 or chkbox_num == 1:
    #             if self.filter_list_init:
    #                 self.chkbox_2nd.setVisible(True)
    #                 self.chkbox_2nd.setChecked(True)
    #                 self.filter_list_init = False
    #                 self.chkbox_2nd.setText(li[1])
    #             else:
    #                 if self.chkbox_2nd.isChecked():
    #                     return True
    #                 else:
    #                     return False
    #         elif len(li) == 3 or chkbox_num == 2:
    #             if self.filter_list_init:
    #                 self.chkbox_3rd.setVisible(True)
    #                 self.chkbox_3rd.setChecked(True)
    #                 self.filter_list_init = False
    #                 self.chkbox_3rd.setText(li[2])
    #             else:
    #                 if self.chkbox_3rd.isChecked():
    #                     return True
    #                 else:
    #                     return False
    #         elif len(li) == 4 or chkbox_num == 3:
    #             if self.filter_list_init:
    #                 self.chkbox_4th.setVisible(True)
    #                 self.chkbox_4th.setChecked(True)
    #                 self.filter_list_init = False
    #                 self.chkbox_4th.setText(li[3])
    #             else:
    #                 if self.chkbox_4th.isChecked():
    #                     return True
    #                 else:
    #                     return False
    #         elif len(li) == 5 or chkbox_num == 4:
    #             if self.filter_list_init:
    #                 self.chkbox_5th.setVisible(True)
    #                 self.chkbox_5th.setChecked(True)
    #                 self.filter_list_init = False
    #                 self.chkbox_5th.setText(li[4])
    #             else:
    #                 if self.chkbox_5th.isChecked():
    #                     return True
    #                 else:
    #                     return False

    def ui_close(self):
        self.close()
