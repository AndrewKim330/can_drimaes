from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class UserFilter(QDialog):

    def __init__(self, base_dir, main_obj):
        super().__init__()
        self.filter_ui = uic.loadUi(base_dir + r"./src/can_user_filter_ui.ui", self)
        self.setWindowIcon(QIcon(base_dir + r"./src/drimaes_icon.ico"))
        self.setWindowTitle("User Defined Filter for E-51 IVI CAN Simulator")
        self.show()

        self.tx_name_set = set()
        self.default_item = "--Select signal--"
        self.comboBox_user_filter.addItem(self.default_item)

        self.main_obj = main_obj

        self.filtered_list = []

        self.filter_list_flag = True
        self.filter_list_init = True

        self.prev_list_num = 0

        self.chkbox_filter_node_acu.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_bcm.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_esc.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_ic.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_pms.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_pms_s.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_pms_c.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_fcs.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_bms.toggled.connect(self.node_filter_toggling)
        self.chkbox_filter_node_mcu.toggled.connect(self.node_filter_toggling)

        self.chkbox_1st.toggled.connect(self.node_filter_toggling)
        self.chkbox_2nd.toggled.connect(self.node_filter_toggling)
        self.chkbox_3rd.toggled.connect(self.node_filter_toggling)
        self.chkbox_4th.toggled.connect(self.node_filter_toggling)
        self.chkbox_5th.toggled.connect(self.node_filter_toggling)

    def node_filter_toggling(self):
        self.main_obj.console_text_clear("tx_console_clear")

    def node_filter(self, tx_name):
        if self.chkbox_filter_node_acu.isChecked():
            if tx_name == "ACU_Status":
                return True

        if self.chkbox_filter_node_bcm.isChecked():
            if tx_name == "BCM_StateUpdate" or tx_name == "BCM_LightChimeReq" or tx_name == "BCM_MMIFBSts" \
                    or tx_name == "SWS-LIN" or tx_name == "SwmCem_Lin4Fr02":
                return True

        if self.chkbox_filter_node_esc.isChecked():
            if tx_name == "ESC_ABS_BrakeSysSts":
                return True

        if self.chkbox_filter_node_ic.isChecked():
            if tx_name == "IC_TC01" or tx_name == "IC_VDHR":
                return True

        if self.chkbox_filter_node_pms.isChecked():
            if tx_name == "PMS_BodyControlInfo" or tx_name == "PMS_PTInfoIndicate" or tx_name == "PMS_VRI":
                return True

        if self.chkbox_filter_node_pms_s.isChecked():
            if tx_name == "HVSM_MMIFBSts":
                return True

        if self.chkbox_filter_node_pms_c.isChecked():
            if tx_name == "SasChas1Fr01":
                return True

        if self.chkbox_filter_node_fcs.isChecked():
            if tx_name == "FCS_AEBS1" or tx_name == "FCS_LDWSystemState":
                return True

        if self.chkbox_filter_node_bms.isChecked():
            if tx_name == "BMS_BatteryInfo" or tx_name == "BMS_ChgInfo":
                return True

        if self.chkbox_filter_node_mcu.isChecked():
            if tx_name == "MCU_MotorElePara":
                return True

        return False

    def user_filter(self, tx_name):
        prev_num = len(self.tx_name_set)
        self.tx_name_set.add(tx_name)
        next_num = len(self.tx_name_set)
        if next_num - prev_num != 0:
            self.comboBox_user_filter.addItem(tx_name)
        if self.comboBox_user_filter.currentText() != self.default_item:
            if len(self.filtered_list) == 0:
                self.filtered_list.append(self.comboBox_user_filter.currentText())
            else:
                temp_list = self.filtered_list[:]
                append_flag = True
                for elem in temp_list:
                    if self.comboBox_user_filter.currentText() == elem:
                        append_flag = False
                if append_flag:
                    self.filtered_list.append(self.comboBox_user_filter.currentText())
        self.user_filter_chkbox(self.filtered_list)
        for i in range(len(self.filtered_list)):
            if tx_name == self.filtered_list[i]:
                return self.user_filter_chkbox(self.filtered_list, chkbox_num=i)
        return False

    def user_filter_chkbox(self, li, chkbox_num=1000):
        present_list_num = len(li)
        if self.prev_list_num != present_list_num:
            self.filter_list_init = True
            self.main_obj.console_text_clear("tx_console_clear")
        self.prev_list_num = len(li)
        if len(li) == 0:
            self.chkbox_1st.setVisible(False)
            self.chkbox_2nd.setVisible(False)
            self.chkbox_3rd.setVisible(False)
            self.chkbox_4th.setVisible(False)
            self.chkbox_5th.setVisible(False)
        elif self.comboBox_user_filter.currentText() == self.default_item:
            self.chkbox_1st.setVisible(False)
            self.chkbox_2nd.setVisible(False)
            self.chkbox_3rd.setVisible(False)
            self.chkbox_4th.setVisible(False)
            self.chkbox_5th.setVisible(False)
            self.filtered_list = []
        else:
            if len(li) == 1 or chkbox_num == 0:
                if self.filter_list_init:
                    self.chkbox_1st.setVisible(True)
                    self.chkbox_1st.setChecked(True)
                    self.filter_list_init = False
                    self.chkbox_1st.setText(li[0])
                else:
                    if self.chkbox_1st.isChecked():
                        return True
                    else:
                        return False
            if len(li) == 2 or chkbox_num == 1:
                if self.filter_list_init:
                    self.chkbox_2nd.setVisible(True)
                    self.chkbox_2nd.setChecked(True)
                    self.filter_list_init = False
                    self.chkbox_2nd.setText(li[1])
                else:
                    if self.chkbox_2nd.isChecked():
                        return True
                    else:
                        return False
            elif len(li) == 3 or chkbox_num == 2:
                if self.filter_list_init:
                    self.chkbox_3rd.setVisible(True)
                    self.chkbox_3rd.setChecked(True)
                    self.filter_list_init = False
                    self.chkbox_3rd.setText(li[2])
                else:
                    if self.chkbox_3rd.isChecked():
                        return True
                    else:
                        return False
            elif len(li) == 4 or chkbox_num == 3:
                if self.filter_list_init:
                    self.chkbox_4th.setVisible(True)
                    self.chkbox_4th.setChecked(True)
                    self.filter_list_init = False
                    self.chkbox_4th.setText(li[3])
                else:
                    if self.chkbox_4th.isChecked():
                        return True
                    else:
                        return False
            elif len(li) == 5 or chkbox_num == 4:
                if self.filter_list_init:
                    self.chkbox_5th.setVisible(True)
                    self.chkbox_5th.setChecked(True)
                    self.filter_list_init = False
                    self.chkbox_5th.setText(li[4])
                else:
                    if self.chkbox_5th.isChecked():
                        return True
                    else:
                        return False

    def ui_close(self):
        self.close()
