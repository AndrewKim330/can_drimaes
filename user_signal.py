from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class UserSignal(QDialog):

    def __init__(self, base_dir, main_obj):
        super().__init__()
        self.signal_ui = uic.loadUi(base_dir + r"./src/can_user_signal_ui.ui", self)
        self.setWindowIcon(QIcon(base_dir + r"./src/drimaes_icon.ico"))
        self.setWindowTitle("User Defined Signal for E-51 IVI CAN Simulator")
        self.show()

        self.height_init = 165
        self.height = None

        self.main_obj = main_obj

        self.tx_name_set = set()
        self.default_message_item = "--Select signal--"
        self.default_bus_item = "--Select bus--"

        self.btn_arbitrary_add_signal.released.connect(self.add_message_handler)
        self.btn_arbitrary_remove_signal.released.connect(self.remove_message_handler)
        self.btn_arbitrary_reset.released.connect(self.entire_message_reset)

        self.btn_arbitrary_clear_1.released.connect(self.data_clear)
        self.btn_arbitrary_clear_2.released.connect(self.data_clear)
        self.btn_arbitrary_clear_3.released.connect(self.data_clear)
        self.btn_arbitrary_clear_4.released.connect(self.data_clear)
        self.btn_arbitrary_clear_5.released.connect(self.data_clear)

        self.message_comp_list = [
            {"label": [self.label_message_id_1], "chkbox": [self.chkbox_period_1],
             "combo_box": [self.comboBox_user_signal_mess_name_1, self.comboBox_user_signal_bus_1],
             "line_edit": [self.lineEdit_data_1_0, self.lineEdit_data_1_1, self.lineEdit_data_1_2,
                           self.lineEdit_data_1_3, self.lineEdit_data_1_4, self.lineEdit_data_1_5,
                           self.lineEdit_data_1_6, self.lineEdit_data_1_7, self.lineEdit_period_1],
             "btn": [self.btn_arbitrary_send_1, self.btn_arbitrary_clear_1]},
            {"label": [self.label_message_id_2], "chkbox": [self.chkbox_period_2],
             "combo_box": [self.comboBox_user_signal_mess_name_2, self.comboBox_user_signal_bus_2],
             "line_edit": [self.lineEdit_data_2_0, self.lineEdit_data_2_1, self.lineEdit_data_2_2,
                           self.lineEdit_data_2_3, self.lineEdit_data_2_4, self.lineEdit_data_2_5,
                           self.lineEdit_data_2_6, self.lineEdit_data_2_7, self.lineEdit_period_2],
             "btn": [self.btn_arbitrary_send_2, self.btn_arbitrary_clear_2]},
            {"label": [self.label_message_id_3], "chkbox": [self.chkbox_period_3],
             "combo_box": [self.comboBox_user_signal_mess_name_3, self.comboBox_user_signal_bus_3],
             "line_edit": [self.lineEdit_data_3_0, self.lineEdit_data_3_1, self.lineEdit_data_3_2,
                           self.lineEdit_data_3_3, self.lineEdit_data_3_4, self.lineEdit_data_3_5,
                           self.lineEdit_data_3_6, self.lineEdit_data_3_7, self.lineEdit_period_3],
             "btn": [self.btn_arbitrary_send_3, self.btn_arbitrary_clear_3]},
            {"label": [self.label_message_id_4], "chkbox": [self.chkbox_period_4],
             "combo_box": [self.comboBox_user_signal_mess_name_4, self.comboBox_user_signal_bus_4],
             "line_edit": [self.lineEdit_data_4_0, self.lineEdit_data_4_1, self.lineEdit_data_4_2,
                           self.lineEdit_data_4_3, self.lineEdit_data_4_4, self.lineEdit_data_4_5,
                           self.lineEdit_data_4_6, self.lineEdit_data_4_7, self.lineEdit_period_4],
             "btn": [self.btn_arbitrary_send_4, self.btn_arbitrary_clear_4]},
            {"label": [self.label_message_id_5], "chkbox": [self.chkbox_period_5],
             "combo_box": [self.comboBox_user_signal_mess_name_5, self.comboBox_user_signal_bus_5],
             "line_edit": [self.lineEdit_data_5_0, self.lineEdit_data_5_1, self.lineEdit_data_5_2,
                           self.lineEdit_data_5_3, self.lineEdit_data_5_4, self.lineEdit_data_5_5,
                           self.lineEdit_data_5_6, self.lineEdit_data_5_7, self.lineEdit_period_5],
             "btn": [self.btn_arbitrary_send_5, self.btn_arbitrary_clear_5]},
            {"label": [self.label_message_id_6], "chkbox": [self.chkbox_period_6],
             "combo_box": [self.comboBox_user_signal_mess_name_6, self.comboBox_user_signal_bus_6],
             "line_edit": [self.lineEdit_data_6_0, self.lineEdit_data_6_1, self.lineEdit_data_6_2,
                           self.lineEdit_data_6_3, self.lineEdit_data_6_4, self.lineEdit_data_6_5,
                           self.lineEdit_data_6_6, self.lineEdit_data_6_7, self.lineEdit_period_6],
             "btn": [self.btn_arbitrary_send_6, self.btn_arbitrary_clear_6]},
            {"label": [self.label_message_id_7], "chkbox": [self.chkbox_period_7],
             "combo_box": [self.comboBox_user_signal_mess_name_7, self.comboBox_user_signal_bus_7],
             "line_edit": [self.lineEdit_data_7_0, self.lineEdit_data_7_1, self.lineEdit_data_7_2,
                           self.lineEdit_data_7_3, self.lineEdit_data_7_4, self.lineEdit_data_7_5,
                           self.lineEdit_data_7_6, self.lineEdit_data_7_7, self.lineEdit_period_7],
             "btn": [self.btn_arbitrary_send_7, self.btn_arbitrary_clear_7]},
            {"label": [self.label_message_id_8], "chkbox": [self.chkbox_period_8],
             "combo_box": [self.comboBox_user_signal_mess_name_8, self.comboBox_user_signal_bus_8],
             "line_edit": [self.lineEdit_data_8_0, self.lineEdit_data_8_1, self.lineEdit_data_8_2,
                           self.lineEdit_data_8_3, self.lineEdit_data_8_4, self.lineEdit_data_8_5,
                           self.lineEdit_data_8_6, self.lineEdit_data_8_7, self.lineEdit_period_8],
             "btn": [self.btn_arbitrary_send_8, self.btn_arbitrary_clear_8]},
            {"label": [self.label_message_id_9], "chkbox": [self.chkbox_period_9],
             "combo_box": [self.comboBox_user_signal_mess_name_9, self.comboBox_user_signal_bus_9],
             "line_edit": [self.lineEdit_data_9_0, self.lineEdit_data_9_1, self.lineEdit_data_9_2,
                           self.lineEdit_data_9_3, self.lineEdit_data_9_4, self.lineEdit_data_9_5,
                           self.lineEdit_data_9_6, self.lineEdit_data_9_7, self.lineEdit_period_9],
             "btn": [self.btn_arbitrary_send_9, self.btn_arbitrary_clear_9]},
            {"label": [self.label_message_id_10], "chkbox": [self.chkbox_period_10],
             "combo_box": [self.comboBox_user_signal_mess_name_10, self.comboBox_user_signal_bus_10],
             "line_edit": [self.lineEdit_data_10_0, self.lineEdit_data_10_1, self.lineEdit_data_10_2,
                           self.lineEdit_data_10_3, self.lineEdit_data_10_4, self.lineEdit_data_10_5,
                           self.lineEdit_data_10_6, self.lineEdit_data_10_7, self.lineEdit_period_10],
             "btn": [self.btn_arbitrary_send_10, self.btn_arbitrary_clear_10]}]

        self.entire_message_reset()

        self.message_count = 0

        self.signal_list = []

        self.signal_list_flag = True

        self.prev_list_num = 0

        self.reset_flag = True

        # self.label_message_id.setStyleSheet(f"color: {color}")
        # self.lineEdit_message_id.setEnabled(flag)
        # self.btn_arbitrary_send.setEnabled(flag)

        # if self.user_signal_obj.chkbox_period.isChecked():
        #     self.user_signal_obj.lineEdit_period.setEnabled(True)
        # else:
        #     self.user_signal_obj.lineEdit_period.setEnabled(False)

    def signal_init(self):
        pass

    def change_height(self):
        self.setFixedHeight(self.height)

    def add_message_handler(self):
        if self.message_count < 9:
            self.height += 30
            self.message_count += 1
            self.change_height()

            self.message_setting(self.message_comp_list[self.message_count], True)

    def remove_message_handler(self):
        if self.message_count == 0:
            self.data_clear(self.message_comp_list[self.message_count])
        else:
            self.message_setting(self.message_comp_list[self.message_count], False)
            self.height -= 30
            self.change_height()
            self.message_count -= 1

    def message_setting(self, message_comp_set, visible_flag=False):
        for comp_int in message_comp_set.values():
            for comp in comp_int:
                comp.setVisible(visible_flag)
        self.data_clear(message_comp_set)

    def data_clear(self, message_comp_set=None):
        if message_comp_set:
            reset_set = message_comp_set
        else:
            clear_num = int(self.sender().objectName()[-1])
            reset_set = self.message_comp_list[clear_num - 1]

        for comp in reset_set["line_edit"]:
            comp.setText("")
        reset_set["combo_box"][0].clear()
        reset_set["combo_box"][0].addItem(self.default_message_item)
        reset_set["combo_box"][1].clear()
        reset_set["combo_box"][1].addItem(self.default_bus_item)

        for comp in reset_set["chkbox"]:
            if comp.isChecked():
                comp.setChecked(False)

    def entire_message_reset(self):
        if not self.height or self.height > self.height_init:
            self.height = self.height_init
        self.change_height()
        self.message_count = 0
        for i in range(len(self.message_comp_list)):
            if i == 0:
                visable_flag = True
            else:
                visable_flag = False
            self.message_setting(self.message_comp_list[i], visible_flag=visable_flag)

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
