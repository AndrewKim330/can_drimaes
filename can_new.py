import os
import sys
import can
import time
import security_algorithm as algo
import dtc_identifier as dtc_id
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtCore
from PyQt5.QtGui import *
from can import interfaces


import can_thread as worker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Ui_MainWindow, QtBaseClass = uic.loadUiType(BASE_DIR + r"./src/untitled.ui")


class Main(QMainWindow, Ui_MainWindow):
    custom_signal = pyqtSignal("PyQt_PyObject")

    def __init__(self):
        super().__init__()

        QtCore.QCoreApplication.processEvents()

        self.setupUi(self)

        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.write_data = [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA]
        self.raw_data = []
        self.res_data = []
        self.temp_list = []
        self.data_len = 0
        self.data_type = None
        self.log_data = []

        self.diag_tester_id = 0x18da41f1

        self.flow = False

        self.write_txt = ''
        self.write_txt_ascii = ''

        self.c_can_bus = None
        self.p_can_bus = None
        self.bus_flag = False

        self.diag_btn_text = None
        self.diag_success_byte = None
        self.diag_failure_byte = 0x7f
        self.drv_state = False
        self.test_mode_basic = False

        self.txt_domain = 'Default'
        self.color_domain = 'gray'
        self.flag_domain = False

        self.flow_control_len = 0

        self.pms_s_hvsm_worker = worker.PMS_S_HVSM(parent=self)
        self.pms_c_strwhl_worker = worker.PMS_C_StrWhl(parent=self)
        self.pms_bodycont_c_worker = worker.PMS_BodyCont_C(parent=self)
        self.pms_ptinfo_worker = worker.PMS_PTInfo(parent=self)

        self.btn_drv_state.clicked.connect(self.set_drv_state)

        # Default value of Power mode radio button
        self.btn_acc.setChecked(True)

        self.bcm_mmi_worker = worker.BCM_MMI(parent=self)
        # Default value of Gear radio button
        self.btn_gear_n.setChecked(True)

        self.bcm_swrc_worker = worker.BCM_SWRC(parent=self)
        self.btn_ok.clicked.connect(self.bcm_swrc_worker.thread_func)
        self.btn_left.pressed.connect(self.bcm_swrc_worker.thread_func)
        self.btn_right.pressed.connect(self.bcm_swrc_worker.thread_func)
        self.btn_right.released.connect(self.bcm_swrc_worker.thread_func)
        self.btn_undo.clicked.connect(self.bcm_swrc_worker.thread_func)
        self.btn_mode.clicked.connect(self.bcm_swrc_worker.thread_func)
        self.btn_mute.clicked.connect(self.bcm_swrc_worker.thread_func)

        self.btn_call.clicked.connect(self.bcm_swrc_worker.thread_func)
        self.btn_vol_up.released.connect(self.bcm_swrc_worker.thread_func)
        self.btn_vol_down.released.connect(self.bcm_swrc_worker.thread_func)

        self.bcm_strwhl_heat_worker = worker.BCM_StrWhlHeat(parent=self)

        self.bcm_lightchime_worker = worker.BCM_LightChime(parent=self)

        self.bcm_stateupdate_worker = worker.BCM_StateUpdate(parent=self)

        self.ic_tachospeed_worker = worker.IC_TachoSpeed(parent=self)
        self.ic_distance_worker = worker.IC_Distance(parent=self)

        self.btn_ota_cond.clicked.connect(self.set_ota_cond)

        self.esc_tpms_worker = worker.ESC_TPMS(parent=self)

        self.btn_tpms_success.clicked.connect(self.esc_tpms_worker.thread_func)
        self.btn_tpms_fail.clicked.connect(self.esc_tpms_worker.thread_func)

        self.btn_bright_afternoon.setChecked(True)

        self.fcs_aeb_worker = worker.FCS_AEB(parent=self)
        self.fcs_ldw_worker = worker.FCS_LDW(parent=self)

        self.btn_mscs_ok.setChecked(True)

        self.btn_mscs_ok.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_CmnFail.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_NotEdgePress.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_EdgeSho.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_SnsrFltT.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_FltPwrSplyErr.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_FltSwtHiSide.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_SigFailr.clicked.connect(self.bcm_mmi_worker.thread_func)

        self.acu_seatbelt_worker = worker.ACU_SeatBelt(parent=self)

        self.chkbox_drv_invalid.stateChanged.connect(self.acu_seatbelt_worker.drv_invalid)
        self.chkbox_pass_invalid.stateChanged.connect(self.acu_seatbelt_worker.pass_invalid)

        self.pms_bodycont_p_worker = worker.PMS_BodyCont_P(parent=self)
        self.pms_vri_worker = worker.PMS_VRI(parent=self)

        self.bms_batt_worker = worker.BMS_Batt(parent=self)
        self.bms_charge_worker = worker.BMS_Charge(parent=self)

        self.mcu_motor_worker = worker.MCU_Motor(parent=self)

        self.tester_worker = worker.TesterPresent(parent=self)

        self.thread_worker = worker.ThreadWorker(parent=self)
        self.thread_worker.sig2.connect(self.sig2)

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

        self.chkbox_diag_functional_domain_basic.released.connect(self.set_diag_basic_btns_labels)
        self.chkbox_diag_test_mode_basic.released.connect(self.set_diag_basic_btns_labels)
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
        self.chkbox_diag_test_mode_comm_cont.released.connect(self.set_diag_comm_cont_btns_labels)
        self.btn_diag_reset_comm_cont.released.connect(self.set_diag_comm_cont_btns_labels)

        # Connect security control buttons to diagnostic handling function
        self.btn_sec_req_seed.released.connect(self.diag_func)
        self.btn_sec_send_key.released.connect(self.diag_func)
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
        self.btn_write_vin.clicked.connect(self.diag_func)

        self.chkbox_diag_test_mode_write.released.connect(self.set_diag_write_btns_labels)
        self.btn_write_data_convert.clicked.connect(self.ascii_convert)

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

        self.chkbox_diag_test_mode_mem_fault.released.connect(self.set_diag_mem_fault_btns_labels)
        self.btn_diag_reset_mem_fault.released.connect(self.set_diag_mem_fault_btns_labels)

        self.btn_bus_connect.clicked.connect(self.bus_connect)

        self.btn_main_console_clear.clicked.connect(self.console_text_clear)
        self.btn_diag_console_clear.clicked.connect(self.console_text_clear)
        self.btn_write_data_clear.clicked.connect(self.console_text_clear)
        self.btn_diag_dtc_console_clear.released.connect(self.console_text_clear)

        self.btn_bus_start.clicked.connect(self.thread_start)
        self.btn_bus_stop.clicked.connect(self.thread_stop)

        self.chkbox_node_acu.released.connect(self.set_node)
        self.chkbox_node_bcm.released.connect(self.set_node)
        self.chkbox_node_esc.released.connect(self.set_node)
        self.chkbox_node_fcs.released.connect(self.set_node)
        self.chkbox_node_ic.released.connect(self.set_node)
        self.chkbox_node_pms.released.connect(self.set_node)
        self.chkbox_node_pms_s.released.connect(self.set_node)
        self.chkbox_node_pms_c.released.connect(self.set_node)
        self.chkbox_node_bms.released.connect(self.set_node)
        self.chkbox_node_mcu.released.connect(self.set_node)

        self.btn_save_log.released.connect(self.save_log)
        self.chkbox_save_log.released.connect(self.save_log)
        self.comboBox_log_format.addItem(".blf")
        self.comboBox_log_format.addItem(".asc")
        self.comboBox_log_format.setEnabled(False)

        self.chkbox_can_dump.released.connect(self.can_dump_mode)

        self.set_node_btns(False)
        self.set_can_basic_btns_labels(False)
        self.set_diag_basic_btns_labels(False)
        self.set_diag_did_btns_labels(False)
        self.set_diag_sec_btns_labels(False)
        self.set_diag_write_btns_labels(False)
        self.set_diag_comm_cont_btns_labels(False)
        self.set_diag_mem_fault_btns_labels(False)

        self.image_initialization()

    def bus_connect(self):
        if not self.bus_flag:
            try:
                temp1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
                self.bus_console.appendPlainText("1 Channel is connected")
                try:
                    temp2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')
                    if temp1.recv(0.1):
                        self.c_can_bus = temp1
                        self.p_can_bus = temp2
                    else:
                        self.c_can_bus = temp2
                        self.p_can_bus = temp1
                    self.bus_console.appendPlainText("2 Channel is connected")
                except:
                    if temp1.recv(0.1):
                        self.c_can_bus = temp1
                    else:
                        self.p_can_bus = temp1

                self.bus_flag = True
                self.bus_console.appendPlainText("PCAN bus is connected")
            except interfaces.pcan.pcan.PcanCanInitializationError as e1:
                print(e1)
                self.bus_console.appendPlainText("PCAN bus is not connected")
                try:
                    self.c_can_bus = can.interface.Bus(bustype='vector', channel=0, bitrate='500000')
                    self.p_can_bus = can.interface.Bus(bustype='vector', channel=1, bitrate='500000')
                    self.bus_flag = True
                    self.bus_console.appendPlainText("Vector bus is connected")
                except interfaces.vector.VectorError as e2:
                    print(e2)
                    self.bus_console.appendPlainText("CAN device is not connected")
                except can.exceptions.CanInterfaceNotImplementedError as e3:
                    print(e3)
                    self.bus_console.appendPlainText("CAN device is not connected")
        else:
            self.bus_console.appendPlainText("CAN bus is already connected")

    def thread_start(self):
        if self.bus_flag:
            # self.data_sender_main = SendDiagMessage(self.c_can_bus)
            # print(self.data_sender_main)
            self.thread_worker._isRunning = True
            self.tester_worker._isRunning = True
            self.set_node()
            self.set_node_btns(True)
            self.thread_worker.start()
            self.tester_worker.start()

            self.set_can_basic_btns_labels(True)
            self.set_diag_basic_btns_labels(True)
            self.thread_worker.test_mode_flag_basic = True
            self.set_diag_did_btns_labels(True)
            self.set_diag_sec_btns_labels(True)
            self.set_diag_write_btns_labels(True)
            self.set_diag_comm_cont_btns_labels(True)
            self.set_diag_mem_fault_btns_labels(True)
            self.diag_initialization()
        else:
            self.bus_console.appendPlainText("Can bus is not connected")

    def thread_stop(self):
        self.set_can_basic_btns_labels(False)

        self.set_diag_basic_btns_labels(False)
        if self.chkbox_diag_test_mode_basic.isChecked():
            self.chkbox_diag_test_mode_basic.toggle()
        if self.chkbox_diag_compression_bit_basic.isChecked():
            self.chkbox_diag_compression_bit_basic.toggle()
        if self.chkbox_diag_functional_domain_basic.isChecked():
            self.chkbox_diag_functional_domain_basic.toggle()

        self.set_diag_did_btns_labels(False)
        if self.chkbox_diag_test_mode_did.isChecked():
            self.chkbox_diag_test_mode_did.toggle()

        self.set_diag_sec_btns_labels(False)
        if self.chkbox_diag_test_mode_sec.isChecked():
            self.chkbox_diag_test_mode_sec.toggle()

        self.set_diag_write_btns_labels(False)
        if self.chkbox_diag_test_mode_write.isChecked():
            self.chkbox_diag_test_mode_write.toggle()

        self.set_diag_comm_cont_btns_labels(False)
        if self.chkbox_diag_compression_bit_comm_cont.isChecked():
            self.chkbox_diag_compression_bit_comm_cont.toggle()
        if self.chkbox_diag_functional_domain_comm_cont.isChecked():
            self.chkbox_diag_functional_domain_comm_cont.toggle()

        self.set_diag_mem_fault_btns_labels(False)

        time.sleep(0.1)

        self.comboBox_log_format.setEnabled(False)
        self.set_node_btns(False)

        self.pms_s_hvsm_worker.stop()
        self.pms_c_strwhl_worker.stop()
        self.pms_bodycont_c_worker.stop()
        self.pms_ptinfo_worker.stop()
        self.bcm_mmi_worker.stop()
        self.bcm_swrc_worker.stop()
        self.bcm_strwhl_heat_worker.stop()
        self.bcm_lightchime_worker.stop()
        self.bcm_stateupdate_worker.stop()
        self.esc_tpms_worker.stop()
        self.fcs_aeb_worker.stop()
        self.fcs_ldw_worker.stop()
        self.bms_batt_worker.stop()
        self.bms_charge_worker.stop()
        self.ic_distance_worker.stop()
        self.ic_tachospeed_worker.stop()
        self.mcu_motor_worker.stop()
        self.pms_bodycont_p_worker.stop()
        self.pms_vri_worker.stop()
        self.mcu_motor_worker.stop()
        self.acu_seatbelt_worker.stop()

        self.thread_worker.stop()
        self.tester_worker.stop()

        self.set_mmi_labels_init()

    def send_message(self, bus, sig_id, send_data):
        if sig_id == 0x18da41f1 or sig_id == 0x18db33f1:
            self.diag_console.appendPlainText("Tester sends the diagnosis message")
        message = can.Message(timestamp=time.time(), arbitration_id=sig_id, data=send_data)
        if self.chkbox_save_log.isChecked():
            self.log_data.append(message)
        bus.send(message)

    def can_dump_mode(self):
        self.chkbox_node_acu.toggle()
        self.chkbox_node_bcm.toggle()
        self.chkbox_node_esc.toggle()
        self.chkbox_node_fcs.toggle()
        self.chkbox_node_ic.toggle()
        self.chkbox_node_pms.toggle()
        self.chkbox_node_pms_s.toggle()
        self.chkbox_node_pms_c.toggle()
        self.chkbox_node_bms.toggle()
        self.chkbox_node_mcu.toggle()

    def save_log(self):
        if self.sender().objectName() == "btn_save_log":
            if len(self.log_data) > 0:
                self.bus_console.appendPlainText("Can Log saving Start")
                log_dir = BASE_DIR + f"./log{self.comboBox_log_format.currentText()}"
                f = open(log_dir, 'w')
                count = 0
                while count < len(self.log_data):
                    sig_id = self.log_data[count].arbitration_id
                    if sig_id == 0x18ffd741 or sig_id == 0x18ffd841 or sig_id == 0x0c0ba021 or sig_id == 0x18a9e821 or sig_id == 0x18ff6341 or sig_id == 0x18ff4b41:
                        data = 'tx ' + str(self.log_data[count])
                    else:
                        data = 'rx ' + str(self.log_data[count])
                    f.write(data)
                    f.write('\n')
                    count += 1
                f.close()
                self.bus_console.appendPlainText("Can Log saving End")
                QMessageBox.information(self, "Log Save", "CAN Log Saving complete")
                self.log_data = []
        elif self.sender().objectName() == "chkbox_save_log":
            if self.chkbox_save_log.isChecked():
                self.bus_console.appendPlainText("Can Log Writing Start")
            else:
                self.bus_console.appendPlainText("Can Log Writing Stop")
                self.comboBox_log_format.setEnabled(True)

    def set_node(self):
        if self.chkbox_node_acu.isChecked():
            self.acu_seatbelt_worker._isRunning = True
            self.acu_seatbelt_worker.start()
        else:
            self.acu_seatbelt_worker.stop()

        if self.chkbox_node_bcm.isChecked():
            self.bcm_mmi_worker._isRunning = True
            self.bcm_swrc_worker._isRunning = True
            self.bcm_strwhl_heat_worker._isRunning = True
            self.bcm_lightchime_worker._isRunning = True
            self.bcm_stateupdate_worker._isRunning = True
            self.bcm_mmi_worker.start()
            self.bcm_swrc_worker.start()
            self.bcm_strwhl_heat_worker.start()
            self.bcm_lightchime_worker.start()
            self.bcm_stateupdate_worker.start()
        else:
            self.bcm_mmi_worker.stop()
            self.bcm_swrc_worker.stop()
            self.bcm_strwhl_heat_worker.stop()
            self.bcm_lightchime_worker.stop()
            self.bcm_stateupdate_worker.stop()

        if self.chkbox_node_esc.isChecked():
            self.esc_tpms_worker._isRunning = True
            self.esc_tpms_worker.start()
        else:
            self.esc_tpms_worker.stop()

        if self.chkbox_node_fcs.isChecked():
            self.fcs_aeb_worker._isRunning = True
            self.fcs_ldw_worker._isRunning = True
            self.fcs_aeb_worker.start()
            self.fcs_ldw_worker.start()
        else:
            self.fcs_aeb_worker.stop()
            self.fcs_ldw_worker.stop()

        if self.chkbox_node_ic.isChecked():
            self.ic_distance_worker._isRunning = True
            self.ic_tachospeed_worker._isRunning = True
            self.ic_distance_worker.start()
            self.ic_tachospeed_worker.start()
        else:
            self.ic_distance_worker.stop()
            self.ic_tachospeed_worker.stop()

        if self.chkbox_node_pms.isChecked():
            self.pms_bodycont_c_worker._isRunning = True
            self.pms_ptinfo_worker._isRunning = True
            self.pms_bodycont_p_worker._isRunning = True
            self.pms_vri_worker._isRunning = True
            self.pms_bodycont_c_worker.start()
            self.pms_ptinfo_worker.start()
            self.pms_bodycont_p_worker.start()
            self.pms_vri_worker.start()
        else:
            self.pms_bodycont_c_worker.stop()
            self.pms_ptinfo_worker.stop()
            self.pms_bodycont_p_worker.stop()
            self.pms_vri_worker.stop()

        if self.chkbox_node_pms_s.isChecked():
            self.pms_s_hvsm_worker.start()
            self.pms_s_hvsm_worker._isRunning = True
        else:
            self.pms_s_hvsm_worker.stop()

        if self.chkbox_node_pms_c.isChecked():
            self.pms_c_strwhl_worker._isRunning = True
            self.pms_c_strwhl_worker.start()
        else:
            self.pms_c_strwhl_worker.stop()

        if self.chkbox_node_bms.isChecked():
            self.bms_batt_worker._isRunning = True
            self.bms_charge_worker._isRunning = True
            self.bms_batt_worker.start()
            self.bms_charge_worker.start()
        else:
            self.bms_batt_worker.stop()
            self.bms_charge_worker.stop()

        if self.chkbox_node_mcu.isChecked():
            self.mcu_motor_worker._isRunning = True
            self.mcu_motor_worker.start()
        else:
            self.mcu_motor_worker.stop()

    def set_drv_state(self):
        if self.drv_state or self.sender().text() == 'Set Driving State':
            self.btn_gear_d.setChecked(True)
            self.btn_start.setChecked(True)
            self.chkbox_pt_ready.setChecked(True)
        else:
            self.btn_gear_n.setChecked(True)
            self.btn_acc.setChecked(True)
            self.chkbox_pt_ready.setChecked(False)
            self.thread_worker.slider_speed_func(0)

    def set_ota_cond(self):
        if self.btn_ota_cond.text() == 'On OTA Condition':
            self.chkbox_h_brake.setChecked(False)
        else:
            self.btn_gear_n.setChecked(True)
            self.chkbox_h_brake.setChecked(True)

    def set_mmi_labels_init(self):
        self.txt_res_aeb.setText("None")
        self.txt_res_drv_heat.setText("OFF")
        self.txt_res_drv_vent.setText("OFF")
        self.txt_res_pass_heat.setText("OFF")
        self.txt_res_pass_vent.setText("OFF")
        self.txt_res_side_mani.setText("None")
        self.txt_res_side_heat.setText("None")
        self.txt_res_st_whl_heat.setText("OFF")
        self.txt_res_light.setText("OFF")

    def set_node_btns(self, flag):
        self.chkbox_node_acu.setEnabled(flag)
        self.chkbox_node_bcm.setEnabled(flag)
        self.chkbox_node_esc.setEnabled(flag)
        self.chkbox_node_fcs.setEnabled(flag)
        self.chkbox_node_ic.setEnabled(flag)
        self.chkbox_node_pms.setEnabled(flag)
        self.chkbox_node_pms_s.setEnabled(flag)
        self.chkbox_node_pms_c.setEnabled(flag)
        self.chkbox_node_bms.setEnabled(flag)
        self.chkbox_node_mcu.setEnabled(flag)

    def set_can_basic_btns_labels(self, flag):
        if flag:
            color = "black"
            self.slider_speed.sliderMoved.connect(self.thread_worker.slider_speed_func)
            self.slider_speed.valueChanged.connect(self.thread_worker.slider_speed_func)

            self.slider_battery.sliderMoved.connect(self.thread_worker.slider_battery_func)
            self.slider_battery.valueChanged.connect(self.thread_worker.slider_battery_func)
        else:
            color = "gray"

        self.btn_gear_n.setEnabled(flag)
        self.btn_gear_r.setEnabled(flag)
        self.btn_gear_d.setEnabled(flag)

        self.btn_acc_off.setEnabled(flag)
        self.btn_acc.setEnabled(flag)
        self.btn_ign.setEnabled(flag)
        self.btn_start.setEnabled(flag)

        self.chkbox_pt_ready.setEnabled(flag)

        self.btn_drv_state.setEnabled(flag)

        self.btn_ok.setEnabled(flag)
        self.btn_left.setEnabled(flag)
        self.btn_left_long.setEnabled(flag)
        self.btn_right.setEnabled(flag)
        self.btn_right_long.setEnabled(flag)
        self.btn_undo.setEnabled(flag)
        self.btn_mode.setEnabled(flag)
        self.btn_mute.setEnabled(flag)

        self.btn_call.setEnabled(flag)
        self.btn_call_long.setEnabled(flag)
        self.btn_vol_up.setEnabled(flag)
        self.btn_vol_up_long.setEnabled(flag)
        self.btn_vol_down.setEnabled(flag)
        self.btn_vol_down_long.setEnabled(flag)

        self.btn_reset.setEnabled(flag)

        self.btn_ota_cond.setEnabled(flag)

        self.chkbox_h_brake.setEnabled(flag)

        self.btn_tpms_success.setEnabled(flag)
        self.btn_tpms_fail.setEnabled(flag)

        self.btn_bright_afternoon.setEnabled(flag)
        self.btn_bright_night.setEnabled(flag)

        self.btn_mscs_ok.setEnabled(flag)
        self.btn_mscs_CmnFail.setEnabled(flag)
        self.btn_mscs_NotEdgePress.setEnabled(flag)
        self.btn_mscs_EdgeSho.setEnabled(flag)
        self.btn_mscs_SnsrFltT.setEnabled(flag)
        self.btn_mscs_FltPwrSplyErr.setEnabled(flag)
        self.btn_mscs_FltSwtHiSide.setEnabled(flag)
        self.btn_mscs_SigFailr.setEnabled(flag)

        self.slider_battery.setEnabled(flag)
        self.chkbox_charge.setEnabled(flag)

        self.tick_0_speed.setStyleSheet(f"color: {color}")
        self.tick_120.setStyleSheet(f"color: {color}")
        self.tick_240.setStyleSheet(f"color: {color}")
        self.label_speed.setStyleSheet(f"color: {color}")

        self.tick_0_batt.setStyleSheet(f"color: {color}")
        self.tick_50.setStyleSheet(f"color: {color}")
        self.tick_100.setStyleSheet(f"color: {color}")
        self.label_battery.setStyleSheet(f"color: {color}")

        self.chkbox_drv_invalid.setEnabled(flag)
        self.chkbox_pass_invalid.setEnabled(flag)

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

        self.btn_id_ecu_num.setEnabled(self.flag_domain)
        self.label_id_ecu_num.setText(f"{self.txt_domain}")
        self.label_id_ecu_num.setStyleSheet(f"color: {self.color_domain}")
        self.btn_id_ecu_supp.setEnabled(flag)
        self.label_id_ecu_supp.setText(f"{txt}")
        self.label_id_ecu_supp.setStyleSheet(f"color: {color}")
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

        self.btn_id_nrc_13.setEnabled(flag)
        self.label_id_nrc_13.setText(f"{txt}")
        self.label_id_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_id_nrc_31.setEnabled(flag)
        self.label_id_nrc_31.setText(f"{txt}")
        self.label_id_nrc_31.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_did.setEnabled(flag)
        self.chkbox_diag_test_mode_did.setEnabled(flag)

    def set_diag_sec_btns_labels(self, flag=True):
        if flag:
            color = "black"
        else:
            color = "gray"

        self.btn_sec_req_seed.setEnabled(flag)
        self.label_sec_req_seed.setStyleSheet(f"color: {color}")
        self.btn_sec_send_key.setEnabled(flag)
        self.label_sec_send_key.setStyleSheet(f"color: {color}")

        self.btn_sec_nrc_12.setEnabled(flag)
        self.label_sec_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_13.setEnabled(flag)
        self.label_sec_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_24.setEnabled(flag)
        self.label_sec_nrc_24.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_35.setEnabled(flag)
        self.label_sec_nrc_35.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_36.setEnabled(flag)
        self.label_sec_nrc_36.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_37.setEnabled(flag)
        self.label_sec_nrc_37.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_7f_req.setEnabled(flag)
        self.label_sec_nrc_7f_req.setStyleSheet(f"color: {color}")
        self.btn_sec_nrc_7f_send.setEnabled(flag)
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

        self.lineEdit_write_data.setEnabled(flag)
        self.btn_write_data_clear.setEnabled(flag)
        self.btn_write_data_convert.setEnabled(flag)

        self.btn_write_vin.setEnabled(flag)
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
        self.btn_write_nrc_31.setEnabled(flag)
        self.label_write_nrc_31.setText(f"{txt}")
        self.label_write_nrc_31.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_write.setEnabled(flag)
        self.chkbox_diag_test_mode_write.setEnabled(flag)

    def set_diag_comm_cont_btns_labels(self, flag=True):
        if self.chkbox_diag_test_mode_comm_cont.isChecked():
            self.chkbox_diag_compression_bit_comm_cont.setEnabled(True)
            self.chkbox_diag_functional_domain_comm_cont.setEnabled(True)
            color = 'black'
            txt = "Not tested"
        else:
            self.chkbox_diag_compression_bit_comm_cont.setEnabled(False)
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
        self.btn_mem_fault_num_check.setEnabled(flag)
        self.btn_mem_fault_list_check.setEnabled(flag)
        self.btn_mem_fault_reset.setEnabled(flag)
        self.btn_mem_fault_avail_sts_mask.setEnabled(flag)
        if self.sender():
            if self.chkbox_diag_test_mode_mem_fault.isChecked():
                self.chkbox_diag_functional_domain_mem_fault.setEnabled(True)
                color = 'black'
                txt = "Not tested"
                self.btn_mem_fault_num_check.setEnabled(not flag)
                self.btn_mem_fault_list_check.setEnabled(not flag)
                self.btn_mem_fault_reset.setEnabled(not flag)
                self.btn_mem_fault_avail_sts_mask.setEnabled(not flag)
            else:
                self.chkbox_diag_functional_domain_mem_fault.setEnabled(False)
                color = 'gray'
                txt = "Default"
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

    def console_text_clear(self, txt=None):
        if self.sender().objectName() == "btn_main_console_clear":
            self.main_console.clear()
        elif self.sender().objectName() == "btn_diag_console_clear":
            self.diag_console.clear()
        elif self.sender().objectName() == "btn_write_data_clear" or txt:
            self.label_flag_convert.setText("Fill the data")
            self.lineEdit_write_data.clear()
        elif self.sender().objectName() == "btn_diag_dtc_console_clear":
            self.diag_dtc_console.clear()

    def diag_initialization(self):
        self.flow_control_len = 1
        self.res_data = []
        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.write_data = [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA]
        self.raw_data = []
        self.lineEdit_write_data.clear()
        self.lineEdit_id_data.clear()
        self.drv_state = False
        self.set_drv_state()

    def diag_data_collector(self, mess, multi=False):
        self.res_data = []
        self.raw_data = []
        flag = False
        bb = []
        counter = 0
        while len(self.res_data) < self.flow_control_len:
            for i, mess_data in zip(range(len(mess)), mess):
                self.data[i] = mess_data
            self.send_message(self.c_can_bus, self.diag_tester_id, self.data)
            if multi:
                time.sleep(0.020)
                self.data[0] = 0x30
                self.send_message(self.c_can_bus, self.diag_tester_id, self.data)
            time.sleep(0.3)
            reservoir = self.thread_worker.reservoir[:]
            if multi:
                if flag:
                    for qqq in reservoir:
                        if qqq.data[0] == 0x03:
                            continue
                        uni = bb | {qqq.data[0]}
                        if bb != uni:
                            bb.add(qqq.data[0])
                            self.res_data.append(qqq)
                            break
                else:
                    for qqq in reservoir:
                        if qqq.data[0] == 0x03:
                            continue
                        bb.append(qqq.data[0])
                        self.res_data.append(qqq)
                    bb = set(bb)
                    flag = True
            else:
                for tx_single in reservoir:
                    if tx_single.arbitration_id == 0x18daf141:
                        self.res_data.append(tx_single)
            self.thread_worker.reservoir = []
            QtCore.QCoreApplication.processEvents()
            if counter > 50:
                return 0
        temp_li = []
        if len(self.res_data) == 1:
            if self.data_len > 0:
                self.raw_data += self.res_data[0].data[1:8]
        else:
            for i in range(self.flow_control_len):
                for j in range(self.flow_control_len):
                    a = self.res_data[j].data[0] % 0x10
                    if i == a:
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

    def ascii_convert(self, conv=None):
        if conv == 'a2c':
            entire_ch = ''
            for ch in self.raw_data[3:]:
                entire_ch += chr(ch)
            self.lineEdit_id_data.setText(entire_ch)
        else:
            self.write_txt = self.lineEdit_write_data.text()
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
                self.label_flag_convert.setText(f'Conversion Success - Data : {self.write_txt}, length: {txt_len}')
                self.write_txt_ascii = ascii_li

    def write_data_not_correct(self, txt):
        if txt == "btn_write_vin":
            err = "Length Error"
            message = "Incorrect length of VIN number \n (Need to 17 Character)"
        elif txt == "btn_write_install_date":
            pass
        elif txt == "btn_write_veh_name":
            pass
        elif txt == "btn_write_sys_name":
            pass
        elif txt == "btn_write_net_config":
            pass
        QMessageBox.warning(self, err, message)
        self.console_text_clear(err)

    @pyqtSlot(can.Message)
    def sig2(self, tx_single):
        self.main_console.appendPlainText(str(tx_single))

    def diag_func(self):
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
                    or self.diag_btn_text == "btn_id_nrc_13" or self.diag_btn_text == "btn_id_nrc_31":
                self.diag_success_byte = 0x62
                self.diag_did(self.diag_btn_text)
            elif self.diag_btn_text == "btn_sec_req_seed" or self.diag_btn_text == "btn_sec_send_key" \
                    or self.diag_btn_text == "btn_sec_nrc_12" or self.diag_btn_text == "btn_sec_nrc_13" \
                    or self.diag_btn_text == "btn_sec_nrc_24" or self.diag_btn_text == "btn_sec_nrc_35" \
                    or self.diag_btn_text == "btn_sec_nrc_36" or self.diag_btn_text == "btn_sec_nrc_37" \
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
                    or self.diag_btn_text == "btn_write_nrc_13" or self.diag_btn_text == "btn_write_nrc_31":
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

    def diag_sess(self, txt):
        # **need to add test failed scenario
        self.diag_initialization()
        if txt == "btn_sess_default":
            sig_li = [0x02, 0x10, 0x01]
        elif txt == "btn_sess_extended":
            sig_li = [0x02, 0x10, 0x03]
        elif txt == "btn_sess_nrc_12":
            sig_li = [0x02, 0x10, 0xFF]
        elif txt == "btn_sess_nrc_13":
            sig_li = [0x03, 0x10, 0x01, 0x01]
        self.diag_data_collector(sig_li)
        tx_result = self.res_data[0].data[:4]
        if self.chkbox_diag_test_mode_basic.isChecked():
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

    def diag_reset(self, txt):
        self.diag_initialization()
        if txt == "btn_reset_sw":
            self.diag_sess("btn_sess_extended")
            sig_li = [0x02, 0x11, 0x01]
        elif txt == "btn_reset_hw":
            self.diag_sess("btn_sess_extended")
            sig_li = [0x02, 0x11, 0x03]
        elif txt == "btn_reset_nrc_12":
            self.diag_sess("btn_sess_extended")
            sig_li = [0x02, 0x11, 0x07]
        elif txt == "btn_reset_nrc_13":
            self.diag_sess("btn_sess_extended")
            sig_li = [0x03, 0x11, 0x01, 0x01]
        elif txt == "btn_reset_nrc_7f_sw":
            self.diag_sess("btn_sess_default")
            sig_li = [0x02, 0x11, 0x01]
        elif txt == "btn_reset_nrc_7f_hw":
            self.diag_sess("btn_sess_default")
            sig_li = [0x02, 0x11, 0x03]
        elif txt == "btn_reset_nrc_22_sw":
            self.diag_sess("btn_sess_extended")
            self.drv_state = True
            self.set_drv_state()
            self.thread_worker.slider_speed_func(20)
            time.sleep(0.1)
            sig_li = [0x02, 0x11, 0x01]
        elif txt == "btn_reset_nrc_22_hw":
            self.diag_sess("btn_sess_extended")
            self.drv_state = True
            self.set_drv_state()
            self.thread_worker.slider_speed_func(20)
            time.sleep(0.1)
            sig_li = [0x02, 0x11, 0x03]
        self.diag_data_collector(sig_li)
        tx_result = self.res_data[0].data[:4]
        if self.chkbox_diag_test_mode_basic.isChecked():
            if tx_result[1] == self.diag_success_byte:
                if tx_result[2] == 0x01:
                    self.btn_reset_sw.setEnabled(False)
                    self.label_reset_sw.setText("Success")
                elif tx_result[2] == 0x03:
                    self.btn_reset_hw.setEnabled(False)
                    self.label_reset_hw.setText("Success")
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

    def diag_tester(self, txt):
        # **need to add test failed scenario
        self.diag_initialization()
        if txt == "btn_tester":
            sig_li = [0x02, 0x3E, 0x00]
        elif txt == "btn_tester_nrc_12":
            sig_li = [0x02, 0x3E, 0x03]
        elif txt == "btn_tester_nrc_13":
            sig_li = [0x03, 0x3E, 0x00, 0x01]
        self.diag_data_collector(sig_li)
        tx_result = self.res_data[0].data[:4]
        if self.chkbox_diag_test_mode_basic.isChecked():
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
            self.data_type = "bcd"
            sig_li = [0x03, 0x22, 0xF1, 0xA2]
            self.data_len = 4
        elif txt == "btn_id_diag_ver":
            self.data_type = "hex"
            sig_li = [0x03, 0x22, 0xF1, 0x13]
            self.data_len = 4
        elif txt == "btn_id_sys_name":
            self.flow_control_len = 2
            self.data_type = "ascii"
            sig_li = [0x03, 0x22, 0xF1, 0x97]
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
                self.ascii_convert('a2c')
            elif self.data_type == "bcd":
                print(self.raw_data)
                temp_str = f'{str(hex(self.raw_data[3])[2:].zfill(2))}{str(hex(self.raw_data[4])[2:].zfill(2))}/{str(hex(self.raw_data[5])[2:].zfill(2))}/{str(hex(self.raw_data[6])[2:].zfill(2))}'
                self.lineEdit_id_data.setText(temp_str)
            elif self.data_type == "hex":
                temp_str = ''
                for temp_ch in self.raw_data[3:]:
                    if temp_ch != 0xaa:
                        temp_str += hex(temp_ch)[2:]
                        temp_str += ' '
                self.lineEdit_id_data.setText(temp_str)
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

    def diag_security_access(self, txt):
        self.diag_initialization()
        if txt == "btn_sec_req_seed":
            self.diag_sess("btn_sess_extended")
            time.sleep(0.1)
            sig_li = [0x02, 0x27, 0x01]
            self.diag_data_collector(sig_li)
            self.req_seed = self.res_data[0].data[3:7]
        elif txt == "btn_sec_send_key":
            while len(self.res_data) < self.flow_control_len:
                self.diag_sess("btn_sess_default")
                time.sleep(0.1)
                self.diag_security_access("btn_sec_req_seed")
                seed_converted = algo.secu_algo(self.req_seed)
                sig_li = [0x06, 0x27, 0x02]
                time.sleep(0.1)
                self.diag_data_collector(sig_li + seed_converted)
                if self.res_data[0].data[1] == 0x67 and self.res_data[0].data[2] == 0x02:
                    break
                else:
                    self.res_data = []
        else:
            if txt == "btn_sec_nrc_12":
                self.diag_sess("btn_sess_extended")
                sig_li = [0x02, 0x27, 0x03]
            elif txt == "btn_sec_nrc_13":
                self.diag_sess("btn_sess_extended")
                sig_li = [0x03, 0x27, 0x01, 0x01]
            elif txt == "btn_sec_nrc_24":
                self.diag_sess("btn_sess_extended")
                sig_li = [0x02, 0x27, 0x02]
            elif txt == "btn_sec_nrc_35":
                self.diag_sess("btn_sess_default")
                time.sleep(0.1)
                self.diag_security_access("btn_sec_req_seed")
                sig_li = [0x06, 0x27, 0x02, 0x00, 0x00, 0x00, 0x00]
                time.sleep(0.1)
            elif txt == "btn_sec_nrc_36":
                count = 0
                while count < 3:
                    self.diag_sess("btn_sess_default")
                    self.diag_security_access("btn_sec_nrc_35")
                    count += 1
                sig_li = [0x02, 0x27, 0x01]
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

    def diag_write(self, txt):
        self.diag_initialization()
        if self.chkbox_diag_test_mode_write.isChecked():
            test_mode = True
        else:
            test_mode = False
        if txt == "btn_write_vin":
            data_len = len(self.write_txt_ascii)
            if data_len != 17:
                self.write_data_not_correct(txt)
            else:
                count = 0
                while count < self.flow_control_len:
                    self.diag_security_access("btn_sec_send_key")
                    self.flow_control_len = 3
                    temp_li = []
                    for i in range(self.flow_control_len):
                        self.write_data = [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA]
                        if i == 0:
                            self.write_data[0] = 0x10
                            self.write_data[1] = 0x14
                            self.write_data[2] = 0x2E
                            self.write_data[3] = 0xF1
                            self.write_data[4] = 0x90
                            self.write_data[5] = self.write_txt_ascii.pop(0)
                            self.write_data[6] = self.write_txt_ascii.pop(0)
                            self.write_data[7] = self.write_txt_ascii.pop(0)
                        else:
                            for j in range(8):
                                if len(self.write_txt_ascii) > 0:
                                    if j == 0:
                                        self.write_data[0] = (0x20 + i)
                                    else:
                                        self.write_data[j] = self.write_txt_ascii.pop(0)

                        temp_li.append(self.write_data)
                    for w_data in temp_li:
                        self.data = w_data
                        self.diag_send_message()
                        time.sleep(0.030)
                    time.sleep(1)
                    reservoir = self.thread_worker.reservoir[:]
                    for qqq in reservoir:
                        if qqq.arbitration_id == 0x18daf141:
                            temp = qqq
                            count = self.flow_control_len
                    self.thread_worker.reservoir = []
                    QtCore.QCoreApplication.processEvents()
                self.diag_console.appendPlainText(str(temp))
        #     time.sleep(0.2)
        #     zzz = copy.copy(self.tx_worker.ggg)
        #     for qqq in zzz:
        #         if qqq[8] == "10":
        #             count = int(int(qqq[9], 16) / 7) + 1
        #             self.diag_console.appendPlainText(str(qqq))
        #     self.tx_worker.ggg = []
        #     QtCore.QCoreApplication.processEvents()
        # self.flow_control_len = count
        # elif txt == "btn_id_ecu_supp":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x8A
        #     self.flow_control_len = 2
        # elif txt == "btn_id_vin":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x90
        #     self.flow_control_len = 3
        # elif txt == "btn_id_install_date":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0xA2
        # elif txt == "btn_id_diag_ver":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x13
        # elif txt == "btn_id_sys_name":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x97
        #     self.flow_control_len = 2
        # elif txt == "btn_id_active_sess":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x86
        # elif txt == "btn_id_veh_name":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x12
        #     self.flow_control_len = 2
        # elif txt == "btn_id_ecu_serial":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x8C
        #     self.flow_control_len = 4
        # elif txt == "btn_id_hw_ver":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x93
        #     self.flow_control_len = 3
        # elif txt == "btn_id_sw_ver":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x95
        #     self.flow_control_len = 3
        # elif txt == "btn_id_ecu_manu_date":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x8B
        # elif txt == "btn_id_assy_num":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x8E
        #     self.flow_control_len = 3
        # elif txt == "btn_id_net_config":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0xF1
        #     self.data[3] = 0x10
        #     self.flow_control_len = 2
        # elif txt == "btn_sess_nrc_13":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x22
        #     self.data[2] = 0x01
        #     self.data[3] = 0x01
        #     self.data[4] = 0x01
        # elif txt == "btn_sess_nrc_31":
        #     self.data[0] = 0x22
        #     self.data[1] = 0xFF
        #     self.data[2] = 0xFF
        # temp_li = []
        # while len(temp_li) < self.flow_control_len:
        #     self.diag_console.appendPlainText("Thread trying to send message")
        #     message = can.Message(arbitration_id=0x18da41f1, data=self.data)
        #     self.c_can_bus.send(message)
        #     time.sleep(0.5)
        #     zzz = copy.copy(self.tx_worker.ggg)
        #     for qqq in zzz:
        #         if qqq[3] == "18daf141":
        #             temp_li.append(qqq)
        #     QtCore.QCoreApplication.processEvents()
        # # if test_mode:
        # #     if temp[9] == self.diag_success_byte:
        # #         if temp[10] == "01":
        # #             self.btn_sess_default.setEnabled(False)
        # #             self.label_sess_default.setText("Success")
        # #         elif temp[10] == "03":
        # #             self.btn_sess_extended.setEnabled(False)
        # #             self.label_sess_extended.setText("Success")
        # #     else:
        # #         if temp[11] == "12":
        # #             self.btn_sess_nrc_12.setEnabled(False)
        # #             self.label_sess_nrc_12.setText("Success")
        # #         elif temp[11] == "13":
        # #             self.btn_sess_nrc_13.setEnabled(False)
        # #             self.label_sess_nrc_13.setText("Success")
        # # self.diag_console.appendPlainText(str(temp))
        # self.tx_worker.ggg = []
        # # **need to add test failed scenario

    def diag_comm_cont(self, txt):
        self.diag_initialization()
        if txt == 'btn_comm_cont_all_en':
            self.diag_sess("btn_sess_extended")
            sig_li = [0x03, 0x28, 0x00, 0x01]
        elif txt == 'btn_comm_cont_tx_dis':
            self.diag_sess("btn_sess_extended")
            sig_li = [0x03, 0x28, 0x01, 0x01]
        elif txt == 'btn_comm_cont_all_dis':
            self.diag_sess("btn_sess_extended")
            sig_li = [0x03, 0x28, 0x03, 0x01]
        elif txt == 'btn_comm_cont_nrc_12':
            self.diag_sess("btn_sess_extended")
            sig_li = [0x03, 0x28, 0x0F, 0x01]
        elif txt == 'btn_comm_cont_nrc_13':
            self.diag_sess("btn_sess_extended")
            sig_li = [0x04, 0x28, 0x00, 0x01, 0x01]
        elif txt == 'btn_comm_cont_nrc_31':
            self.diag_sess("btn_sess_extended")
            sig_li = [0x03, 0x28, 0x00, 0xFF]
        elif txt == "btn_comm_cont_nrc_7f_all_en":
            self.diag_sess("btn_sess_default")
            sig_li = [0x03, 0x28, 0x00, 0x01]
        elif txt == "btn_comm_cont_nrc_7f_tx_dis":
            self.diag_sess("btn_sess_default")
            sig_li = [0x03, 0x28, 0x01, 0x01]
        elif txt == "btn_comm_cont_nrc_7f_all_dis":
            self.diag_sess("btn_sess_default")
            sig_li = [0x03, 0x28, 0x03, 0x01]
        elif txt == "btn_comm_cont_nrc_22_all_en":
            self.diag_sess("btn_sess_extended")
            self.drv_state = True
            self.set_drv_state()
            self.thread_worker.slider_speed_func(20)
            time.sleep(0.2)
            sig_li = [0x03, 0x28, 0x00, 0x01]
        elif txt == "btn_comm_cont_nrc_22_tx_dis":
            self.diag_sess("btn_sess_extended")
            self.drv_state = True
            self.set_drv_state()
            self.thread_worker.slider_speed_func(20)
            time.sleep(0.2)
            sig_li = [0x03, 0x28, 0x01, 0x01]
        elif txt == "btn_comm_cont_nrc_22_all_dis":
            self.diag_sess("btn_sess_extended")
            self.drv_state = True
            self.set_drv_state()
            self.thread_worker.slider_speed_func(20)
            time.sleep(0.2)
            sig_li = [0x03, 0x28, 0x03, 0x01]
        self.diag_data_collector(sig_li)
        self.drv_state = False
        self.thread_worker.slider_speed_func(0)
        self.set_drv_state()
        tx_result = self.res_data[0].data[:4]
        if self.chkbox_diag_test_mode_comm_cont.isChecked():
            if tx_result[1] == self.diag_success_byte:
                if tx_result[2] == 0x00:
                    self.btn_comm_cont_all_en.setEnabled(False)
                    self.label_comm_cont_all_en.setText("Success")
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

    def diag_memory_fault(self, txt):
        self.diag_initialization()
        if txt == "btn_mem_fault_list_check":
            self.diag_memory_fault("btn_mem_fault_num_check")
            dtc_num = self.res_data[0].data[6]
            if dtc_num > 1:
                occu = 5
                self.flow_control_len = 2
                for i in range(dtc_num - 2):
                    for j in range(4):
                        occu += 1
                        if occu == 7:
                            self.flow_control_len += 1
                            occu = 0
            self.res_data = []
            sig_li = [0x03, 0x19, 0x02, 0x09]
            self.diag_data_collector(sig_li, True)
            if len(self.raw_data) == 0:
                self.raw_data = self.res_data[0].data[1:8]
            st = 3
            for i in range(dtc_num):
                if i == 0:
                    self.diag_dtc_console.appendPlainText(f'- Number of DTCs : {dtc_num}')
                single_dtc = self.raw_data[st:st+4]
                st += 4
                dtc_name = dtc_id.dtc_identifier(single_dtc)
                self.diag_dtc_console.appendPlainText(f'DTC Code : 0x{hex(single_dtc[0])[2:].zfill(2)} 0x{hex(single_dtc[1])[2:].zfill(2)} 0x{hex(single_dtc[2])[2:].zfill(2)} - {dtc_name}')
        else:
            if txt == "btn_mem_fault_num_check":
                sig_li = [0x03, 0x19, 0x01, 0x09]
            elif txt == "btn_mem_fault_reset":
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
                self.drv_state = True
                self.set_drv_state()
                self.thread_worker.slider_speed_func(20)
                time.sleep(0.1)
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

    def image_initialization(self):
        self.img_drv_heat_off = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_off.png").scaledToWidth(100)
        self.img_drv_heat_1 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_01_on.png").scaledToWidth(100)
        self.img_drv_heat_2 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_02_on.png").scaledToWidth(100)
        self.img_drv_heat_3 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_03_on.png").scaledToWidth(100)
        self.img_drv_vent_off = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_off.png").scaledToWidth(100)
        self.img_drv_vent_1 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_01_on.png").scaledToWidth(100)
        self.img_drv_vent_2 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_02_on.png").scaledToWidth(100)
        self.img_drv_vent_3 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_03_on.png").scaledToWidth(100)
        self.img_pass_heat_off = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_off.png").scaledToWidth(100)
        self.img_pass_heat_1 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_01_on.png").scaledToWidth(100)
        self.img_pass_heat_2 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_02_on.png").scaledToWidth(100)
        self.img_pass_heat_3 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_03_on.png").scaledToWidth(100)
        self.img_pass_vent_off = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_off.png").scaledToWidth(100)
        self.img_pass_vent_1 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_01_on.png").scaledToWidth(100)
        self.img_pass_vent_2 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_02_on.png").scaledToWidth(100)
        self.img_pass_vent_3 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_03_on.png").scaledToWidth(100)

        self.img_side_mani_on = QPixmap(BASE_DIR + r"./src/images/side/btn_navi_sidemirror_normal.png").scaledToWidth(100)
        self.img_side_mani_off = QPixmap(BASE_DIR + r"./src/images/side/btn_navi_sidemirror_fold.png").scaledToWidth(100)
        self.img_side_heat_on = QPixmap(BASE_DIR + r"./src/images/side/sidemirrorheat_on.png").scaledToWidth(100)
        self.img_side_heat_off = QPixmap(BASE_DIR + r"./src/images/side/sidemirrorheat_off.png").scaledToWidth(100)

        self.img_str_whl_heat_off = QPixmap(BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_off.png").scaledToWidth(
            100)
        self.img_str_whl_heat_1 = QPixmap(BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_01_on.png").scaledToWidth(
            100)
        self.img_str_whl_heat_2 = QPixmap(BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_02_on.png").scaledToWidth(
            100)
        self.img_str_whl_heat_3 = QPixmap(BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_03_on.png").scaledToWidth(
            100)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Main()
    mywindow.show()
    sys.exit(app.exec_())
