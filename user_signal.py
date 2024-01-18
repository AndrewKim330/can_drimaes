from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import data_identifier as data_id
import can_thread as worker


class UserSignal(QDialog):

    def __init__(self, base_dir, main_obj):
        super().__init__()
        self.signal_ui = uic.loadUi(base_dir + r"./src/can_user_signal_ui.ui", self)
        self.setWindowIcon(QIcon(base_dir + r"./src/drimaes_icon.ico"))
        self.setWindowTitle("User Defined Signal for E-51 IVI CAN Simulator")
        self.show()

        self.height_init = 170
        self.height = None
        self.main_obj = main_obj

        self.mani_set = {0: "N", 1: "N", 2: "N", 3: "N", 4: "N", 5: "N", 6: "N", 7: "N", 8: "N", 9: "N"}

        self.bus_selector = {"C": None, "P": None}

        if main_obj.c_can_bus:
            self.bus_selector["C"] = "C-CAN"
        if main_obj.p_can_bus:
            self.bus_selector["P"] = "P-CAN"

        self.tx_name_set = set()
        self.default_message_item = "--Select signal--"
        self.default_bus_item = "--Select bus--"

        self.comboBox_user_signal_bus_0.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_1.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_2.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_3.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_4.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_5.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_6.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_7.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_8.currentIndexChanged.connect(self.bus_change_mess_name)
        self.comboBox_user_signal_bus_9.currentIndexChanged.connect(self.bus_change_mess_name)

        self.comboBox_user_signal_mess_name_0.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_1.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_2.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_3.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_4.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_5.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_6.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_7.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_8.currentIndexChanged.connect(self.signal_select)
        self.comboBox_user_signal_mess_name_9.currentIndexChanged.connect(self.signal_select)

        self.btn_arbitrary_add_signal.released.connect(self.add_message_handler)
        self.btn_arbitrary_remove_signal.released.connect(self.remove_message_handler)
        self.btn_arbitrary_reset.released.connect(self.entire_signal_reset)

        self.btn_arbitrary_clear_0.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_1.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_2.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_3.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_4.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_5.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_6.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_7.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_8.released.connect(self.single_signal_clear)
        self.btn_arbitrary_clear_9.released.connect(self.single_signal_clear)

        self.chkbox_auto_fill_0.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_1.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_2.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_3.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_4.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_5.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_6.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_7.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_8.stateChanged.connect(self.period_enable_set)
        self.chkbox_auto_fill_9.stateChanged.connect(self.period_enable_set)

        self.lineEdit_id_0.textChanged.connect(self.id_detect)
        self.lineEdit_id_1.textChanged.connect(self.id_detect)
        self.lineEdit_id_2.textChanged.connect(self.id_detect)
        self.lineEdit_id_3.textChanged.connect(self.id_detect)
        self.lineEdit_id_4.textChanged.connect(self.id_detect)
        self.lineEdit_id_5.textChanged.connect(self.id_detect)
        self.lineEdit_id_6.textChanged.connect(self.id_detect)
        self.lineEdit_id_7.textChanged.connect(self.id_detect)
        self.lineEdit_id_8.textChanged.connect(self.id_detect)
        self.lineEdit_id_9.textChanged.connect(self.id_detect)

        self.btn_arbitrary_send_0.released.connect(self.data_send)
        self.btn_arbitrary_send_1.released.connect(self.data_send)
        self.btn_arbitrary_send_2.released.connect(self.data_send)
        self.btn_arbitrary_send_3.released.connect(self.data_send)
        self.btn_arbitrary_send_4.released.connect(self.data_send)
        self.btn_arbitrary_send_5.released.connect(self.data_send)
        self.btn_arbitrary_send_6.released.connect(self.data_send)
        self.btn_arbitrary_send_7.released.connect(self.data_send)
        self.btn_arbitrary_send_8.released.connect(self.data_send)
        self.btn_arbitrary_send_9.released.connect(self.data_send)

        self.send_data = [
            {"id": None, "data": [], "period": None, "auto_fill": True}, {"id": None, "data": [], "period": None, "auto_fill": True},
            {"id": None, "data": [], "period": None, "auto_fill": True}, {"id": None, "data": [], "period": None, "auto_fill": True},
            {"id": None, "data": [], "period": None, "auto_fill": True}, {"id": None, "data": [], "period": None, "auto_fill": True},
            {"id": None, "data": [], "period": None, "auto_fill": True}, {"id": None, "data": [], "period": None, "auto_fill": True},
            {"id": None, "data": [], "period": None, "auto_fill": True}, {"id": None, "data": [], "period": None, "auto_fill": True}]

        self.message_comp_list = [
            {"chkbox": [self.chkbox_auto_fill_0], "btn": [self.btn_arbitrary_send_0, self.btn_arbitrary_clear_0],
             "combo_box": [self.comboBox_user_signal_mess_name_0, self.comboBox_user_signal_bus_0],
             "line_edit": [self.lineEdit_data_0_0, self.lineEdit_data_0_1, self.lineEdit_data_0_2,
                           self.lineEdit_data_0_3, self.lineEdit_data_0_4, self.lineEdit_data_0_5,
                           self.lineEdit_data_0_6, self.lineEdit_data_0_7, self.lineEdit_period_0, self.lineEdit_id_0]},
            {"chkbox": [self.chkbox_auto_fill_1], "btn": [self.btn_arbitrary_send_1, self.btn_arbitrary_clear_1],
             "combo_box": [self.comboBox_user_signal_mess_name_1, self.comboBox_user_signal_bus_1],
             "line_edit": [self.lineEdit_data_1_0, self.lineEdit_data_1_1, self.lineEdit_data_1_2,
                           self.lineEdit_data_1_3, self.lineEdit_data_1_4, self.lineEdit_data_1_5,
                           self.lineEdit_data_1_6, self.lineEdit_data_1_7, self.lineEdit_period_1, self.lineEdit_id_1]},
            {"chkbox": [self.chkbox_auto_fill_2], "btn": [self.btn_arbitrary_send_2, self.btn_arbitrary_clear_2],
             "combo_box": [self.comboBox_user_signal_mess_name_2, self.comboBox_user_signal_bus_2],
             "line_edit": [self.lineEdit_data_2_0, self.lineEdit_data_2_1, self.lineEdit_data_2_2,
                           self.lineEdit_data_2_3, self.lineEdit_data_2_4, self.lineEdit_data_2_5,
                           self.lineEdit_data_2_6, self.lineEdit_data_2_7, self.lineEdit_period_2, self.lineEdit_id_2]},
            {"chkbox": [self.chkbox_auto_fill_3], "btn": [self.btn_arbitrary_send_3, self.btn_arbitrary_clear_3],
             "combo_box": [self.comboBox_user_signal_mess_name_3, self.comboBox_user_signal_bus_3],
             "line_edit": [self.lineEdit_data_3_0, self.lineEdit_data_3_1, self.lineEdit_data_3_2,
                           self.lineEdit_data_3_3, self.lineEdit_data_3_4, self.lineEdit_data_3_5,
                           self.lineEdit_data_3_6, self.lineEdit_data_3_7, self.lineEdit_period_3, self.lineEdit_id_3]},
            {"chkbox": [self.chkbox_auto_fill_4], "btn": [self.btn_arbitrary_send_4, self.btn_arbitrary_clear_4],
             "combo_box": [self.comboBox_user_signal_mess_name_4, self.comboBox_user_signal_bus_4],
             "line_edit": [self.lineEdit_data_4_0, self.lineEdit_data_4_1, self.lineEdit_data_4_2,
                           self.lineEdit_data_4_3, self.lineEdit_data_4_4, self.lineEdit_data_4_5,
                           self.lineEdit_data_4_6, self.lineEdit_data_4_7, self.lineEdit_period_4, self.lineEdit_id_4]},
            {"chkbox": [self.chkbox_auto_fill_5], "btn": [self.btn_arbitrary_send_5, self.btn_arbitrary_clear_5],
             "combo_box": [self.comboBox_user_signal_mess_name_5, self.comboBox_user_signal_bus_5],
             "line_edit": [self.lineEdit_data_5_0, self.lineEdit_data_5_1, self.lineEdit_data_5_2,
                           self.lineEdit_data_5_3, self.lineEdit_data_5_4, self.lineEdit_data_5_5,
                           self.lineEdit_data_5_6, self.lineEdit_data_5_7, self.lineEdit_period_5, self.lineEdit_id_5]},
            {"chkbox": [self.chkbox_auto_fill_6], "btn": [self.btn_arbitrary_send_6, self.btn_arbitrary_clear_6],
             "combo_box": [self.comboBox_user_signal_mess_name_6, self.comboBox_user_signal_bus_6],
             "line_edit": [self.lineEdit_data_6_0, self.lineEdit_data_6_1, self.lineEdit_data_6_2,
                           self.lineEdit_data_6_3, self.lineEdit_data_6_4, self.lineEdit_data_6_5,
                           self.lineEdit_data_6_6, self.lineEdit_data_6_7, self.lineEdit_period_6, self.lineEdit_id_6]},
            {"chkbox": [self.chkbox_auto_fill_7], "btn": [self.btn_arbitrary_send_7, self.btn_arbitrary_clear_7],
             "combo_box": [self.comboBox_user_signal_mess_name_7, self.comboBox_user_signal_bus_7],
             "line_edit": [self.lineEdit_data_7_0, self.lineEdit_data_7_1, self.lineEdit_data_7_2,
                           self.lineEdit_data_7_3, self.lineEdit_data_7_4, self.lineEdit_data_7_5,
                           self.lineEdit_data_7_6, self.lineEdit_data_7_7, self.lineEdit_period_7, self.lineEdit_id_7]},
            {"chkbox": [self.chkbox_auto_fill_8], "btn": [self.btn_arbitrary_send_8, self.btn_arbitrary_clear_8],
             "combo_box": [self.comboBox_user_signal_mess_name_8, self.comboBox_user_signal_bus_8],
             "line_edit": [self.lineEdit_data_8_0, self.lineEdit_data_8_1, self.lineEdit_data_8_2,
                           self.lineEdit_data_8_3, self.lineEdit_data_8_4, self.lineEdit_data_8_5,
                           self.lineEdit_data_8_6, self.lineEdit_data_8_7, self.lineEdit_period_8, self.lineEdit_id_8]},
            {"chkbox": [self.chkbox_auto_fill_9], "btn": [self.btn_arbitrary_send_9, self.btn_arbitrary_clear_9],
             "combo_box": [self.comboBox_user_signal_mess_name_9, self.comboBox_user_signal_bus_9],
             "line_edit": [self.lineEdit_data_9_0, self.lineEdit_data_9_1, self.lineEdit_data_9_2,
                           self.lineEdit_data_9_3, self.lineEdit_data_9_4, self.lineEdit_data_9_5,
                           self.lineEdit_data_9_6, self.lineEdit_data_9_7, self.lineEdit_period_9, self.lineEdit_id_9]}]

        self.user_signal_worker = [
            worker.UserSignal(parent=self, handle_num=0), worker.UserSignal(parent=self, handle_num=1),
            worker.UserSignal(parent=self, handle_num=2), worker.UserSignal(parent=self, handle_num=3),
            worker.UserSignal(parent=self, handle_num=4), worker.UserSignal(parent=self, handle_num=5),
            worker.UserSignal(parent=self, handle_num=6), worker.UserSignal(parent=self, handle_num=7),
            worker.UserSignal(parent=self, handle_num=8), worker.UserSignal(parent=self, handle_num=9)]

        self.user_signal_worker[0].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[1].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[2].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[3].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[4].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[5].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[6].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[7].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[8].user_defined_signal.connect(self.main_obj.can_signal_sender)
        self.user_signal_worker[9].user_defined_signal.connect(self.main_obj.can_signal_sender)

        self.entire_signal_reset()
        self.message_count = 0

        self.c_can_set = data_id.master_set_c
        self.p_can_set = data_id.master_set_p

        self.signal_list = []

        self.signal_list_flag = True

        self.prev_list_num = 0

        self.reset_flag = True

    def change_height(self):
        self.setFixedHeight(self.height)

    def add_message_handler(self):
        if self.message_count < 9:
            self.height += 40
            self.message_count += 1
            self.change_height()

            self.single_signal_setting(self.message_comp_list[self.message_count], True)

    def remove_message_handler(self):
        if self.message_count == 0:
            self.single_signal_clear(self.message_comp_list[self.message_count])
        else:
            self.single_signal_setting(self.message_comp_list[self.message_count], False)
            self.height -= 40
            self.change_height()
            self.message_count -= 1

    def single_signal_setting(self, message_comp_set, visible_flag=False):
        for comp_int in message_comp_set.values():
            for comp in comp_int:
                comp.setVisible(visible_flag)
        self.single_signal_clear(message_comp_set)

    def single_signal_clear(self, message_comp_set=None):
        if message_comp_set:
            clear_num = int(message_comp_set["chkbox"][0].objectName()[-1])
            reset_set = message_comp_set
        else:
            clear_num = int(self.sender().objectName()[-1])
            reset_set = self.message_comp_list[clear_num]

        self.line_edit_comp_text_clear(reset_set["line_edit"])
        self.send_data[clear_num]["data"] = []
        self.send_data[clear_num]["period"] = None

        reset_set["combo_box"][0].clear()
        reset_set["combo_box"][0].addItem(self.default_message_item)
        reset_set["combo_box"][1].clear()
        reset_set["combo_box"][1].addItem(self.default_bus_item)

        for bus in self.bus_selector.values():
            if bus:
                reset_set["combo_box"][1].addItem(bus)

        for comp in reset_set["chkbox"]:
            if comp.isChecked():
                comp.setChecked(True)
        if not reset_set["chkbox"][0].isChecked():
            reset_set["chkbox"][0].setChecked(True)

        self.user_signal_worker[clear_num]._isRunning = False

    def entire_signal_reset(self):
        if not self.height or self.height > self.height_init:
            self.height = self.height_init
        self.change_height()
        self.message_count = 0
        for i in range(len(self.message_comp_list)):
            if i == 0:
                visible_flag = True
            else:
                visible_flag = False
            self.single_signal_setting(self.message_comp_list[i], visible_flag=visible_flag)

    def bus_change_mess_name(self):
        handle_num = int(self.sender().objectName()[-1])
        if self.sender().currentText() == "C-CAN":
            self.mani_set[handle_num] = "C"
            mess_set = self.c_can_set
        elif self.sender().currentText() == "P-CAN":
            self.mani_set[handle_num] = "P"
            mess_set = self.p_can_set
        else:
            self.mani_set[handle_num] = "N"
            self.message_comp_list[handle_num]["combo_box"][0].clear()
            self.message_comp_list[handle_num]["combo_box"][0].addItem(self.default_message_item)
            return 0

        for mess in mess_set.values():
            if mess["mess_name"][:3] == "MMI":
                if mess["mess_name"] == "MMI_DiagReq":
                    pass
                elif mess["mess_name"] == "Func_DiagReq":
                    pass
                else:
                    continue
            self.message_comp_list[handle_num]["combo_box"][0].addItem(mess["mess_name"])

    def signal_select(self):
        if self.sender().currentText() == self.default_message_item:
            handle_num = int(self.sender().objectName()[-1])
            self.message_comp_list[handle_num]["line_edit"][-1].setText("")
            self.message_comp_list[handle_num]["line_edit"][-1].setReadOnly(False)
        else:
            handle_num = int(self.sender().objectName()[-1])
            if self.mani_set[handle_num] == "C":
                mess_set = self.c_can_set
            elif self.mani_set[handle_num] == "P":
                mess_set = self.p_can_set
            else:
                return 0
            for mess in mess_set.values():
                if mess["mess_name"] == self.sender().currentText():
                    self.message_comp_list[handle_num]["line_edit"][-1].setText(f'0x{str(hex(mess["id"])).upper()[2:].zfill(8)}')
                    self.message_comp_list[handle_num]["line_edit"][-1].setReadOnly(True)
                    return 0

    def period_enable_set(self):
        handle_num = int(self.sender().objectName()[-1])
        if self.message_comp_list[handle_num]["chkbox"][0].isChecked():
            self.send_data[handle_num]["auto_fill"] = True
        else:
            self.send_data[handle_num]["auto_fill"] = False

    def id_detect(self):
        handle_num = int(self.sender().objectName()[-1])
        written_txt = self.message_comp_list[handle_num]["line_edit"][-1].text()
        if len(written_txt) > 10:
            QMessageBox.warning(self, "ID Error", "Write 8 digit Hex number\nex) 0x18FFA57F or 18FFA57F")
            return 0
        elif len(written_txt) < 8:
            return 0
        else:
            if len(written_txt) == 10:
                valid_id = written_txt[2:]
            elif len(written_txt) == 8:
                if written_txt[:2] == "0x":
                    return 0
                valid_id = written_txt[:]
            try:
                if len(valid_id) == 8:
                    try:
                        valid_id = int(valid_id, 16)
                        for comp in self.c_can_set.values():
                            if comp["id"] == valid_id:
                                temp_comp = comp
                                break
                        for comp in self.p_can_set.values():
                            if comp["id"] == valid_id:
                                temp_comp = comp
                                break
                        self.message_comp_list[handle_num]["combo_box"][0].setCurrentText(temp_comp["mess_name"])
                        self.send_data[handle_num]["id"] = valid_id
                    except ValueError:
                        QMessageBox.warning(self, "ID Error", "Write the Hex number\n (0~9 or A~F)")
                        return 0
                    except UnboundLocalError:
                        QMessageBox.warning(self, "ID Error", "Write 8 digit Hex number\nex) 0x18FFA57F or 18FFA57F")
                        return 0
                else:
                    QMessageBox.warning(self, "ID Error", "Write 8 digit Hex number\nex) 0x18FFA57F or 18FFA57F")
                    return 0
            except UnboundLocalError:
                QMessageBox.warning(self, "ID Error", "Write 8 digit Hex number\nex) 0x18FFA57F or 18FFA57F")
                return 0

    def signal_data(self, handle_num):
        if self.send_data[handle_num]["id"]:
            data_list = self.message_comp_list[handle_num]["line_edit"][0:8]
            send_list = []
            for line_edit_comp in data_list:
                single_data = line_edit_comp.text()
                try:
                    if single_data[0:2] == '0x':
                        conv_int_data = int(single_data[2:], 16)
                    else:
                        conv_int_data = int(single_data, 16)
                except ValueError:
                    if single_data == "":
                        continue
                    else:
                        QMessageBox.warning(self, "Data Error", "Write the Hex number\n (0x00 ~ 0xFF)")
                        self.line_edit_comp_text_clear(data_list)
                        return False
                if conv_int_data > 0xFF:
                    QMessageBox.warning(self, "Data Error", "Write appropriate range of Hex number\n (0x00 ~ 0xFF)")
                    self.line_edit_comp_text_clear(data_list)
                    return False
                else:
                    send_list.append(conv_int_data)
            data_len = len(send_list)
            if data_len == 0:
                QMessageBox.warning(self, "Data Error", "Insert the 0~8 bytes arbitrary data")
                return False
            else:
                if data_len < 8:
                    if self.send_data[handle_num]["auto_fill"]:
                        for i in range(8 - data_len):
                            send_list.append(0xFF)
                self.send_data[handle_num]["data"] = send_list
        else:
            QMessageBox.warning(self, "ID Error", "Set the CAN id first")
        return True

    def line_edit_comp_text_clear(self, data_list):
        for comp in data_list:
            comp.setText("")

    def signal_period(self, handle_num):
        period = self.message_comp_list[handle_num]["line_edit"][-2].text()
        try:
            conv_int_data = int(period)
            self.send_data[handle_num]["period"] = conv_int_data
        except ValueError:
            if period == "":
                pass
            else:
                QMessageBox.warning(self, "Data Error", "Write the int number of period (ms)")
                return False
        return True

    def data_send(self):
        handle_num = int(self.sender().objectName()[-1])
        if self.signal_data(handle_num) and self.signal_period(handle_num):
            if self.message_comp_list[handle_num]["combo_box"][-1].currentText() == self.default_bus_item:
                QMessageBox.warning(self, "Bus Error", "Select the bus")
                return False
            else:
                self.user_signal_worker[handle_num].bus_selector = self.message_comp_list[handle_num]["combo_box"][-1].currentText()
                self.user_signal_worker[handle_num].send_data = self.send_data[handle_num]
                self.user_signal_worker[handle_num]._isRunning = True
                self.user_signal_worker[handle_num].start()

    def ui_close(self):
        self.close()
