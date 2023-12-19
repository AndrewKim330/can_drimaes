import time
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import security_algorithm as algo
import sig_generator as sig_gen
import data_identifier as data_id


class DiagMain(QDialog):

    def __init__(self, base_dir, main_obj):
        super().__init__()
        self.ui = uic.loadUi(base_dir + r"./src/can_diagnosis_ui.ui", self)
        self.setWindowIcon(QIcon("./src/drimaes_icon.ico"))
        self.setWindowTitle("Diagnostic Console for E-51 IVI CAN Simulator")
        self.main_obj = main_obj
        self.show()

        if main_obj.c_can_bus:
            self.c_can_bus = main_obj.c_can_bus
        if main_obj.p_can_bus:
            self.p_can_bus = main_obj.p_can_bus

        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.write_data = [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA]
        self.raw_data = []
        self.res_data = []
        self.temp_list = []
        self.graph_data_list = []
        self.data_len = 0
        self.dtc_num = 0
        self.data_type = None
        self.req_seed = []

        self.recv_flag = False

        self.diag_tester_id = 0x18da41f1

        self.flow = False

        self.write_txt = ''

        self.diag_btn_text = None
        self.diag_success_byte = None
        self.diag_failure_byte = 0x7f

        self.test_mode_basic = False

        self.txt_domain = 'Default'
        self.color_domain = 'gray'
        self.flag_domain = False

        self.flow_control_len = 0

        self.write_secu_nrc = True

        # Connect diagnosis basic buttons to diagnostic handling function
        self.btn_sess_default.clicked.connect(self.diag_func)
        self.btn_sess_extended.clicked.connect(self.diag_func)
        self.btn_sess_nrc_12.clicked.connect(self.diag_func)
        self.btn_sess_nrc_13.clicked.connect(self.diag_func)

        self.btn_reset_sw.clicked.connect(self.diag_func)
        self.btn_reset_hw.clicked.connect(self.diag_func)
        self.btn_reset_nrc_12.clicked.connect(self.diag_func)
        self.btn_reset_nrc_13.clicked.connect(self.diag_func)
        self.btn_reset_nrc_7f_sw.clicked.connect(self.diag_func)
        self.btn_reset_nrc_7f_hw.clicked.connect(self.diag_func)
        self.btn_reset_nrc_22_sw.clicked.connect(self.diag_func)
        self.btn_reset_nrc_22_hw.clicked.connect(self.diag_func)

        self.btn_tester.released.connect(self.diag_func)
        self.btn_tester_nrc_12.released.connect(self.diag_func)
        self.btn_tester_nrc_13.released.connect(self.diag_func)

        main_obj.tester_worker.tester_signal.connect(self.diag_data_collector)
        self.chkbox_tester_present.released.connect(self.tester_present_handler)

        self.chkbox_diag_test_mode_basic.released.connect(self.set_diag_basic_btns_labels)
        self.chkbox_diag_functional_domain_basic.released.connect(self.set_diag_basic_btns_labels)
        self.chkbox_diag_compression_bit_basic.released.connect(self.set_diag_basic_btns_labels)
        self.btn_diag_reset_basic.released.connect(self.set_diag_basic_btns_labels)

        # Connect data identification buttons to diagnostic handling function
        self.btn_id_ecu_num.released.connect(self.diag_func)
        self.btn_id_ecu_supp.released.connect(self.diag_func)
        self.btn_id_vin.released.connect(self.diag_func)
        self.btn_id_install_date.released.connect(self.diag_func)
        self.btn_id_diag_ver.released.connect(self.diag_func)
        self.btn_id_sys_name.released.connect(self.diag_func)
        self.btn_id_active_sess.released.connect(self.diag_func)
        self.btn_id_veh_name.released.connect(self.diag_func)
        self.btn_id_ecu_serial.released.connect(self.diag_func)
        self.btn_id_hw_ver.released.connect(self.diag_func)
        self.btn_id_sw_ver.released.connect(self.diag_func)
        self.btn_id_ecu_manu_date.released.connect(self.diag_func)
        self.btn_id_assy_num.released.connect(self.diag_func)
        self.btn_id_net_config.released.connect(self.diag_func)
        self.btn_id_ecu_sts_info.released.connect(self.diag_func)
        self.btn_id_nrc_13.released.connect(self.diag_func)
        self.btn_id_nrc_31.released.connect(self.diag_func)

        self.chkbox_diag_test_mode_did.released.connect(self.set_diag_did_btns_labels)
        self.chkbox_diag_functional_domain_did.released.connect(self.set_diag_did_btns_labels)
        self.btn_diag_reset_did.released.connect(self.set_diag_did_btns_labels)

        # Connect communication control buttons to diagnostic handling function
        self.btn_comm_cont_all_en.released.connect(self.diag_func)
        self.btn_comm_cont_tx_dis.released.connect(self.diag_func)
        self.btn_comm_cont_all_dis.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_12.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_13.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_31.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_22_all_en.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_22_tx_dis.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_22_all_dis.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_7f_all_en.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_7f_tx_dis.released.connect(self.diag_func)
        self.btn_comm_cont_nrc_7f_all_dis.released.connect(self.diag_func)

        self.chkbox_diag_functional_domain_comm_cont.released.connect(self.set_diag_comm_cont_btns_labels)
        self.chkbox_diag_compression_bit_comm_cont.released.connect(self.set_diag_comm_cont_btns_labels)
        self.chkbox_diag_test_mode_comm_cont.released.connect(self.set_diag_comm_cont_btns_labels)
        self.btn_diag_reset_comm_cont.released.connect(self.set_diag_comm_cont_btns_labels)

        # Connect security control buttons to diagnostic handling function
        self.btn_sec_req_seed.released.connect(self.diag_func)
        self.btn_sec_send_key.released.connect(self.diag_func)
        self.btn_sec_seed_plus_send.released.connect(self.diag_func)
        self.btn_sec_nrc_12.released.connect(self.diag_func)
        self.btn_sec_nrc_13.released.connect(self.diag_func)
        self.btn_sec_nrc_24.released.connect(self.diag_func)
        self.btn_sec_nrc_35.released.connect(self.diag_func)
        self.btn_sec_nrc_36.released.connect(self.diag_func)
        self.btn_sec_nrc_37.released.connect(self.diag_func)
        self.btn_sec_nrc_7f_req.released.connect(self.diag_func)
        self.btn_sec_nrc_7f_send.released.connect(self.diag_func)

        self.chkbox_diag_test_mode_sec.released.connect(self.set_diag_sec_btns_labels)
        self.btn_diag_reset_sec.released.connect(self.set_diag_sec_btns_labels)

        # Connect data write buttons to diagnostic handling function
        self.btn_write_vin.released.connect(self.diag_func)
        self.btn_write_vin_init.released.connect(self.diag_func)
        self.btn_write_install_date.released.connect(self.diag_func)
        self.btn_write_veh_name.released.connect(self.diag_func)
        self.btn_write_sys_name.released.connect(self.diag_func)
        self.btn_write_net_config.released.connect(self.diag_func)
        self.btn_write_nrc_13.released.connect(self.diag_func)
        self.btn_write_nrc_7f_vin.released.connect(self.diag_func)
        self.btn_write_nrc_7f_install_date.released.connect(self.diag_func)
        self.btn_write_nrc_7f_veh_name.released.connect(self.diag_func)
        self.btn_write_nrc_7f_sys_name.released.connect(self.diag_func)
        self.btn_write_nrc_7f_net_config.released.connect(self.diag_func)
        self.btn_write_nrc_33_vin.released.connect(self.diag_func)
        self.btn_write_nrc_33_install_date.released.connect(self.diag_func)
        self.btn_write_nrc_33_veh_name.released.connect(self.diag_func)
        self.btn_write_nrc_33_sys_name.released.connect(self.diag_func)
        self.btn_write_nrc_33_net_config.released.connect(self.diag_func)
        self.btn_write_nrc_22_vin.released.connect(self.diag_func)
        self.btn_write_nrc_22_install_date.released.connect(self.diag_func)
        self.btn_write_nrc_22_veh_name.released.connect(self.diag_func)
        self.btn_write_nrc_22_sys_name.released.connect(self.diag_func)
        self.btn_write_nrc_22_net_config.released.connect(self.diag_func)

        self.chkbox_diag_test_mode_write.released.connect(self.set_diag_write_btns_labels)
        self.btn_write_data_send.clicked.connect(self.write_data_sender)

        # Connect dtc buttons to diagnostic handling function
        self.btn_mem_fault_num_check.clicked.connect(self.diag_func)
        self.btn_mem_fault_list_check.clicked.connect(self.diag_func)
        self.btn_mem_fault_reset.clicked.connect(self.diag_func)
        self.btn_mem_fault_avail_sts_mask.clicked.connect(self.diag_func)
        self.btn_mem_fault_nrc_12.clicked.connect(self.diag_func)
        self.btn_mem_fault_nrc_13.clicked.connect(self.diag_func)
        self.btn_mem_fault_nrc_13_reset.clicked.connect(self.diag_func)
        self.btn_mem_fault_nrc_22_reset.clicked.connect(self.diag_func)
        self.btn_mem_fault_nrc_31_reset.clicked.connect(self.diag_func)

        self.chkbox_diag_functional_domain_mem_fault.released.connect(self.set_diag_mem_fault_btns_labels)
        self.chkbox_diag_test_mode_mem_fault.released.connect(self.set_diag_mem_fault_btns_labels)
        self.btn_diag_reset_mem_fault.released.connect(self.set_diag_mem_fault_btns_labels)

        # Connect dtc control buttons to diagnostic handling function
        self.btn_dtc_cont_en.clicked.connect(self.diag_func)
        self.btn_dtc_cont_dis.clicked.connect(self.diag_func)
        self.btn_dtc_cont_nrc_12.clicked.connect(self.diag_func)
        self.btn_dtc_cont_nrc_13.clicked.connect(self.diag_func)
        self.btn_dtc_cont_nrc_7f_en.clicked.connect(self.diag_func)
        self.btn_dtc_cont_nrc_7f_dis.clicked.connect(self.diag_func)
        self.btn_dtc_cont_nrc_22_en.clicked.connect(self.diag_func)
        self.btn_dtc_cont_nrc_22_dis.clicked.connect(self.diag_func)

        self.chkbox_diag_test_mode_dtc_cont.released.connect(self.set_diag_dtc_cont_btns_labels)
        self.chkbox_diag_functional_domain_dtc_cont.released.connect(self.set_diag_dtc_cont_btns_labels)
        self.chkbox_diag_compression_bit_dtc_cont.released.connect(self.set_diag_dtc_cont_btns_labels)
        self.btn_diag_reset_dtc_cont.released.connect(self.set_diag_dtc_cont_btns_labels)

        self.btn_diag_console_clear.clicked.connect(main_obj.console_text_clear)
        self.btn_write_data_clear.clicked.connect(main_obj.console_text_clear)
        self.btn_diag_dtc_console_clear.released.connect(main_obj.console_text_clear)

        self.treeWidget_dtc.setColumnWidth(1, 350)

        self.set_diag_basic_btns_labels(False)
        self.set_diag_did_btns_labels(False)
        self.set_diag_sec_btns_labels(False)
        self.set_diag_write_btns_labels(False)
        self.set_diag_comm_cont_btns_labels(False)
        self.set_diag_mem_fault_btns_labels(False)
        self.set_diag_dtc_cont_btns_labels(False)

    def set_diag_basic_btns_labels(self, flag=True):
        if self.chkbox_diag_test_mode_basic.isChecked():
            self.chkbox_diag_compression_bit_basic.setEnabled(True)
            self.chkbox_diag_functional_domain_basic.setEnabled(True)
            color = 'black'
            txt = "Not tested"
            if self.chkbox_diag_functional_domain_basic.isChecked():
                self.diag_tester_id = 0x18db33f1
            else:
                self.diag_tester_id = 0x18da41f1

        else:
            if self.chkbox_diag_functional_domain_basic.isChecked():
                self.diag_tester_id = 0x18da41f1
                self.chkbox_diag_functional_domain_basic.toggle()
            if self.chkbox_diag_compression_bit_basic.isChecked():
                self.chkbox_diag_compression_bit_basic.toggle()
            self.chkbox_diag_compression_bit_basic.setEnabled(False)
            self.chkbox_diag_functional_domain_basic.setEnabled(False)
            color = 'gray'
            txt = "Default"

        self.btn_sess_default.setEnabled(flag)
        self.label_sess_default.setText(f"{txt}")
        self.label_sess_default.setStyleSheet(f"color: {color}")
        self.btn_sess_extended.setEnabled(flag)
        self.label_sess_extended.setText(f"{txt}")
        self.label_sess_extended.setStyleSheet(f"color: {color}")
        self.btn_sess_nrc_12.setEnabled(flag)
        self.label_sess_nrc_12.setText(f"{txt}")
        self.label_sess_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_sess_nrc_13.setEnabled(flag)
        self.label_sess_nrc_13.setText(f"{txt}")
        self.label_sess_nrc_13.setStyleSheet(f"color: {color}")

        self.btn_reset_sw.setEnabled(flag)
        self.label_reset_sw.setText(f"{txt}")
        self.label_reset_sw.setStyleSheet(f"color: {color}")
        self.btn_reset_hw.setEnabled(flag)
        self.label_reset_hw.setText(f"{txt}")
        self.label_reset_hw.setStyleSheet(f"color: {color}")
        self.btn_reset_nrc_12.setEnabled(flag)
        self.label_reset_nrc_12.setText(f"{txt}")
        self.label_reset_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_reset_nrc_13.setEnabled(flag)
        self.label_reset_nrc_13.setText(f"{txt}")
        self.label_reset_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_reset_nrc_7f_sw.setEnabled(flag)
        self.label_reset_nrc_7f_sw.setText(f"{txt}")
        self.label_reset_nrc_7f_sw.setStyleSheet(f"color: {color}")
        self.btn_reset_nrc_7f_hw.setEnabled(flag)
        self.label_reset_nrc_7f_hw.setText(f"{txt}")
        self.label_reset_nrc_7f_hw.setStyleSheet(f"color: {color}")
        self.btn_reset_nrc_22_sw.setEnabled(flag)
        self.label_reset_nrc_22_sw.setText(f"{txt}")
        self.label_reset_nrc_22_sw.setStyleSheet(f"color: {color}")
        self.btn_reset_nrc_22_hw.setEnabled(flag)
        self.label_reset_nrc_22_hw.setText(f"{txt}")
        self.label_reset_nrc_22_hw.setStyleSheet(f"color: {color}")

        self.btn_tester.setEnabled(flag)
        self.label_tester.setText(f"{txt}")
        self.label_tester.setStyleSheet(f"color: {color}")
        self.btn_tester_nrc_12.setEnabled(flag)
        self.label_tester_nrc_12.setText(f"{txt}")
        self.label_tester_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_tester_nrc_13.setEnabled(flag)
        self.label_tester_nrc_13.setText(f"{txt}")
        self.label_tester_nrc_13.setStyleSheet(f"color: {color}")
        self.chkbox_tester_present.setEnabled(flag)

        self.btn_diag_reset_basic.setEnabled(flag)
        self.chkbox_diag_test_mode_basic.setEnabled(flag)

    def set_diag_did_btns_labels(self, flag=True):
        if self.chkbox_diag_test_mode_did.isChecked():
            self.chkbox_diag_functional_domain_did.setEnabled(True)
            color = 'black'
            txt = "Not tested"
            if self.chkbox_diag_functional_domain_did.isChecked():
                self.diag_tester_id = 0x18db33f1
                self.txt_domain = 'Test Unable on\nFunctional Domain'
                self.color_domain = 'gray'
                self.flag_domain = False
            else:
                self.diag_tester_id = 0x18da41f1
                self.flag_domain = flag
                self.txt_domain = txt
                self.color_domain = color
        else:
            if self.chkbox_diag_functional_domain_did.isChecked():
                self.diag_tester_id = 0x18da41f1
                self.chkbox_diag_functional_domain_did.toggle()
            self.chkbox_diag_functional_domain_did.setEnabled(False)
            color = 'gray'
            txt = "Default"
            self.txt_domain = txt
            self.flag_domain = flag
            self.color_domain = color

        if self.sender():
            if self.sender().objectName() == "btn_bus_start" or self.sender().objectName() == "chkbox_diag_console":
                self.label_id.setStyleSheet(f"color: black")
                self.label_id_data_length.setStyleSheet(f"color: black")
            elif self.sender().objectName() == "btn_bus_stop":
                self.label_id.setStyleSheet(f"color: gray")
                self.label_id_data_length.setStyleSheet(f"color: gray")
                self.label_id_data_length.setText("Data Length : -")
                self.lineEdit_id_data.setText('')

        self.lineEdit_id_data.setEnabled(flag)
        self.btn_id_ecu_num.setEnabled(self.flag_domain)
        self.label_id_ecu_num.setText(f"{self.txt_domain}")
        self.label_id_ecu_num.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_ecu_supp.setEnabled(self.flag_domain)
        self.label_id_ecu_supp.setText(f"{self.txt_domain}")
        self.label_id_ecu_supp.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_vin.setEnabled(self.flag_domain)
        self.label_id_vin.setText(f"{self.txt_domain}")
        self.label_id_vin.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_install_date.setEnabled(flag)
        self.label_id_install_date.setText(f"{txt}")
        self.label_id_install_date.setStyleSheet(f"color: {color}")
        self.btn_id_diag_ver.setEnabled(flag)
        self.label_id_diag_ver.setText(f"{txt}")
        self.label_id_diag_ver.setStyleSheet(f"color: {color}")
        self.btn_id_sys_name.setEnabled(self.flag_domain)
        self.label_id_sys_name.setText(f"{self.txt_domain}")
        self.label_id_sys_name.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_active_sess.setEnabled(flag)
        self.label_id_active_sess.setText(f"{txt}")
        self.label_id_active_sess.setStyleSheet(f"color: {color}")
        self.btn_id_veh_name.setEnabled(self.flag_domain)
        self.label_id_veh_name.setText(f"{self.txt_domain}")
        self.label_id_veh_name.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_ecu_serial.setEnabled(self.flag_domain)
        self.label_id_ecu_serial.setText(f"{self.txt_domain}")
        self.label_id_ecu_serial.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_hw_ver.setEnabled(self.flag_domain)
        self.label_id_hw_ver.setText(f"{self.txt_domain}")
        self.label_id_hw_ver.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_sw_ver.setEnabled(self.flag_domain)
        self.label_id_sw_ver.setText(f"{self.txt_domain}")
        self.label_id_sw_ver.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_ecu_manu_date.setEnabled(flag)
        self.label_id_ecu_manu_date.setText(f"{txt}")
        self.label_id_ecu_manu_date.setStyleSheet(f"color: {color}")
        self.btn_id_assy_num.setEnabled(self.flag_domain)
        self.label_id_assy_num.setText(f"{self.txt_domain}")
        self.label_id_assy_num.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_net_config.setEnabled(self.flag_domain)
        self.label_id_net_config.setText(f"{self.txt_domain}")
        self.label_id_net_config.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_ecu_sts_info.setEnabled(self.flag_domain)
        self.label_id_ecu_sts_info.setText(f"{self.txt_domain}")
        self.label_id_ecu_sts_info.setStyleSheet(f"color: {self.color_domain}")

        self.btn_id_nrc_13.setEnabled(flag)
        self.label_id_nrc_13.setText(f"{txt}")
        self.label_id_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_id_nrc_31.setEnabled(flag)
        self.label_id_nrc_31.setText(f"{txt}")
        self.label_id_nrc_31.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_did.setEnabled(flag)
        self.chkbox_diag_test_mode_did.setEnabled(flag)

    def set_diag_sec_btns_labels(self, flag=True):
        if self.chkbox_diag_test_mode_sec.isChecked():
            color = "black"
            txt = "Not tested"
        else:
            color = "gray"
            txt = "Default"

        self.btn_sec_req_seed.setEnabled(flag)
        self.label_sec_req_seed.setText(f"{txt}")
        self.label_sec_req_seed.setStyleSheet(f"color: {color}")
        self.btn_sec_send_key.setEnabled(flag)
        self.label_sec_send_key.setText(f"{txt}")
        self.label_sec_send_key.setStyleSheet(f"color: {color}")
        self.btn_sec_seed_plus_send.setEnabled(flag)
        self.label_sec_seed_plus_send.setText(f"{txt}")
        self.label_sec_seed_plus_send.setStyleSheet(f"color: {color}")

        self.btn_sec_nrc_12.setEnabled(flag)
        self.label_sec_nrc_12.setText(f"{txt}")
        self.label_sec_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_13.setEnabled(flag)
        self.label_sec_nrc_13.setText(f"{txt}")
        self.label_sec_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_24.setEnabled(flag)
        self.label_sec_nrc_24.setText(f"{txt}")
        self.label_sec_nrc_24.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_35.setEnabled(flag)
        self.label_sec_nrc_35.setText(f"{txt}")
        self.label_sec_nrc_35.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_36.setEnabled(flag)
        self.label_sec_nrc_36.setText(f"{txt}")
        self.label_sec_nrc_36.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_37.setEnabled(flag)
        self.label_sec_nrc_37.setText(f"{txt}")
        self.label_sec_nrc_37.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_7f_req.setEnabled(flag)
        self.label_sec_nrc_7f_req.setText(f"{txt}")
        self.label_sec_nrc_7f_req.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_7f_send.setEnabled(flag)
        self.label_sec_nrc_7f_send.setText(f"{txt}")
        self.label_sec_nrc_7f_send.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_sec.setEnabled(flag)
        self.chkbox_diag_test_mode_sec.setEnabled(flag)

    def set_diag_write_btns_labels(self, flag=True):
        if self.chkbox_diag_test_mode_write.isChecked():
            color = 'black'
            txt = "Not tested"
        else:
            color = 'gray'
            txt = "Default"

        if self.sender():
            if self.sender().objectName() == "btn_bus_start" or self.sender().objectName() == "chkbox_diag_console":
                self.label_write.setStyleSheet(f"color: black")
                self.label_flag_send.setStyleSheet(f"color: black")
            elif self.sender().objectName() == "btn_bus_stop":
                self.label_write.setStyleSheet(f"color: gray")
                self.label_flag_send.setStyleSheet(f"color: gray")
                self.lineEdit_write_data.setText('')

        self.lineEdit_write_data.setEnabled(flag)
        self.btn_write_data_clear.setEnabled(flag)
        self.btn_write_data_send.setEnabled(flag)

        self.btn_write_vin.setEnabled(flag)
        self.btn_write_vin_init.setEnabled(flag)
        self.label_write_vin.setText(f"{txt}")
        self.label_write_vin.setStyleSheet(f"color: {color}")
        self.btn_write_install_date.setEnabled(flag)
        self.label_write_install_date.setText(f"{txt}")
        self.label_write_install_date.setStyleSheet(f"color: {color}")
        self.btn_write_veh_name.setEnabled(flag)
        self.label_write_veh_name.setText(f"{txt}")
        self.label_write_veh_name.setStyleSheet(f"color: {color}")
        self.btn_write_sys_name.setEnabled(flag)
        self.label_write_sys_name.setText(f"{txt}")
        self.label_write_sys_name.setStyleSheet(f"color: {color}")
        self.btn_write_net_config.setEnabled(flag)
        self.label_write_net_config.setText(f"{txt}")
        self.label_write_net_config.setStyleSheet(f"color: {color}")

        self.btn_write_nrc_7f_vin.setEnabled(flag)
        self.label_write_nrc_7f_vin.setText(f"{txt}")
        self.label_write_nrc_7f_vin.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_7f_install_date.setEnabled(flag)
        self.label_write_nrc_7f_install_date.setText(f"{txt}")
        self.label_write_nrc_7f_install_date.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_7f_veh_name.setEnabled(flag)
        self.label_write_nrc_7f_veh_name.setText(f"{txt}")
        self.label_write_nrc_7f_veh_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_7f_sys_name.setEnabled(flag)
        self.label_write_nrc_7f_sys_name.setText(f"{txt}")
        self.label_write_nrc_7f_sys_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_7f_net_config.setEnabled(flag)
        self.label_write_nrc_7f_net_config.setText(f"{txt}")
        self.label_write_nrc_7f_net_config.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_vin.setEnabled(flag)
        self.label_write_nrc_33_vin.setText(f"{txt}")
        self.label_write_nrc_33_vin.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_install_date.setEnabled(flag)
        self.label_write_nrc_33_install_date.setText(f"{txt}")
        self.label_write_nrc_33_install_date.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_veh_name.setEnabled(flag)
        self.label_write_nrc_33_veh_name.setText(f"{txt}")
        self.label_write_nrc_33_veh_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_sys_name.setEnabled(flag)
        self.label_write_nrc_33_sys_name.setText(f"{txt}")
        self.label_write_nrc_33_sys_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_net_config.setEnabled(flag)
        self.label_write_nrc_33_net_config.setText(f"{txt}")
        self.label_write_nrc_33_net_config.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_vin.setEnabled(flag)
        self.label_write_nrc_22_vin.setText(f"{txt}")
        self.label_write_nrc_22_vin.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_install_date.setEnabled(flag)
        self.label_write_nrc_22_install_date.setText(f"{txt}")
        self.label_write_nrc_22_install_date.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_veh_name.setEnabled(flag)
        self.label_write_nrc_22_veh_name.setText(f"{txt}")
        self.label_write_nrc_22_veh_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_sys_name.setEnabled(flag)
        self.label_write_nrc_22_sys_name.setText(f"{txt}")
        self.label_write_nrc_22_sys_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_net_config.setEnabled(flag)
        self.label_write_nrc_22_net_config.setText(f"{txt}")
        self.label_write_nrc_22_net_config.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_13.setEnabled(flag)
        self.label_write_nrc_13.setText(f"{txt}")
        self.label_write_nrc_13.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_write.setEnabled(flag)
        self.chkbox_diag_test_mode_write.setEnabled(flag)

    def set_diag_comm_cont_btns_labels(self, flag=True):
        if self.chkbox_diag_test_mode_comm_cont.isChecked():
            self.chkbox_diag_compression_bit_comm_cont.setEnabled(True)
            self.chkbox_diag_functional_domain_comm_cont.setEnabled(True)
            color = 'black'
            txt = "Not tested"
            if self.chkbox_diag_functional_domain_comm_cont.isChecked():
                self.diag_tester_id = 0x18db33f1
            else:
                self.diag_tester_id = 0x18da41f1
        else:
            if self.chkbox_diag_compression_bit_comm_cont.isChecked():
                self.diag_tester_id = 0x18da41f1
                self.chkbox_diag_compression_bit_comm_cont.toggle()
            self.chkbox_diag_compression_bit_comm_cont.setEnabled(False)
            if self.chkbox_diag_functional_domain_comm_cont.isChecked():
                self.chkbox_diag_functional_domain_comm_cont.toggle()
            self.chkbox_diag_functional_domain_comm_cont.setEnabled(False)
            color = 'gray'
            txt = "Default"

        self.btn_comm_cont_all_en.setEnabled(flag)
        self.label_comm_cont_all_en.setText(f"{txt}")
        self.label_comm_cont_all_en.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_tx_dis.setEnabled(flag)
        self.label_comm_cont_tx_dis.setText(f"{txt}")
        self.label_comm_cont_tx_dis.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_all_dis.setEnabled(flag)
        self.label_comm_cont_all_dis.setText(f"{txt}")
        self.label_comm_cont_all_dis.setStyleSheet(f"color: {color}")

        self.btn_comm_cont_nrc_12.setEnabled(flag)
        self.label_comm_cont_nrc_12.setText(f"{txt}")
        self.label_comm_cont_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_13.setEnabled(flag)
        self.label_comm_cont_nrc_13.setText(f"{txt}")
        self.label_comm_cont_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_31.setEnabled(flag)
        self.label_comm_cont_nrc_31.setText(f"{txt}")
        self.label_comm_cont_nrc_31.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_7f_all_en.setEnabled(flag)
        self.label_comm_cont_nrc_7f_all_en.setText(f"{txt}")
        self.label_comm_cont_nrc_7f_all_en.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_7f_tx_dis.setEnabled(flag)
        self.label_comm_cont_nrc_7f_tx_dis.setText(f"{txt}")
        self.label_comm_cont_nrc_7f_tx_dis.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_7f_all_dis.setEnabled(flag)
        self.label_comm_cont_nrc_7f_all_dis.setText(f"{txt}")
        self.label_comm_cont_nrc_7f_all_dis.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_22_all_en.setEnabled(flag)
        self.label_comm_cont_nrc_22_all_en.setText(f"{txt}")
        self.label_comm_cont_nrc_22_all_en.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_22_tx_dis.setEnabled(flag)
        self.label_comm_cont_nrc_22_tx_dis.setText(f"{txt}")
        self.label_comm_cont_nrc_22_tx_dis.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_22_all_dis.setEnabled(flag)
        self.label_comm_cont_nrc_22_all_dis.setText(f"{txt}")
        self.label_comm_cont_nrc_22_all_dis.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_comm_cont.setEnabled(flag)
        self.chkbox_diag_test_mode_comm_cont.setEnabled(flag)

    def set_diag_mem_fault_btns_labels(self, flag=True):
        if self.chkbox_diag_test_mode_mem_fault.isChecked():
            color = 'black'
            txt = "Not tested"
        else:
            color = 'gray'
            txt = "Default"
        self.btn_diag_reset_mem_fault.setEnabled(flag)
        self.chkbox_diag_test_mode_mem_fault.setEnabled(flag)
        self.chkbox_diag_functional_domain_mem_fault.setEnabled(flag)
        self.treeWidget_dtc.setEnabled(flag)
        self.btn_diag_dtc_console_clear.setEnabled(flag)
        self.btn_mem_fault_num_check.setEnabled(flag)
        self.btn_mem_fault_list_check.setEnabled(flag)
        self.btn_mem_fault_reset.setEnabled(flag)
        self.btn_mem_fault_avail_sts_mask.setEnabled(flag)
        if self.sender():
            if self.sender().objectName() == "btn_bus_start" or self.sender().objectName() == "chkbox_diag_console":
                self.label_mem_fault_dtc_num.setStyleSheet(f"color: black")
            elif self.sender().objectName() == "btn_bus_stop":
                self.label_mem_fault_dtc_num.setStyleSheet(f"color: gray")

            if self.chkbox_diag_test_mode_mem_fault.isChecked():
                self.chkbox_diag_functional_domain_mem_fault.setEnabled(True)
                self.btn_mem_fault_num_check.setEnabled(not flag)
                self.btn_mem_fault_list_check.setEnabled(not flag)
                self.btn_mem_fault_reset.setEnabled(not flag)
                self.btn_mem_fault_avail_sts_mask.setEnabled(not flag)
                if self.chkbox_diag_functional_domain_mem_fault.isChecked():
                    self.diag_tester_id = 0x18db33f1
                else:
                    self.diag_tester_id = 0x18da41f1
            else:
                if self.chkbox_diag_functional_domain_mem_fault.isChecked():
                    self.diag_tester_id = 0x18da41f1
                    self.chkbox_diag_functional_domain_mem_fault.toggle()
                self.chkbox_diag_functional_domain_mem_fault.setEnabled(False)
        self.btn_mem_fault_nrc_12.setEnabled(flag)
        self.label_mem_fault_nrc_12.setText(f"{txt}")
        self.label_mem_fault_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_mem_fault_nrc_13.setEnabled(flag)
        self.label_mem_fault_nrc_13.setText(f"{txt}")
        self.label_mem_fault_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_mem_fault_nrc_13_reset.setEnabled(flag)
        self.label_mem_fault_nrc_13_reset.setText(f"{txt}")
        self.label_mem_fault_nrc_13_reset.setStyleSheet(f"color: {color}")
        self.btn_mem_fault_nrc_22_reset.setEnabled(flag)
        self.label_mem_fault_nrc_22_reset.setText(f"{txt}")
        self.label_mem_fault_nrc_22_reset.setStyleSheet(f"color: {color}")
        self.btn_mem_fault_nrc_31_reset.setEnabled(flag)
        self.label_mem_fault_nrc_31_reset.setText(f"{txt}")
        self.label_mem_fault_nrc_31_reset.setStyleSheet(f"color: {color}")

    def set_diag_dtc_cont_btns_labels(self, flag=True):
        if self.chkbox_diag_test_mode_dtc_cont.isChecked():
            self.chkbox_diag_compression_bit_dtc_cont.setEnabled(True)
            self.chkbox_diag_functional_domain_dtc_cont.setEnabled(True)
            color = 'black'
            txt = "Not tested"
            if self.chkbox_diag_functional_domain_dtc_cont.isChecked():
                self.diag_tester_id = 0x18db33f1
            else:
                self.diag_tester_id = 0x18da41f1
        else:
            if self.chkbox_diag_compression_bit_dtc_cont.isChecked():
                self.diag_tester_id = 0x18da41f1
                self.chkbox_diag_compression_bit_dtc_cont.toggle()
            self.chkbox_diag_compression_bit_dtc_cont.setEnabled(False)
            if self.chkbox_diag_functional_domain_dtc_cont.isChecked():
                self.chkbox_diag_functional_domain_dtc_cont.toggle()
            self.chkbox_diag_functional_domain_dtc_cont.setEnabled(False)
            color = 'gray'
            txt = "Default"

        self.btn_dtc_cont_en.setEnabled(flag)
        self.label_dtc_cont_en.setText(f"{txt}")
        self.label_dtc_cont_en.setStyleSheet(f"color: {color}")
        self.btn_dtc_cont_dis.setEnabled(flag)
        self.label_dtc_cont_dis.setText(f"{txt}")
        self.label_dtc_cont_dis.setStyleSheet(f"color: {color}")
        self.btn_dtc_cont_nrc_12.setEnabled(flag)
        self.label_dtc_cont_nrc_12.setText(f"{txt}")
        self.label_dtc_cont_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_dtc_cont_nrc_13.setEnabled(flag)
        self.label_dtc_cont_nrc_13.setText(f"{txt}")
        self.label_dtc_cont_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_dtc_cont_nrc_7f_en.setEnabled(flag)
        self.label_dtc_cont_nrc_7f_en.setText(f"{txt}")
        self.label_dtc_cont_nrc_7f_en.setStyleSheet(f"color: {color}")
        self.btn_dtc_cont_nrc_7f_dis.setEnabled(flag)
        self.label_dtc_cont_nrc_7f_dis.setText(f"{txt}")
        self.label_dtc_cont_nrc_7f_dis.setStyleSheet(f"color: {color}")
        self.btn_dtc_cont_nrc_22_en.setEnabled(flag)
        self.label_dtc_cont_nrc_22_en.setText(f"{txt}")
        self.label_dtc_cont_nrc_22_en.setStyleSheet(f"color: {color}")
        self.btn_dtc_cont_nrc_22_dis.setEnabled(flag)
        self.label_dtc_cont_nrc_22_dis.setText(f"{txt}")
        self.label_dtc_cont_nrc_22_dis.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_dtc_cont.setEnabled(flag)
        self.chkbox_diag_test_mode_dtc_cont.setEnabled(flag)

    def diag_initialization(self):
        self.flow_control_len = 1
        self.res_data = []
        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.write_data = [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA]
        self.raw_data = []
        self.lineEdit_write_data.clear()
        self.lineEdit_id_data.clear()
        self.treeWidget_dtc.clear()
        self.dtc_num = 0
        self.label_mem_fault_dtc_num.setText('Number of DTCs : -')

    @pyqtSlot(list)
    def diag_data_collector(self, mess, multi=False, comp=False):
        for i, mess_data in zip(range(len(mess)), mess):
            self.data[i] = mess_data
        self.main_obj.send_message('c', self.diag_tester_id, self.data, 0)
        time.sleep(0.030)
        if multi:
            self.data[0] = 0x30
            self.main_obj.send_message('c', self.diag_tester_id, self.data, 0)
        time.sleep(0.300)
        self.res_data = self.main_obj.thread_worker.reservoir[:]
        self.main_obj.thread_worker.reservoir = []
        if comp:
            return False
        if len(self.res_data) < self.flow_control_len:
            QMessageBox.warning(self, "Not sufficient length", "Try to send diag signal once more")
            return False
        else:
            temp_li = []
            if len(self.res_data) == 1:
                if self.data_len > 0:
                    self.raw_data += self.res_data[0].data[1:8]
            elif len(self.res_data) > 1:
                for i in range(self.flow_control_len):
                    for j in range(self.flow_control_len):
                        flow_seq = self.res_data[j].data[0] % 0x10
                        if i == flow_seq:
                            if self.res_data[j].data[0] == 0x10:
                                self.data_len = self.res_data[j].data[1]
                                st = 2
                            else:
                                st = 1
                            for k in range(st, 8):
                                self.raw_data.append(self.res_data[j].data[k])
                                if len(self.raw_data) == self.data_len:
                                    break
                            temp_li.append(self.res_data[j])
                            break
                self.res_data = temp_li
            for m in self.res_data:
                self.diag_console.appendPlainText(str(m))
                QtCore.QCoreApplication.processEvents()
        return True

    def data_converter(self, conv):
        if conv == 'a2c':
            entire_ch = ''
            for ch in self.raw_data[3:]:
                entire_ch += chr(ch)
            return entire_ch
        elif conv == 'c2a':
            txt_len = len(self.write_txt)
            if txt_len > 0:
                while self.write_txt[0] == ' ' or self.write_txt[txt_len - 1] == ' ':
                    if self.write_txt[0] == ' ':
                        self.write_txt = self.write_txt[1:]
                    if self.write_txt[txt_len - 1] == ' ':
                        self.write_txt = self.write_txt[:txt_len - 1]
                ascii_li = []
                for i, ch in zip(range(txt_len), self.write_txt):
                    # LMPA1KMB7NC002090
                    ascii_li.append(int(hex(ord(ch))[2:], 16))
                self.write_txt = ascii_li[:]
        elif conv == 'bcd':
            bcd_li = []
            for i in range(0, len(self.write_txt), 2):
                try:
                    bcd_li.append(int(self.write_txt[i:i+2]))
                except ValueError:
                    return False
            self.write_txt = bcd_li[:]
        elif conv == 'hex':
            self.write_txt = self.write_txt.split(' ')
            for i in range(len(self.write_txt)):
                try:
                    self.write_txt[i] = int(self.write_txt[i], 16)
                except ValueError:
                    return False
        return True

    def write_data_sender(self):
        self.write_txt = self.lineEdit_write_data.text()
        self.label_flag_send.setText(f'Sended data : {self.write_txt}, length: {len(self.write_txt)}')

    def write_data_not_correct(self, txt):
        if txt == "btn_write_vin":
            err = "Length Error"
            message = "Incorrect length of VIN number \n (Need to 17 Character)"
        elif txt == "btn_write_install_date":
            err = "Data Format or Length Error"
            message = "Incorrect data \n (Data should be number and 'yyyymmdd' format)"
        elif txt == "btn_write_veh_name":
            err = "Length Error"
            message = "Incorrect length of Vehicle name \n (Need to 8 Character)"
        elif txt == "btn_write_sys_name":
            err = "Length Error"
            message = "Incorrect length of System name \n (Need to 8 Character)"
        elif txt == "btn_write_net_config":
            err = "Data Format or Length Error"
            message = "Incorrect length of Network Configuration \n (Data should be hex number and 'nn nn nn nn nn nn nn nn' format)"
        QMessageBox.warning(self, err, message)
        self.main_obj.console_text_clear(err)

    def diag_func(self):
        if self.c_can_bus:
            if self.sender():
                self.diag_btn_text = self.sender().objectName()
                if self.diag_btn_text == "btn_sess_default" or self.diag_btn_text == "btn_sess_extended" \
                        or self.diag_btn_text == "btn_sess_nrc_12" or self.diag_btn_text == "btn_sess_nrc_13":
                    self.diag_success_byte = 0x50
                    self.diag_sess(self.diag_btn_text)
                elif self.diag_btn_text == "btn_reset_sw" or self.diag_btn_text == "btn_reset_hw" \
                        or self.diag_btn_text == "btn_reset_nrc_12" or self.diag_btn_text == "btn_reset_nrc_13" \
                        or self.diag_btn_text == "btn_reset_nrc_7f_sw" or self.diag_btn_text == "btn_reset_nrc_7f_hw" \
                        or self.diag_btn_text == "btn_reset_nrc_22_sw" or self.diag_btn_text == "btn_reset_nrc_22_hw":
                    self.diag_success_byte = 0x51
                    self.diag_reset(self.diag_btn_text)
                elif self.diag_btn_text == "btn_tester" \
                        or self.diag_btn_text == "btn_tester_nrc_12" or self.diag_btn_text == "btn_tester_nrc_13":
                    self.diag_success_byte = 0x7e
                    self.diag_tester(self.diag_btn_text)
                elif self.diag_btn_text == "btn_id_ecu_num" or self.diag_btn_text == "btn_id_ecu_supp" \
                        or "btn_id_vin" == self.diag_btn_text or self.diag_btn_text == "btn_id_install_date" \
                        or self.diag_btn_text == "btn_id_diag_ver" or self.diag_btn_text == "btn_id_sys_name" \
                        or self.diag_btn_text == "btn_id_active_sess" or self.diag_btn_text == "btn_id_veh_name" \
                        or self.diag_btn_text == "btn_id_ecu_serial" or self.diag_btn_text == "btn_id_hw_ver" \
                        or self.diag_btn_text == "btn_id_sw_ver" or self.diag_btn_text == "btn_id_ecu_manu_date" \
                        or self.diag_btn_text == "btn_id_assy_num" or self.diag_btn_text == "btn_id_net_config" \
                        or self.diag_btn_text == "btn_id_ecu_sts_info" \
                        or self.diag_btn_text == "btn_id_nrc_13" or self.diag_btn_text == "btn_id_nrc_31":
                    self.diag_success_byte = 0x62
                    self.diag_did(self.diag_btn_text)
                elif self.diag_btn_text == "btn_sec_req_seed" or self.diag_btn_text == "btn_sec_send_key" \
                        or self.diag_btn_text == "btn_sec_seed_plus_send" or self.diag_btn_text == "btn_sec_nrc_12" \
                        or self.diag_btn_text == "btn_sec_nrc_13" or self.diag_btn_text == "btn_sec_nrc_24" \
                        or self.diag_btn_text == "btn_sec_nrc_35" or self.diag_btn_text == "btn_sec_nrc_36" \
                        or self.diag_btn_text == "btn_sec_nrc_37" \
                        or self.diag_btn_text == "btn_sec_nrc_7f_req" or self.diag_btn_text == "btn_sec_nrc_7f_send":
                    self.diag_success_byte = 0x67
                    self.diag_security_access(self.diag_btn_text)
                elif self.diag_btn_text == "btn_write_vin" or self.diag_btn_text == "btn_write_install_date" \
                        or self.diag_btn_text == "btn_write_veh_name" or self.diag_btn_text == "btn_write_sys_name" \
                        or self.diag_btn_text == "btn_write_net_config" or self.diag_btn_text == "btn_write_nrc_7f_vin" \
                        or self.diag_btn_text == "btn_write_nrc_7f_install_date" or self.diag_btn_text == "btn_write_nrc_7f_veh_name" \
                        or self.diag_btn_text == "btn_write_nrc_7f_sys_name" or self.diag_btn_text == "btn_write_nrc_7f_net_config" \
                        or self.diag_btn_text == "btn_write_nrc_33_vin" or self.diag_btn_text == "btn_write_nrc_33_install_date" \
                        or self.diag_btn_text == "btn_write_nrc_33_veh_name" or self.diag_btn_text == "btn_write_nrc_33_sys_name" \
                        or self.diag_btn_text == "btn_write_nrc_33_net_config" or self.diag_btn_text == "btn_write_nrc_22_vin" \
                        or self.diag_btn_text == "btn_write_nrc_22_install_date" or self.diag_btn_text == "btn_write_nrc_22_veh_name" \
                        or self.diag_btn_text == "btn_write_nrc_22_sys_name" or self.diag_btn_text == "btn_write_nrc_22_net_config" \
                        or self.diag_btn_text == "btn_write_nrc_13" or self.diag_btn_text == "btn_write_vin_init":
                    self.diag_success_byte = 0x6e
                    self.diag_write(self.diag_btn_text)
                elif self.diag_btn_text == 'btn_comm_cont_all_en' or self.diag_btn_text == 'btn_comm_cont_tx_dis' \
                        or self.diag_btn_text == 'btn_comm_cont_all_dis' or self.diag_btn_text == 'btn_comm_cont_nrc_12' \
                        or self.diag_btn_text == 'btn_comm_cont_nrc_13' or self.diag_btn_text == 'btn_comm_cont_nrc_31' \
                        or self.diag_btn_text == 'btn_comm_cont_nrc_22_all_en' or self.diag_btn_text == 'btn_comm_cont_nrc_22_tx_dis' \
                        or self.diag_btn_text == 'btn_comm_cont_nrc_22_all_dis' or self.diag_btn_text == 'btn_comm_cont_nrc_7f_all_en' \
                        or self.diag_btn_text == 'btn_comm_cont_nrc_7f_tx_dis' or self.diag_btn_text ==  'btn_comm_cont_nrc_7f_all_dis':
                    self.diag_success_byte = 0x68
                    self.diag_comm_cont(self.diag_btn_text)
                elif self.diag_btn_text == "btn_mem_fault_num_check" \
                        or self.diag_btn_text == "btn_mem_fault_list_check" or self.diag_btn_text == "btn_mem_fault_avail_sts_mask"\
                        or self.diag_btn_text == 'btn_mem_fault_nrc_12' or self.diag_btn_text == 'btn_mem_fault_nrc_13':
                    self.diag_success_byte = 0x59
                    self.diag_memory_fault(self.diag_btn_text)
                elif self.diag_btn_text == "btn_mem_fault_reset" or self.diag_btn_text == 'btn_mem_fault_nrc_13_reset' \
                        or self.diag_btn_text == 'btn_mem_fault_nrc_22_reset' or self.diag_btn_text == 'btn_mem_fault_nrc_31_reset':
                    self.diag_success_byte = 0x54
                    self.diag_memory_fault(self.diag_btn_text)
                elif self.diag_btn_text == 'btn_dtc_cont_en' or self.diag_btn_text == 'btn_dtc_cont_dis' \
                        or self.diag_btn_text == 'btn_dtc_cont_nrc_12' or self.diag_btn_text == 'btn_dtc_cont_nrc_13' \
                        or self.diag_btn_text == 'btn_dtc_cont_nrc_22_en' or self.diag_btn_text == 'btn_dtc_cont_nrc_22_dis' \
                        or self.diag_btn_text == 'btn_dtc_cont_nrc_7f_en' or self.diag_btn_text == 'btn_dtc_cont_nrc_7f_dis':
                    self.diag_success_byte = 0xC5
                    self.diag_dtc_cont(self.diag_btn_text)
        else:
            QMessageBox.warning(self, "C-CAN bus error", "C-CAN bus is not properly connected")

    def diag_sess(self, txt, ex_comp_data=False, ex_comp_sig=False):
        # **need to add test failed scenario
        self.diag_initialization()
        if txt == "btn_sess_default":
            sig_li = [0x02, 0x10, 0x01]
        elif txt == "btn_sess_extended":
            sig_li = [0x02, 0x10, 0x03]
        elif txt == "btn_sess_nrc_12":
            sig_li = [0x02, 0x10, 0x04]
        elif txt == "btn_sess_nrc_13":
            sig_li = [0x03, 0x10, 0x01, 0x01]
        if self.chkbox_diag_compression_bit_basic.isChecked() or ex_comp_sig:
            sig_li[2] = sig_gen.binary_sig(sig_li[2], 0, 1, 1)

        if self.chkbox_diag_test_mode_basic.isChecked() and self.sender().objectName()[4:8] == "sess":
            if self.chkbox_diag_compression_bit_basic.isChecked() and (txt == "btn_sess_default" or txt == "btn_sess_extended"):
                self.diag_data_collector(sig_li, comp=True)
                self.diag_did("btn_id_active_sess")
                if self.raw_data[3] == (sig_li[2] % 0x80):
                    if txt == "btn_sess_default":
                        self.btn_sess_default.setEnabled(False)
                        self.label_sess_default.setText("Success")
                    elif txt == "btn_sess_extended":
                        self.btn_sess_extended.setEnabled(False)
                        self.label_sess_extended.setText("Success")
            else:
                self.diag_data_collector(sig_li)
                tx_result = self.res_data[0].data[:4]
                if tx_result[1] == self.diag_success_byte:
                    if tx_result[2] == 0x01:
                        self.btn_sess_default.setEnabled(False)
                        self.label_sess_default.setText("Success")
                    elif tx_result[2] == 0x03:
                        self.btn_sess_extended.setEnabled(False)
                        self.label_sess_extended.setText("Success")
                else:
                    if tx_result[3] == 0x12:
                        self.btn_sess_nrc_12.setEnabled(False)
                        self.label_sess_nrc_12.setText("Success")
                    elif tx_result[3] == 0x13:
                        self.btn_sess_nrc_13.setEnabled(False)
                        self.label_sess_nrc_13.setText("Success")
        else:
            self.diag_data_collector(sig_li, comp=ex_comp_data)

    def diag_reset(self, txt):
        if self.chkbox_diag_compression_bit_basic.isChecked():
            ex_comp_data = True
        else:
            ex_comp_data = False
        self.diag_initialization()
        if txt == "btn_reset_sw":
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data)
            sig_li = [0x02, 0x11, 0x01]
        elif txt == "btn_reset_hw":
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data)
            sig_li = [0x02, 0x11, 0x03]
        elif txt == "btn_reset_nrc_12":
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data)
            sig_li = [0x02, 0x11, 0x07]
        elif txt == "btn_reset_nrc_13":
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data)
            sig_li = [0x03, 0x11, 0x01, 0x01]
        elif txt == "btn_reset_nrc_7f_sw":
            self.diag_sess("btn_sess_default", ex_comp_data=ex_comp_data)
            sig_li = [0x02, 0x11, 0x01]
        elif txt == "btn_reset_nrc_7f_hw":
            self.diag_sess("btn_sess_default", ex_comp_data=ex_comp_data)
            sig_li = [0x02, 0x11, 0x03]
        elif txt == "btn_reset_nrc_22_sw":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data)
            sig_li = [0x02, 0x11, 0x01]
        elif txt == "btn_reset_nrc_22_hw":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data)
            sig_li = [0x02, 0x11, 0x03]
        if self.chkbox_diag_compression_bit_basic.isChecked():
            sig_li[2] = sig_gen.binary_sig(sig_li[2], 0, 1, 1)

        if self.chkbox_diag_test_mode_basic.isChecked():
            if self.chkbox_diag_compression_bit_basic.isChecked() and (txt == "btn_reset_sw" or txt == "btn_reset_hw"):
                self.diag_data_collector(sig_li, comp=True)
                if txt == "btn_reset_sw":
                    self.label_reset_sw.setText("Check S/W reset\nis executed")
                elif txt == "btn_reset_hw":
                    self.label_reset_hw.setText("Check H/W reset\nis executed")
            else:
                self.diag_data_collector(sig_li)
                tx_result = self.res_data[0].data[:4]
                if tx_result[1] == self.diag_success_byte:
                    if tx_result[2] == 0x01:
                        self.label_reset_sw.setText("Check S/W\nreset is executed")
                    elif tx_result[2] == 0x03:
                        self.label_reset_hw.setText("Check H/W\nreset is executed")
                else:
                    if tx_result[3] == 0x12:
                        self.btn_reset_nrc_12.setEnabled(False)
                        self.label_reset_nrc_12.setText("Success")
                    elif tx_result[3] == 0x13:
                        self.btn_reset_nrc_13.setEnabled(False)
                        self.label_reset_nrc_13.setText("Success")
                    elif txt == "btn_reset_nrc_7f_sw" or txt == "btn_reset_nrc_22_sw":
                        if tx_result[3] == 0x7f:
                            self.btn_reset_nrc_7f_sw.setEnabled(False)
                            self.label_reset_nrc_7f_sw.setText("Success")
                        elif tx_result[3] == 0x22:
                            self.btn_reset_nrc_22_sw.setEnabled(False)
                            self.label_reset_nrc_22_sw.setText("Success")
                    elif txt == "btn_reset_nrc_7f_hw" or txt == "btn_reset_nrc_22_hw":
                        if tx_result[3] == 0x7f:
                            self.btn_reset_nrc_7f_hw.setEnabled(False)
                            self.label_reset_nrc_7f_hw.setText("Success")
                        elif tx_result[3] == 0x22:
                            self.btn_reset_nrc_22_hw.setEnabled(False)
                            self.label_reset_nrc_22_hw.setText("Success")
        else:
            self.diag_data_collector(sig_li)

        self.main_obj.drv_state = False
        self.main_obj.set_drv_state()
        self.main_obj.thread_worker.slider_speed_func(0)

    def diag_tester(self, txt):
        # **need to add test failed scenario
        self.diag_initialization()
        if txt == "btn_tester":
            sig_li = [0x02, 0x3E, 0x00]
        elif txt == "btn_tester_nrc_12":
            sig_li = [0x02, 0x3E, 0x03]
        elif txt == "btn_tester_nrc_13":
            sig_li = [0x03, 0x3E, 0x00, 0x01]
        if self.chkbox_diag_compression_bit_basic.isChecked():
            sig_li[2] = sig_gen.binary_sig(sig_li[2], 0, 1, 1)

        if self.chkbox_diag_test_mode_basic.isChecked():
            if self.chkbox_diag_compression_bit_basic.isChecked() and txt == "btn_tester":
                self.diag_data_collector(sig_li, comp=True)
                time.sleep(0.1)
                self.btn_tester.setEnabled(False)
                self.label_tester.setText("Success")
            else:
                self.diag_data_collector(sig_li)
                tx_result = self.res_data[0].data[:4]
                if tx_result[1] == self.diag_success_byte:
                    if tx_result[2] == 0x00:
                        self.btn_tester.setEnabled(False)
                        self.label_tester.setText("Success")
                else:
                    if tx_result[3] == 0x12:
                        self.btn_tester_nrc_12.setEnabled(False)
                        self.label_tester_nrc_12.setText("Success")
                    elif tx_result[3] == 0x13:
                        self.btn_tester_nrc_13.setEnabled(False)
                        self.label_tester_nrc_13.setText("Success")
        else:
            self.diag_data_collector(sig_li)

    def diag_did(self, txt):
        # **need to add test failed scenario
        self.diag_initialization()
        if txt == "btn_id_ecu_num":
            self.flow_control_len = 4
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x87]
        elif txt == "btn_id_ecu_supp":
            self.flow_control_len = 2
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x8A]
        elif txt == "btn_id_vin":
            self.flow_control_len = 3
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x90]
        elif txt == "btn_id_install_date":
            self.data_type = "bcd_real"
            sig_li = [0x03, 0x22, 0xF1, 0xA2]
            self.data_len = 4
        elif txt == "btn_id_diag_ver":
            self.data_type = "hex"
            sig_li = [0x03, 0x22, 0xF1, 0x13]
            self.data_len = 4
        elif txt == "btn_id_sys_name":
            self.flow_control_len = 2
            self.data_type = "ascii"
            sig_li = [0x03, 0x22,  0xF1, 0x97]
        elif txt == "btn_id_active_sess":
            self.data_type = "hex"
            sig_li = [0x03, 0x22, 0xF1, 0x86]
            self.data_len = 1
        elif txt == "btn_id_veh_name":
            self.flow_control_len = 2
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x12]
        elif txt == "btn_id_ecu_serial":
            self.flow_control_len = 4
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x8C]
        elif txt == "btn_id_hw_ver":
            self.flow_control_len = 3
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x93]
        elif txt == "btn_id_sw_ver":
            self.flow_control_len = 3
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x95]
        elif txt == "btn_id_ecu_manu_date":
            self.data_type = "bcd"
            sig_li = [0x03, 0x22, 0xF1, 0x8B]
            self.data_len = 4
        elif txt == "btn_id_assy_num":
            self.flow_control_len = 3
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x8E]
        elif txt == "btn_id_net_config":
            self.flow_control_len = 2
            self.data_type = "hex"
            sig_li = [0x03, 0x22, 0xF1, 0x10]
        elif txt == "btn_id_ecu_sts_info":
            self.flow_control_len = 2
            self.data_type = "hex"
            sig_li = [0x03, 0x22, 0xF2, 0xF0]
        elif txt == "btn_id_nrc_13":
            sig_li = [0x04, 0x22, 0xF1, 0x01, 0x01]
        elif txt == "btn_id_nrc_31":
            sig_li = [0x03, 0x22, 0xFF, 0xFF]

        if self.flow_control_len > 1:
            multi = True
        else:
            multi = False
        self.diag_data_collector(sig_li, multi)

        if self.raw_data[0] == self.diag_success_byte:
            if self.data_type == "ascii":
                temp_str = self.data_converter('a2c')
            elif self.data_type == "bcd":
                temp_str = f'{str(hex(self.raw_data[3]))[2:].zfill(2)}{str(hex(self.raw_data[4]))[2:].zfill(2)}/{str(hex(self.raw_data[5]))[2:].zfill(2)}/{str(hex(self.raw_data[6]))[2:].zfill(2)}'
            elif self.data_type == "bcd_real":
                temp_str = f'{str(self.raw_data[3]).zfill(2)}{str(self.raw_data[4]).zfill(2)}/{str(self.raw_data[5]).zfill(2)}/{str(self.raw_data[6]).zfill(2)}'
            elif self.data_type == "hex":
                temp_str = ''
                for temp_ch in self.raw_data[3:]:
                    if temp_ch != 0xaa:
                        temp_str += hex(temp_ch)[2:].upper().zfill(2)
                        temp_str += ' '
            self.lineEdit_id_data.setText(temp_str)
            self.label_id_data_length.setText(f'Data Length : {len(self.raw_data)} ({len(self.raw_data) - 3} + 3)')
        if self.chkbox_diag_test_mode_did.isChecked():
            if multi:
                if self.raw_data[0] == self.diag_success_byte and self.raw_data[1] == sig_li[2] and self.raw_data[2] == sig_li[3]:
                    if txt == "btn_id_ecu_num":
                        self.btn_id_ecu_num.setEnabled(False)
                        self.label_id_ecu_num.setText("Success")
                    elif txt == "btn_id_ecu_supp":
                        self.btn_id_ecu_supp.setEnabled(False)
                        self.label_id_ecu_supp.setText("Success")
                    elif txt == "btn_id_vin":
                        self.btn_id_vin.setEnabled(False)
                        self.label_id_vin.setText("Success")
                    elif txt == "btn_id_sys_name":
                        self.btn_id_sys_name.setEnabled(False)
                        self.label_id_sys_name.setText("Success")
                    elif txt == "btn_id_veh_name":
                        self.btn_id_veh_name.setEnabled(False)
                        self.label_id_veh_name.setText("Success")
                    elif txt == "btn_id_ecu_serial":
                        self.btn_id_ecu_serial.setEnabled(False)
                        self.label_id_ecu_serial.setText("Success")
                    elif txt == "btn_id_hw_ver":
                        self.btn_id_hw_ver.setEnabled(False)
                        self.label_id_hw_ver.setText("Success")
                    elif txt == "btn_id_sw_ver":
                        self.btn_id_sw_ver.setEnabled(False)
                        self.label_id_sw_ver.setText("Success")
                    elif txt == "btn_id_assy_num":
                        self.btn_id_assy_num.setEnabled(False)
                        self.label_id_assy_num.setText("Success")
                    elif txt == "btn_id_net_config":
                        self.btn_id_net_config.setEnabled(False)
                        self.label_id_net_config.setText("Success")
            else:
                if self.res_data[0].data[1] == self.diag_success_byte:
                    if self.res_data[0].data[2] == sig_li[2] and self.res_data[0].data[3] == sig_li[3]:
                        if txt == "btn_id_install_date":
                            self.btn_id_install_date.setEnabled(False)
                            self.label_id_install_date.setText("Success")
                        elif txt == "btn_id_diag_ver":
                            self.btn_id_diag_ver.setEnabled(False)
                            self.label_id_diag_ver.setText("Success")
                        elif txt == "btn_id_active_sess":
                            self.btn_id_active_sess.setEnabled(False)
                            self.label_id_active_sess.setText("Success")
                        elif txt == "btn_id_ecu_manu_date":
                            self.btn_id_ecu_manu_date.setEnabled(False)
                            self.label_id_ecu_manu_date.setText("Success")
                elif self.res_data[0].data[1] == self.diag_failure_byte:
                    if self.res_data[0].data[3] == 0x13:
                        self.btn_id_nrc_13.setEnabled(False)
                        self.label_id_nrc_13.setText("Success")
                    elif self.res_data[0].data[3] == 0x31:
                        self.btn_id_nrc_31.setEnabled(False)
                        self.label_id_nrc_31.setText("Success")

    def diag_security_access(self, txt, sess_init=True):
        self.diag_initialization()
        if txt == "btn_sec_req_seed":
            self.diag_sess("btn_sess_extended")
            sig_li = [0x02, 0x27, 0x01]
            self.diag_data_collector(sig_li)
            self.req_seed = self.res_data[0].data[3:7]
        elif txt == "btn_sec_send_key":
            if len(self.req_seed) == 0:
                err = "Empty Seed Key"
                message = "Get seed key first before send key"
                QMessageBox.warning(self, err, message)
                return False
            seed_converted = algo.secu_algo(self.req_seed)
            sig_li = [0x06, 0x27, 0x02]
            self.diag_data_collector(sig_li + seed_converted)
            self.req_seed = []
        elif txt == "btn_sec_seed_plus_send":
            self.diag_sess("btn_sess_default")
            time.sleep(0.100)
            self.diag_security_access("btn_sec_req_seed")
            time.sleep(0.100)
            self.diag_security_access("btn_sec_send_key")
        elif txt == "btn_sec_nrc_36":
            self.diag_sess("btn_sess_default")
            count = 0
            while count < 3:
                self.diag_security_access("btn_sec_nrc_35", sess_init=False)
                count += 1
        else:
            if txt == "btn_sec_nrc_12":
                self.diag_sess("btn_sess_extended")
                time.sleep(0.100)
                sig_li = [0x02, 0x27, 0x03]
            elif txt == "btn_sec_nrc_13":
                self.diag_sess("btn_sess_extended")
                time.sleep(0.100)
                sig_li = [0x03, 0x27, 0x01, 0x01]
            elif txt == "btn_sec_nrc_24":
                self.diag_sess("btn_sess_extended")
                time.sleep(0.100)
                sig_li = [0x02, 0x27, 0x02]
            elif txt == "btn_sec_nrc_35":
                if sess_init:
                    self.diag_sess("btn_sess_default")
                self.diag_security_access("btn_sec_req_seed")
                time.sleep(0.100)
                sig_li = [0x06, 0x27, 0x02, 0x00, 0x00, 0x00, 0x00]
            elif txt == "btn_sec_nrc_37":
                self.diag_security_access("btn_sec_nrc_36")
                sig_li = [0x02, 0x27, 0x01]
            elif txt == "btn_sec_nrc_7f_req":
                self.diag_sess("btn_sess_default")
                sig_li = [0x02, 0x27, 0x01]
            elif txt == "btn_sec_nrc_7f_send":
                self.diag_sess("btn_sess_default")
                sig_li = [0x02, 0x27, 0x02]
            self.diag_data_collector(sig_li)

            if self.chkbox_diag_test_mode_sec.isChecked():
                print(self.res_data)
            #
            #     if self.raw_data[0] == self.diag_success_byte and self.raw_data[1] == sig_li[2] and self.raw_data[
            #         2] == sig_li[3]:
            #         if txt == "btn_id_ecu_num":
            #             self.btn_id_ecu_num.setEnabled(False)
            #             self.label_id_ecu_num.setText("Success")
            #         elif txt == "btn_id_ecu_supp":
            #             self.btn_id_ecu_supp.setEnabled(False)
            #             self.label_id_ecu_supp.setText("Success")
            #         elif txt == "btn_id_vin":
            #             self.btn_id_vin.setEnabled(False)
            #             self.label_id_vin.setText("Success")
            #         elif txt == "btn_id_sys_name":
            #             self.btn_id_sys_name.setEnabled(False)
            #             self.label_id_sys_name.setText("Success")
            #         elif txt == "btn_id_veh_name":
            #             self.btn_id_veh_name.setEnabled(False)
            #             self.label_id_veh_name.setText("Success")
            #         elif txt == "btn_id_ecu_serial":
            #             self.btn_id_ecu_serial.setEnabled(False)
            #             self.label_id_ecu_serial.setText("Success")
            #         elif txt == "btn_id_hw_ver":
            #             self.btn_id_hw_ver.setEnabled(False)
            #             self.label_id_hw_ver.setText("Success")
            #         elif txt == "btn_id_sw_ver":
            #             self.btn_id_sw_ver.setEnabled(False)
            #             self.label_id_sw_ver.setText("Success")
            #         elif txt == "btn_id_assy_num":
            #             self.btn_id_assy_num.setEnabled(False)
            #             self.label_id_assy_num.setText("Success")
            #         elif txt == "btn_id_net_config":
            #             self.btn_id_net_config.setEnabled(False)
            #             self.label_id_net_config.setText("Success")
            # else:
            #     if self.res_data[0].data[1] == self.diag_success_byte:
            #         if self.res_data[0].data[2] == sig_li[2] and self.res_data[0].data[3] == sig_li[3]:
            #             if txt == "btn_id_install_date":
            #                 self.btn_id_install_date.setEnabled(False)
            #                 self.label_id_install_date.setText("Success")
            #             elif txt == "btn_id_diag_ver":
            #                 self.btn_id_diag_ver.setEnabled(False)
            #                 self.label_id_diag_ver.setText("Success")
            #             elif txt == "btn_id_active_sess":
            #                 self.btn_id_active_sess.setEnabled(False)
            #                 self.label_id_active_sess.setText("Success")
            #             elif txt == "btn_id_ecu_manu_date":
            #                 self.btn_id_ecu_manu_date.setEnabled(False)
            #                 self.label_id_ecu_manu_date.setText("Success")
            #     elif self.res_data[0].data[1] == self.diag_failure_byte:
            #         if self.res_data[0].data[3] == 0x13:
            #             self.btn_id_nrc_13.setEnabled(False)
            #             self.label_id_nrc_13.setText("Success")
            #         elif self.res_data[0].data[3] == 0x31:
            #             self.btn_id_nrc_31.setEnabled(False)
            #             self.label_id_nrc_31.setText("Success")

    def diag_write(self, txt):
        # **need to add test failed scenario
        self.diag_initialization()
        write_flag = None
        data_len = len(self.write_txt)
        if txt == "btn_write_vin":
            sig_li = [0x03, 0x2E, 0xF1, 0x90]
            if data_len == 17:
                write_flag = True
                self.data_converter('c2a')
            else:
                self.write_data_not_correct(txt)
                return 0
        elif txt == "btn_write_vin_init":
            self.write_txt = "LMPA1KMB7NC000000"
            self.diag_write("btn_write_vin")
        elif txt == "btn_write_install_date":
            if data_len != 8:
                self.write_data_not_correct(txt)
                return 0
            if self.data_converter('bcd'):
                sig_li = [0x03, 0x2E, 0xF1, 0xA2]
                write_flag = True
            else:
                self.write_data_not_correct(txt)
                return 0
        elif txt == "btn_write_veh_name":
            sig_li = [0x03, 0x2E, 0xF1, 0x12]
            if data_len == 8:
                write_flag = True
                self.data_converter('c2a')
            else:
                self.write_data_not_correct(txt)
                return 0
        elif txt == "btn_write_sys_name":
            sig_li = [0x03, 0x2E, 0xF1, 0x97]
            if data_len == 8:
                write_flag = True
                self.data_converter('c2a')
            else:
                self.write_data_not_correct(txt)
                return 0
        elif txt == "btn_write_net_config":
            if data_len != 23:
                self.write_data_not_correct(txt)
                return 0
            if self.data_converter('hex'):
                sig_li = [0x03, 0x2E, 0xF1, 0x10]
                write_flag = True
            else:
                self.write_data_not_correct(txt)
                return 0
        elif txt == "btn_write_nrc_13":
            self.diag_sess("btn_sess_extended")
            sig_li = [0x04, 0x2E, 0xF1, 0x01, 0x01]
            self.diag_data_collector(sig_li)
        elif txt == "btn_write_nrc_7f_vin":
            self.diag_sess("btn_sess_default")
            sig_li = [0x03, 0x2E, 0xF1, 0x90]
            self.diag_data_collector(sig_li)
        elif txt == "btn_write_nrc_7f_install_date":
            self.diag_sess("btn_sess_default")
            sig_li = [0x03, 0x2E, 0xF1, 0xA2]
            self.diag_data_collector(sig_li)
        elif txt == "btn_write_nrc_7f_veh_name":
            self.diag_sess("btn_sess_default")
            sig_li = [0x03, 0x2E, 0xF1, 0x12]
            self.diag_data_collector(sig_li)
        elif txt == "btn_write_nrc_7f_sys_name":
            self.diag_sess("btn_sess_default")
            sig_li = [0x03, 0x2E, 0xF1, 0x97]
            self.diag_data_collector(sig_li)
        elif txt == "btn_write_nrc_7f_net_config":
            self.diag_sess("btn_sess_default")
            sig_li = [0x03, 0x2E, 0xF1, 0x10]
            self.diag_data_collector(sig_li)
        elif txt == "btn_write_nrc_33_vin":
            self.diag_sess("btn_sess_extended")
            self.write_txt = 'abcdefghijklmnopq'
            self.write_secu_nrc = False
            self.diag_write("btn_write_vin")
        elif txt == "btn_write_nrc_33_install_date":
            self.write_txt = '12345678'
            self.write_secu_nrc = False
            self.diag_write("btn_write_install_date")
        elif txt == "btn_write_nrc_33_veh_name":
            self.write_txt = 'rstuvwxy'
            self.write_secu_nrc = False
            self.diag_write("btn_write_veh_name")
        elif txt == "btn_write_nrc_33_sys_name":
            self.write_txt = 'zabcdefg'
            self.write_secu_nrc = False
            self.diag_write("btn_write_sys_name")
        elif txt == "btn_write_nrc_33_net_config":
            self.write_txt = '01 23 45 67 89 ab cd ef'
            self.write_secu_nrc = False
            self.diag_write("btn_write_net_config")
        elif txt == "btn_write_nrc_22_vin":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = 'abcdefghijklmnopq'
            self.diag_write("btn_write_vin")
        elif txt == "btn_write_nrc_22_install_date":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = '12345678'
            self.diag_write("btn_write_install_date")
        elif txt == "btn_write_nrc_22_veh_name":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = 'rstuvwxy'
            self.diag_write("btn_write_veh_name")
        elif txt == "btn_write_nrc_22_sys_name":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = 'zabcdefg'
            self.diag_write("btn_write_veh_name")
        elif txt == "btn_write_nrc_22_net_config":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = '01 23 45 67 89 ab cd ef'
            self.diag_write("btn_write_net_config")

        data_len = len(self.write_txt)
        if write_flag:
            if self.write_secu_nrc:
                self.diag_security_access("btn_sec_seed_plus_send")
            else:
                self.diag_sess("btn_sess_default")
                self.diag_sess("btn_sess_extended")
            if self.main_obj.drv_state:
                self.main_obj.set_drv_state()
                self.main_obj.thread_worker.slider_speed_func(20)
                time.sleep(0.1)
            temp_li = []
            if len(self.write_txt) > 4:
                while True:
                    self.write_data = [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA]
                    if self.flow_control_len == 1:
                        self.write_data[0] = 0x10
                        self.write_data[1] = 3 + data_len
                        self.write_data[2] = sig_li[1]
                        self.write_data[3] = sig_li[2]
                        self.write_data[4] = sig_li[3]
                        self.write_data[5] = self.write_txt.pop(0)
                        self.write_data[6] = self.write_txt.pop(0)
                        self.write_data[7] = self.write_txt.pop(0)
                    else:
                        for j in range(8):
                            if len(self.write_txt) > 0:
                                if j == 0:
                                    self.write_data[0] = (0x20 + (self.flow_control_len - 1))
                                else:
                                    self.write_data[j] = self.write_txt.pop(0)
                    temp_li.append(self.write_data)
                    self.flow_control_len += 1
                    if len(self.write_txt) == 0:
                        break
            else:
                self.write_data[0] = 0x07
                self.write_data[1] = sig_li[1]
                self.write_data[2] = sig_li[2]
                self.write_data[3] = sig_li[3]
                self.write_data[4] = self.write_txt.pop(0)
                self.write_data[5] = self.write_txt.pop(0)
                self.write_data[6] = self.write_txt.pop(0)
                self.write_data[7] = self.write_txt.pop(0)
                temp_li.append(self.write_data)
            for w_data in temp_li:
                time.sleep(0.01)
                self.data = w_data
                self.main_obj.send_message('c', self.diag_tester_id, self.data, 0)
            time.sleep(0.3)
            reservoir = self.main_obj.thread_worker.reservoir[:]
            for qqq in reservoir:
                if qqq.arbitration_id == 0x18daf141:
                    self.res_data.append(qqq)
            self.main_obj.thread_worker.reservoir = []
            QtCore.QCoreApplication.processEvents()
            self.diag_console.appendPlainText(str(self.res_data[-1]))
        self.label_flag_send.setText(f'Fill the data')

        tx_result = self.res_data[-1].data[:4]
        if self.chkbox_diag_test_mode_write.isChecked():
            if tx_result[1] == self.diag_success_byte and tx_result[2] == sig_li[2] and tx_result[3] == sig_li[3]:
                if txt == "btn_write_vin":
                    self.btn_write_vin.setEnabled(False)
                    self.label_write_vin.setText("Success")
                elif txt == "btn_write_install_date":
                    self.btn_write_install_date.setEnabled(False)
                    self.label_write_install_date.setText("Success")
                elif txt == "btn_write_sys_name":
                    self.btn_write_sys_name.setEnabled(False)
                    self.label_write_sys_name.setText("Success")
                elif txt == "btn_write_veh_name":
                    self.btn_write_veh_name.setEnabled(False)
                    self.label_write_veh_name.setText("Success")
                elif txt == "btn_write_net_config":
                    self.btn_write_net_config.setEnabled(False)
                    self.label_write_net_config.setText("Success")
            else:
                if tx_result[3] == 0x13:
                    self.btn_write_nrc_13.setEnabled(False)
                    self.label_write_nrc_13.setText("Success")
                elif txt == "btn_write_nrc_7f_vin" or txt == "btn_write_nrc_22_vin" or txt == "btn_write_nrc_33_vin":
                    if tx_result[3] == 0x7f:
                        self.btn_write_nrc_7f_vin.setEnabled(False)
                        self.label_write_nrc_7f_vin.setText("Success")
                    elif tx_result[3] == 0x22:
                        self.btn_write_nrc_22_vin.setEnabled(False)
                        self.label_write_nrc_22_vin.setText("Success")
                    elif tx_result[3] == 0x33:
                        self.btn_write_nrc_33_vin.setEnabled(False)
                        self.label_write_nrc_33_vin.setText("Success")
                elif txt == "btn_write_nrc_7f_install_date" or txt == "btn_write_nrc_22_install_date" or txt == "btn_write_nrc_33_install_date":
                    if tx_result[3] == 0x7f:
                        self.btn_write_nrc_7f_install_date.setEnabled(False)
                        self.label_write_nrc_7f_install_date.setText("Success")
                    elif tx_result[3] == 0x22:
                        self.btn_write_nrc_22_install_date.setEnabled(False)
                        self.label_write_nrc_22_install_date.setText("Success")
                    elif tx_result[3] == 0x33:
                        self.btn_write_nrc_33_install_date.setEnabled(False)
                        self.label_write_nrc_33_install_date.setText("Success")
                elif txt == "btn_write_nrc_7f_veh_name" or txt == "btn_write_nrc_22_veh_name" or txt == "btn_write_nrc_33_veh_name":
                    if tx_result[3] == 0x7f:
                        self.btn_write_nrc_7f_veh_name.setEnabled(False)
                        self.label_write_nrc_7f_veh_name.setText("Success")
                    elif tx_result[3] == 0x22:
                        self.btn_write_nrc_22_veh_name.setEnabled(False)
                        self.label_write_nrc_22_veh_name.setText("Success")
                    elif tx_result[3] == 0x33:
                        self.btn_write_nrc_33_veh_name.setEnabled(False)
                        self.label_write_nrc_33_veh_name.setText("Success")
                elif txt == "btn_write_nrc_7f_sys_name" or txt == "btn_write_nrc_22_sys_name" or txt == "btn_write_nrc_33_sys_name":
                    if tx_result[3] == 0x7f:
                        self.btn_write_nrc_7f_sys_name.setEnabled(False)
                        self.label_write_nrc_7f_sys_name.setText("Success")
                    elif tx_result[3] == 0x22:
                        self.btn_write_nrc_22_sys_name.setEnabled(False)
                        self.label_write_nrc_22_sys_name.setText("Success")
                    elif tx_result[3] == 0x33:
                        self.btn_write_nrc_33_sys_name.setEnabled(False)
                        self.label_write_nrc_33_sys_name.setText("Success")
                elif txt == "btn_write_nrc_7f_net_config" or txt == "btn_write_nrc_22_net_config" or txt == "btn_write_nrc_33_net_config":
                    if tx_result[3] == 0x7f:
                        self.btn_write_nrc_7f_net_config.setEnabled(False)
                        self.label_write_nrc_7f_net_config.setText("Success")
                    elif tx_result[3] == 0x22:
                        self.btn_write_nrc_22_net_config.setEnabled(False)
                        self.label_write_nrc_22_net_config.setText("Success")
                    elif tx_result[3] == 0x33:
                        self.btn_write_nrc_33_net_config.setEnabled(False)
                        self.label_write_nrc_33_net_config.setText("Success")

        self.main_obj.drv_state = False
        self.main_obj.thread_worker.slider_speed_func(0)
        self.main_obj.set_drv_state()
        self.write_secu_nrc = True

    def diag_comm_cont(self, txt):
        if self.chkbox_diag_compression_bit_comm_cont.isChecked():
            ex_comp_data = True
            ex_comp_sig = True
        else:
            ex_comp_data = False
            ex_comp_sig = False
        self.diag_initialization()
        if txt == 'btn_comm_cont_all_en':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x00, 0x01]
        elif txt == 'btn_comm_cont_tx_dis':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x01, 0x01]
        elif txt == 'btn_comm_cont_all_dis':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x03, 0x01]
        elif txt == 'btn_comm_cont_nrc_12':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x0F, 0x01]
        elif txt == 'btn_comm_cont_nrc_13':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x04, 0x28, 0x00, 0x01, 0x01]
        elif txt == 'btn_comm_cont_nrc_31':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x00, 0xFF]
        elif txt == "btn_comm_cont_nrc_7f_all_en":
            self.diag_sess("btn_sess_default", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x00, 0x01]
        elif txt == "btn_comm_cont_nrc_7f_tx_dis":
            self.diag_sess("btn_sess_default", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x01, 0x01]
        elif txt == "btn_comm_cont_nrc_7f_all_dis":
            self.diag_sess("btn_sess_default", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x03, 0x01]
        elif txt == "btn_comm_cont_nrc_22_all_en":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x00, 0x01]
        elif txt == "btn_comm_cont_nrc_22_tx_dis":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x01, 0x01]
        elif txt == "btn_comm_cont_nrc_22_all_dis":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x03, 0x01]

        if self.chkbox_diag_compression_bit_comm_cont.isChecked():
            sig_li[2] = sig_gen.binary_sig(sig_li[2], 0, 1, 1)

        if self.chkbox_diag_test_mode_comm_cont.isChecked():
            if self.chkbox_diag_compression_bit_comm_cont.isChecked() and (
                    txt == "btn_comm_cont_all_en" or txt == "btn_comm_cont_tx_dis" or txt == "btn_comm_cont_all_dis"):
                self.diag_data_collector(sig_li, comp=True)
                if txt == "btn_comm_cont_all_en":
                    self.label_comm_cont_all_en.setText("Data Success \n Check the Tx/Rx availability")
                elif txt == "btn_comm_cont_tx_dis":
                    self.label_comm_cont_tx_dis.setText("Data Success \n Check the Rx availability")
                elif txt == "btn_comm_cont_all_dis":
                    self.label_comm_cont_all_dis.setText("Data Success \n Check the Rx disability")
            else:
                self.diag_data_collector(sig_li)
                tx_result = self.res_data[0].data[:4]
                if tx_result[1] == self.diag_success_byte:
                    if tx_result[2] == 0x00:
                        self.label_comm_cont_all_en.setText("Data Success \n Check the Tx/Rx availability")
                    elif tx_result[2] == 0x01:
                        self.label_comm_cont_tx_dis.setText("Data Success \n Check the Rx availability")
                    elif tx_result[2] == 0x03:
                        self.label_comm_cont_all_dis.setText("Data Success \n Check the Rx disability")
                else:
                    if tx_result[3] == 0x12:
                        self.btn_comm_cont_nrc_12.setEnabled(False)
                        self.label_comm_cont_nrc_12.setText("Success")
                    elif tx_result[3] == 0x13:
                        self.btn_comm_cont_nrc_13.setEnabled(False)
                        self.label_comm_cont_nrc_13.setText("Success")
                    elif tx_result[3] == 0x31:
                        self.btn_comm_cont_nrc_31.setEnabled(False)
                        self.label_comm_cont_nrc_31.setText("Success")
                    elif txt == "btn_comm_cont_nrc_7f_all_en" or txt == "btn_comm_cont_nrc_22_all_en":
                        if tx_result[3] == 0x7f:
                            self.btn_comm_cont_nrc_7f_all_en.setEnabled(False)
                            self.label_comm_cont_nrc_7f_all_en.setText("Success")
                        elif tx_result[3] == 0x22:
                            self.btn_comm_cont_nrc_22_all_en.setEnabled(False)
                            self.label_comm_cont_nrc_22_all_en.setText("Success")
                    elif txt == "btn_comm_cont_nrc_7f_tx_dis" or txt == "btn_comm_cont_nrc_22_tx_dis":
                        if tx_result[3] == 0x7f:
                            self.btn_comm_cont_nrc_7f_tx_dis.setEnabled(False)
                            self.label_comm_cont_nrc_7f_tx_dis.setText("Success")
                        elif tx_result[3] == 0x22:
                            self.btn_comm_cont_nrc_22_tx_dis.setEnabled(False)
                            self.label_comm_cont_nrc_22_tx_dis.setText("Success")
                    elif txt == "btn_comm_cont_nrc_7f_all_dis" or txt == "btn_comm_cont_nrc_22_all_dis":
                        if tx_result[3] == 0x7f:
                            self.btn_comm_cont_nrc_7f_all_dis.setEnabled(False)
                            self.label_comm_cont_nrc_7f_all_dis.setText("Success")
                        elif tx_result[3] == 0x22:
                            self.btn_comm_cont_nrc_22_all_dis.setEnabled(False)
                            self.label_comm_cont_nrc_22_all_dis.setText("Success")
        else:
            self.diag_data_collector(sig_li)

        self.main_obj.thread_worker.slider_speed_func(0)
        self.main_obj.drv_state = False
        self.main_obj.set_drv_state()

    def diag_memory_fault(self, txt):
        self.diag_initialization()
        if txt == "btn_mem_fault_num_check":
            sig_li = [0x03, 0x19, 0x01, 0x09]
            self.diag_data_collector(sig_li)
            self.dtc_num = self.res_data[0].data[6]
            self.label_mem_fault_dtc_num.setText(f'Number of DTCs : {self.dtc_num}')
        elif txt == "btn_mem_fault_list_check":
            self.diag_memory_fault("btn_mem_fault_num_check")
            if self.res_data[0].data[6] == 0x00:
                self.label_mem_fault_dtc_num.setText(f'Number of DTCs : 0')
                return True
            dtc_num = self.res_data[0].data[6]
            multi_flag = False
            if dtc_num > 1:
                multi_flag = True
                occu = 5
                self.flow_control_len = 2
                for i in range(dtc_num - 2):
                    for j in range(4):
                        occu += 1
                        if occu == 7:
                            self.flow_control_len += 1
                            occu = 0
            self.res_data = []
            self.raw_data = []
            sig_li = [0x03, 0x19, 0x02, 0x09]
            time.sleep(0.020)
            data_flag = self.diag_data_collector(sig_li, multi=multi_flag)
            if data_flag:
                if len(self.raw_data) == 0:
                    self.raw_data = self.res_data[0].data[1:8]
                st = 3
                for i in range(dtc_num):
                    item = [QTreeWidgetItem()]
                    single_dtc = self.raw_data[st:st+4]
                    st += 4
                    dtc_code = f'0x{hex(single_dtc[0])[2:].zfill(2)} 0x{hex(single_dtc[1])[2:].zfill(2)} 0x{hex(single_dtc[2])[2:].zfill(2)}'
                    dtc_name = data_id.dtc_identifier(single_dtc)
                    dtc_status_code = f'0x{hex(single_dtc[3])[2:].zfill(2)}'
                    if single_dtc[3] == 0x08:
                        dtc_status = f'DTC Confirmed ({dtc_status_code})'
                    elif single_dtc[3] == 0x09:
                        dtc_status = f'Test Failed ({dtc_status_code})'
                    item[0].setText(0, dtc_code)
                    item[0].setText(1, dtc_name)
                    item[0].setText(2, dtc_status)
                    self.treeWidget_dtc.addTopLevelItems(item)
        else:
            if txt == "btn_mem_fault_reset":
                sig_li = [0x04, 0x14, 0xFF, 0xFF, 0xFF]
            elif txt == "btn_mem_fault_avail_sts_mask":
                sig_li = [0x02, 0x19, 0x0A]
            elif txt == "btn_mem_fault_nrc_12":
                sig_li = [0x03, 0x19, 0xFF, 0x01]
            elif txt == "btn_mem_fault_nrc_13":
                sig_li = [0x04, 0x19, 0x01, 0x01, 0x01]
            elif txt == "btn_mem_fault_nrc_13_reset":
                sig_li = [0x02, 0x14, 0xFF]
            elif txt == "btn_mem_fault_nrc_22_reset":
                self.main_obj.drv_state = True
                self.main_obj.set_drv_state()
                self.main_obj.thread_worker.slider_speed_func(20)
                self.diag_sess("btn_sess_default")
                sig_li = [0x04, 0x14, 0xFF, 0xFF, 0xFF]
            elif txt == "btn_mem_fault_nrc_31_reset":
                sig_li = [0x04, 0x14, 0x11, 0x11, 0x11]
            self.diag_data_collector(sig_li)
            tx_result = self.res_data[0].data[:4]
        if self.chkbox_diag_test_mode_mem_fault.isChecked():
            if tx_result[2] == 0x19:
                if tx_result[3] == 0x12:
                    self.btn_mem_fault_nrc_12.setEnabled(False)
                    self.label_mem_fault_nrc_12.setText("Success")
                elif tx_result[3] == 0x13:
                    self.btn_mem_fault_nrc_13.setEnabled(False)
                    self.label_mem_fault_nrc_13.setText("Success")
            elif tx_result[2] == 0x14:
                if tx_result[3] == 0x13:
                    self.btn_mem_fault_nrc_13_reset.setEnabled(False)
                    self.label_mem_fault_nrc_13_reset.setText("Success")
                elif tx_result[3] == 0x22:
                    self.btn_mem_fault_nrc_22_reset.setEnabled(False)
                    self.label_mem_fault_nrc_22_reset.setText("Success")
                elif tx_result[3] == 0x31:
                    self.btn_mem_fault_nrc_31_reset.setEnabled(False)
                    self.label_mem_fault_nrc_31_reset.setText("Success")

        if txt == "btn_mem_fault_nrc_22_reset":
            self.main_obj.thread_worker.slider_speed_func(0)
            self.main_obj.drv_state = False
            self.main_obj.set_drv_state()

    def diag_dtc_cont(self, txt):
        if self.chkbox_diag_compression_bit_dtc_cont.isChecked():
            ex_comp_data = True
            ex_comp_sig = True
        else:
            ex_comp_data = False
            ex_comp_sig = False
        self.diag_initialization()
        if txt == 'btn_dtc_cont_en':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x02, 0x85, 0x01]
        elif txt == 'btn_dtc_cont_dis':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x02, 0x85, 0x02]
        elif txt == 'btn_dtc_cont_nrc_12':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x02, 0x85, 0x07]
        elif txt == 'btn_dtc_cont_nrc_13':
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x85, 0x01, 0x01]
        elif txt == "btn_dtc_cont_nrc_7f_en":
            self.diag_sess("btn_sess_default", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x02, 0x85, 0x01]
        elif txt == "btn_dtc_cont_nrc_7f_dis":
            self.diag_sess("btn_sess_default", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x02, 0x85, 0x02]
        elif txt == "btn_dtc_cont_nrc_22_en":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x02, 0x85, 0x01]
        elif txt == "btn_dtc_cont_nrc_22_dis":
            self.main_obj.drv_state = True
            self.main_obj.set_drv_state()
            self.main_obj.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x02, 0x85, 0x02]

        if self.chkbox_diag_compression_bit_dtc_cont.isChecked():
            sig_li[2] = sig_gen.binary_sig(sig_li[2], 0, 1, 1)

        if self.chkbox_diag_test_mode_dtc_cont.isChecked():
            if self.chkbox_diag_compression_bit_dtc_cont.isChecked() and (
                    txt == "btn_dtc_cont_en" or txt == "btn_dtc_cont_dis"):
                self.diag_data_collector(sig_li, comp=True)
                if txt == "btn_dtc_cont_en":
                    self.label_dtc_cont_en.setText("Data Success \n Check the DTC availability")
                elif txt == "btn_dtc_cont_dis":
                    self.label_dtc_cont_dis.setText("Data Success \n Check the DTC disability")
            else:
                self.diag_data_collector(sig_li)
                tx_result = self.res_data[0].data[:4]
                if tx_result[1] == self.diag_success_byte:
                    if tx_result[2] == 0x01:
                        self.label_dtc_cont_en.setText("Data Success \n Check the DTC availability")
                    elif tx_result[2] == 0x02:
                        self.label_dtc_cont_dis.setText("Data Success \n Check the DTC disability")
                else:
                    if tx_result[3] == 0x12:
                        self.btn_dtc_cont_nrc_12.setEnabled(False)
                        self.label_dtc_cont_nrc_12.setText("Success")
                    elif tx_result[3] == 0x13:
                        self.btn_dtc_cont_nrc_13.setEnabled(False)
                        self.label_dtc_cont_nrc_13.setText("Success")
                    elif txt == "btn_dtc_cont_nrc_7f_en" or txt == "btn_dtc_cont_nrc_22_en":
                        if tx_result[3] == 0x7f:
                            self.btn_dtc_cont_nrc_7f_en.setEnabled(False)
                            self.label_dtc_cont_nrc_7f_en.setText("Success")
                        elif tx_result[3] == 0x22:
                            self.btn_dtc_cont_nrc_22_en.setEnabled(False)
                            self.label_dtc_cont_nrc_22_en.setText("Success")
                    elif txt == "btn_dtc_cont_nrc_7f_dis" or txt == "btn_dtc_cont_nrc_22_dis":
                        if tx_result[3] == 0x7f:
                            self.btn_dtc_cont_nrc_7f_dis.setEnabled(False)
                            self.label_dtc_cont_nrc_7f_dis.setText("Success")
                        elif tx_result[3] == 0x22:
                            self.btn_dtc_cont_nrc_22_dis.setEnabled(False)
                            self.label_dtc_cont_nrc_22_dis.setText("Success")
        else:
            self.diag_data_collector(sig_li)

        self.main_obj.drv_state = False
        self.main_obj.set_drv_state()
        self.main_obj.thread_worker.slider_speed_func(0)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Enter:
            self.write_data_sender()

    def tester_present_handler(self):
        if self.chkbox_tester_present.isChecked():
            self.main_obj.tester_present_flag = True
        else:
            self.main_obj.tester_present_flag = False

    def ui_close(self):
        self.close()