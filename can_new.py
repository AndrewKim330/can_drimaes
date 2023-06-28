import copy

import scrapping3 as scr

import sys
import can
import time
import security_algorithm as algo
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtCore
from can import interfaces


import can_thread as worker

form_class = uic.loadUiType("untitled.ui")[0]
# form_class = uic.loadUiType("can_dist.ui")[0]

class Main(QMainWindow, form_class):
    custom_signal = pyqtSignal("PyQt_PyObject")

    def __init__(self):
        super().__init__()

        QtCore.QCoreApplication.processEvents()

        self.setupUi(self)

        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        self.write_data = [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA]

        self.temp_list = []

        self.flow = False

        self.write_txt = ''
        self.write_txt_ascii = ''

        self.c_can_bus = None
        self.p_can_bus = None
        self.bus_flag = False

        self.diag_btn_text = None
        self.diag_success_byte = None
        self.diag_failure_byte = "7f"
        self.drv_state = False
        self.test_mode_basic = False

        self.flow_control_len = 0

        self.hvac_worker = worker.Hvac(parent=self)

        self.btn_drv_state.clicked.connect(self.set_drv_state)

        self.power_train_worker = worker.PowerTrain(parent=self)

        # Default value of Gear radio button
        self.btn_gear_n.setChecked(True)

        self.bcm_state_worker = worker.BCMState(parent=self)

        # Default value of Power mode radio button
        self.btn_acc.setChecked(True)

        self.swrc_worker = worker.Swrc(parent=self)

        self.btn_ok.clicked.connect(self.swrc_worker.thread_func)
        self.btn_left.pressed.connect(self.swrc_worker.thread_func)
        self.btn_right.clicked.connect(self.swrc_worker.thread_func)
        self.btn_undo.clicked.connect(self.swrc_worker.thread_func)
        self.btn_mode.clicked.connect(self.swrc_worker.thread_func)
        self.btn_mute.clicked.connect(self.swrc_worker.thread_func)

        self.btn_call.clicked.connect(self.swrc_worker.thread_func)
        self.btn_vol_up.released.connect(self.swrc_worker.thread_func)
        self.btn_vol_down.released.connect(self.swrc_worker.thread_func)

        self.speed_worker = worker.TachoSpeed(parent=self)

        self.btn_ota_cond.clicked.connect(self.set_ota_cond)

        self.tire_worker = worker.TirePressure(parent=self)

        self.btn_tpms_success.clicked.connect(self.tire_worker.thread_func)
        self.btn_tpms_fail.clicked.connect(self.tire_worker.thread_func)

        self.btn_bright_afternoon.setChecked(True)

        self.aeb_worker = worker.AEB(parent=self)

        self.bcm_mmi_worker = worker.BCMMMI(parent=self)

        self.btn_mscs_ok.setChecked(True)

        self.btn_mscs_ok.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_CmnFail.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_NotEdgePress.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_EdgeSho.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_SnsrFltT.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_FltPwrSplyErr.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_FltSwtHiSide.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_SigFailr.clicked.connect(self.bcm_mmi_worker.thread_func)

        self.acu_worker = worker.ACU(parent=self)

        self.chkbox_drv_invalid.stateChanged.connect(self.acu_worker.drv_invalid)
        self.chkbox_pass_invalid.stateChanged.connect(self.acu_worker.pass_invalid)

        self.battery_worker = worker.BatteryManage(parent=self)
        self.charge_worker = worker.ChargingState(parent=self)

        self.tester_worker = worker.TesterPresent(parent=self)

        self.thread_worker = worker.ThreadWorker(parent=self)

        self.tx_worker = worker.TxOnlyWorker(parent=self)

        self.tx_worker.sig2.connect(self.sig2)

        self.btn_sess_default.clicked.connect(self.diag_func)
        self.btn_sess_extended.clicked.connect(self.diag_func)
        self.btn_sess_nrc_12.clicked.connect(self.diag_func)
        self.btn_sess_nrc_13.clicked.connect(self.diag_func)

        self.btn_diag_reset_basic.released.connect(self.set_diag_basic_btns_enable)

        self.btn_reset_sw.clicked.connect(self.diag_func)
        self.btn_reset_hw.clicked.connect(self.diag_func)
        self.btn_reset_nrc_12.clicked.connect(self.diag_func)
        self.btn_reset_nrc_13.clicked.connect(self.diag_func)
        self.btn_reset_nrc_7f_sw.clicked.connect(self.diag_func)
        self.btn_reset_nrc_7f_hw.clicked.connect(self.diag_func)
        self.btn_reset_nrc_22_sw.clicked.connect(self.diag_func)
        self.btn_reset_nrc_22_hw.clicked.connect(self.diag_func)

        self.btn_tester.released.connect(self.diag_func)

        self.btn_sec_req_seed.released.connect(self.diag_func)
        self.btn_sec_send_key.released.connect(self.diag_func)

        self.btn_write_vin.clicked.connect(self.diag_func)

        self.btn_mem_fault_num_check.clicked.connect(self.diag_func)
        self.btn_mem_fault_list_check.clicked.connect(self.diag_func)
        self.btn_mem_fault_reset.clicked.connect(self.diag_func)

        # self.clear_console.clicked.connect(self.diag_text_clear)

        self.btn_bus_connect.clicked.connect(self.bus_connect)

        self.btn_bus_start.clicked.connect(self.thread_start)
        self.btn_bus_stop.clicked.connect(self.thread_stop)

        self.btn_write_data_convert.clicked.connect(self.vin_ascii_convert)

        self.btn_main_console_clear.clicked.connect(self.console_text_clear)
        self.btn_diag_console_clear.clicked.connect(self.console_text_clear)
        self.btn_write_data_clear.clicked.connect(self.console_text_clear)

        # self.btn_diag_reset_1.clicked.connect(self.set_diag_btns_enable)
        # self.btn_diag_reset_2.clicked.connect(self.set_diag_btns_enable)

        self.set_can_basic_btns_enable(False)
        self.set_diag_basic_btns_enable(False)
        self.set_diag_did_btns_enable(False)
        self.set_diag_secu_btns_enable(False)
        self.set_diag_write_btns_enable(False)
        self.set_diag_comm_control_btns_enable(False)

    def bus_connect(self):
        if not self.bus_flag:
            try:
                temp1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
                self.bus_console.appendPlainText("1 Channel is connected")
                try:
                    temp2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')
                    if temp1.recv(1):
                        self.c_can_bus = temp1
                        self.p_can_bus = temp2
                    else:
                        self.c_can_bus = temp2
                        self.p_can_bus = temp1
                    self.bus_console.appendPlainText("2 Channel is connected")
                except:
                    if temp1.recv(1):
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
        time.sleep(0.5)
        if self.bus_flag:
            self.thread_worker.start()
            self.tx_worker.start()
            self.hvac_worker.start()
            self.swrc_worker.start()
            self.power_train_worker.start()
            self.bcm_state_worker.start()
            self.speed_worker.start()
            self.tire_worker.start()
            self.aeb_worker.start()
            self.bcm_mmi_worker.start()
            self.acu_worker.start()
            self.tester_worker.start()

            self.battery_worker.start()
            self.charge_worker.start()

            self.thread_worker._isRunning = True
            self.tx_worker._isRunning = True
            self.hvac_worker._isRunning = True
            self.swrc_worker._isRunning = True
            self.power_train_worker._isRunning = True
            self.bcm_state_worker._isRunning = True
            self.speed_worker._isRunning = True
            self.tire_worker._isRunning = True
            self.aeb_worker._isRunning = True
            self.bcm_mmi_worker._isRunning = True
            self.acu_worker._isRunning = True
            self.tester_worker._isRunning = True

            self.battery_worker._isRunning = True
            self.charge_worker._isRunning = True

            self.set_can_basic_btns_enable(True)
            self.set_diag_basic_btns_enable(True)
            self.set_diag_did_btns_enable(True)
            self.set_diag_secu_btns_enable(True)
            self.set_diag_write_btns_enable(True)
            self.set_diag_comm_control_btns_enable(True)

            QtCore.QCoreApplication.processEvents()
        else:
            self.bus_console.appendPlainText("Can bus is not connected")

    def thread_stop(self):
        self.thread_worker.stop()
        self.tx_worker.stop()
        self.hvac_worker.stop()
        self.swrc_worker.stop()
        self.power_train_worker.stop()
        self.bcm_state_worker.stop()
        self.speed_worker.stop()
        self.tire_worker.stop()
        self.aeb_worker.stop()
        self.bcm_mmi_worker.stop()
        self.acu_worker.stop()
        self.tester_worker.stop()
        self.battery_worker.stop()
        self.charge_worker.stop()

        self.thread_worker.quit()
        self.tx_worker.quit()
        self.hvac_worker.quit()
        self.swrc_worker.quit()
        self.power_train_worker.quit()
        self.bcm_state_worker.quit()
        self.speed_worker.quit()
        self.tire_worker.quit()
        self.aeb_worker.quit()
        self.bcm_mmi_worker.quit()
        self.acu_worker.quit()
        self.tester_worker.quit()
        self.battery_worker.quit()
        self.charge_worker.quit()

        self.set_can_basic_btns_enable(False)
        self.set_diag_basic_btns_enable(False)
        self.set_diag_did_btns_enable(False)
        self.set_diag_secu_btns_enable(False)
        self.set_diag_write_btns_enable(False)
        self.set_diag_comm_control_btns_enable(False)

    def set_drv_state(self):
        if self.btn_drv_state.text() == 'Set Driving State' or self.thread_worker.drv_state:
            self.btn_gear_d.setChecked(True)
            self.btn_start.setChecked(True)
            self.chkbox_pt_ready.setChecked(True)
        else:
            self.btn_gear_n.setChecked(True)
            self.btn_ign.setChecked(True)
            self.chkbox_pt_ready.setChecked(False)

    def set_ota_cond(self):
        if self.btn_ota_cond.text() == 'On OTA Condition':
            self.chkbox_h_brake.setChecked(False)
        else:
            self.btn_gear_n.setChecked(True)
            self.chkbox_h_brake.setChecked(True)

    def set_can_basic_btns_enable(self, flag):
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

    def set_diag_basic_btns_enable(self, flag=True):
        # **need to add reset btns
        if flag:
            color = "black"
        else:
            color = "gray"

        self.btn_sess_default.setEnabled(flag)
        self.label_sess_default.setStyleSheet(f"color: {color}")
        self.btn_sess_extended.setEnabled(flag)
        self.label_sess_extended.setStyleSheet(f"color: {color}")

        self.btn_sess_nrc_12.setEnabled(flag)
        self.label_sess_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_sess_nrc_13.setEnabled(flag)
        self.label_sess_nrc_13.setStyleSheet(f"color: {color}")

        self.btn_tester.setEnabled(flag)
        self.label_tester.setStyleSheet(f"color: {color}")
        self.chkbox_tester_present.setEnabled(flag)

        self.btn_tester_nrc_12.setEnabled(flag)
        self.label_tester_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_tester_nrc_13.setEnabled(flag)
        self.label_tester_nrc_13.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_basic.setEnabled(flag)
        self.chkbox_diag_test_mode_basic.setEnabled(flag)

    def set_diag_did_btns_enable(self, flag=True):
        if flag:
            color = "black"
        else:
            color = "gray"

        self.btn_id_ecu_num.setEnabled(flag)
        self.label_id_ecu_num.setStyleSheet(f"color: {color}")
        self.btn_id_ecu_supp.setEnabled(flag)
        self.label_id_ecu_supp.setStyleSheet(f"color: {color}")
        self.btn_id_vin.setEnabled(flag)
        self.label_id_vin.setStyleSheet(f"color: {color}")
        self.btn_id_install_date.setEnabled(flag)
        self.label_id_install_date.setStyleSheet(f"color: {color}")
        self.btn_id_diag_ver.setEnabled(flag)
        self.label_id_diag_ver.setStyleSheet(f"color: {color}")
        self.btn_id_sys_name.setEnabled(flag)
        self.label_id_sys_name.setStyleSheet(f"color: {color}")
        self.btn_id_active_sess.setEnabled(flag)
        self.label_id_active_sess.setStyleSheet(f"color: {color}")
        self.btn_id_veh_name.setEnabled(flag)
        self.label_id_veh_name.setStyleSheet(f"color: {color}")
        self.btn_id_ecu_serial.setEnabled(flag)
        self.label_id_ecu_serial.setStyleSheet(f"color: {color}")
        self.btn_id_hw_ver.setEnabled(flag)
        self.label_id_hw_ver.setStyleSheet(f"color: {color}")
        self.btn_id_sw_ver.setEnabled(flag)
        self.label_id_sw_ver.setStyleSheet(f"color: {color}")
        self.btn_id_ecu_manu_date.setEnabled(flag)
        self.label_id_ecu_manu_date.setStyleSheet(f"color: {color}")
        self.btn_id_assy_num.setEnabled(flag)
        self.label_id_assy_num.setStyleSheet(f"color: {color}")
        self.btn_id_net_config.setEnabled(flag)
        self.label_id_net_config.setStyleSheet(f"color: {color}")

        self.btn_id_nrc_13.setEnabled(flag)
        self.label_id_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_id_nrc_31.setEnabled(flag)
        self.label_id_nrc_31.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_did.setEnabled(flag)
        self.chkbox_diag_test_mode_did.setEnabled(flag)

    def set_diag_secu_btns_enable(self, flag=True):
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

    def set_diag_write_btns_enable(self, flag=True):
        if flag:
            color = "black"
        else:
            color = "gray"

        self.lineEdit_write_data.setEnabled(flag)
        self.btn_write_data_clear.setEnabled(flag)
        self.btn_write_data_convert.setEnabled(flag)
        self.label_flag_convert.setStyleSheet(f"color: {color}")

        self.btn_write_vin.setEnabled(flag)
        self.label_write_vin.setStyleSheet(f"color: {color}")
        self.btn_write_install_date.setEnabled(flag)
        self.label_write_install_date.setStyleSheet(f"color: {color}")
        self.btn_write_veh_name.setEnabled(flag)
        self.label_write_veh_name.setStyleSheet(f"color: {color}")
        self.btn_write_sys_name.setEnabled(flag)
        self.label_write_sys_name.setStyleSheet(f"color: {color}")
        self.btn_write_net_config.setEnabled(flag)
        self.label_write_net_config.setStyleSheet(f"color: {color}")

        self.btn_write_nrc_7f_vin.setEnabled(flag)
        self.label_write_nrc_7f_vin.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_7f_install_date.setEnabled(flag)
        self.label_write_nrc_7f_install_date.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_7f_veh_name.setEnabled(flag)
        self.label_write_nrc_7f_veh_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_7f_sys_name.setEnabled(flag)
        self.label_write_nrc_7f_sys_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_7f_net_config.setEnabled(flag)
        self.label_write_nrc_7f_net_config.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_vin.setEnabled(flag)
        self.label_write_nrc_33_vin.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_install_date.setEnabled(flag)
        self.label_write_nrc_33_install_date.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_veh_name.setEnabled(flag)
        self.label_write_nrc_33_veh_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_sys_name.setEnabled(flag)
        self.label_write_nrc_33_sys_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_33_net_config.setEnabled(flag)
        self.label_write_nrc_33_net_config.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_vin.setEnabled(flag)
        self.label_write_nrc_22_vin.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_install_date.setEnabled(flag)
        self.label_write_nrc_22_install_date.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_veh_name.setEnabled(flag)
        self.label_write_nrc_22_veh_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_sys_name.setEnabled(flag)
        self.label_write_nrc_22_sys_name.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_22_net_config.setEnabled(flag)
        self.label_write_nrc_22_net_config.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_13.setEnabled(flag)
        self.label_write_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_write_nrc_31.setEnabled(flag)
        self.label_write_nrc_31.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_write.setEnabled(flag)
        self.chkbox_diag_test_mode_write.setEnabled(flag)

    def set_diag_comm_control_btns_enable(self, flag=True):
        if flag:
            color = "black"
        else:
            color = "gray"

        self.btn_comm_cont_all_en.setEnabled(flag)
        self.label_comm_cont_all_en.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_tx_dis.setEnabled(flag)
        self.label_comm_cont_tx_dis.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_all_dis.setEnabled(flag)
        self.label_comm_cont_all_dis.setStyleSheet(f"color: {color}")

        self.btn_comm_cont_nrc_12.setEnabled(flag)
        self.label_comm_cont_nrc_12.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_13.setEnabled(flag)
        self.label_comm_cont_nrc_13.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_31.setEnabled(flag)
        self.label_comm_cont_nrc_31.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_7f_all_en.setEnabled(flag)
        self.label_comm_cont_nrc_7f_all_en.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_7f_tx_dis.setEnabled(flag)
        self.label_comm_cont_nrc_7f_tx_dis.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_7f_all_dis.setEnabled(flag)
        self.label_comm_cont_nrc_7f_all_dis.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_22_all_en.setEnabled(flag)
        self.label_comm_cont_nrc_22_all_en.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_22_tx_dis.setEnabled(flag)
        self.label_comm_cont_nrc_22_tx_dis.setStyleSheet(f"color: {color}")
        self.btn_comm_cont_nrc_22_all_dis.setEnabled(flag)
        self.label_comm_cont_nrc_22_all_dis.setStyleSheet(f"color: {color}")

        self.btn_diag_reset_comm_cont.setEnabled(flag)
        self.chkbox_diag_test_mode_comm_cont.setEnabled(flag)

    def set_diag_mem_fault_btns_enable(self, flag=True):
        self.btn_mem_fault_num_check.setEnabled(flag)
        self.btn_mem_fault_list_check.setEnabled(flag)
        self.btn_mem_fault_reset.setEnabled(flag)

    def console_text_clear(self, txt=None):
        if self.sender().objectName() == "btn_main_console_clear":
            self.main_console.clear()
        elif self.sender().objectName() == "btn_diag_console_clear":
            self.diag_console.clear()
        elif self.sender().objectName() == "btn_write_data_clear" or txt:
            self.label_flag_convert.setText("Fill the data")
            self.lineEdit_write_data.clear()

    def vin_ascii_convert(self):
        self.write_txt = self.lineEdit_write_data.text()
        txt_len = len(self.write_txt)
        if txt_len > 0:
            while self.write_txt[0] == ' ' or self.write_txt[txt_len-1] == ' ':
                if self.write_txt[0] == ' ':
                    self.write_txt = self.write_txt[1:]
                if self.write_txt[txt_len - 1] == ' ':
                    self.write_txt = self.write_txt[:txt_len-1]
            ascii_li = []
            for i, ch in zip(range(txt_len), self.write_txt):
                # LMPA1KMB7NC002090
                ascii_li.append(int(hex(ord(ch))[2:]))
            self.label_flag_convert.setText(f'Conversion Success - Data : {self.write_txt}, length: {txt_len}')
            self.write_txt_ascii = ascii_li

    def write_data_not_correct(self, txt):
        if txt == "btn_write_vin":
            err = "Length Error"
            message = "Incorrect length of VIN number"
        QMessageBox.warning(self, err, message)
        self.console_text_clear(err)

    @pyqtSlot(list)
    def sig2(self, li):
        self.main_console.appendPlainText(str(li))
        QtCore.QCoreApplication.processEvents()

    def diag_func(self):
        if self.sender():
            self.diag_btn_text = self.sender().objectName()
            if self.diag_btn_text == "btn_sess_default" or self.diag_btn_text == "btn_sess_extended" \
                    or self.diag_btn_text == "btn_sess_nrc_12" or self.diag_btn_text == "btn_sess_nrc_13":
                self.diag_success_byte = "50"
                self.diag_sess(self.diag_btn_text)
            elif self.diag_btn_text == "btn_reset_sw" or self.diag_btn_text == "btn_reset_hw" \
                    or self.diag_btn_text == "btn_reset_nrc_12" or self.diag_btn_text == "btn_reset_nrc_13" \
                    or self.diag_btn_text == "btn_reset_nrc_7f_sw" or self.diag_btn_text == "btn_reset_nrc_7f_hw" \
                    or self.diag_btn_text == "btn_reset_nrc_22_sw" or self.diag_btn_text == "btn_reset_nrc_22_hw":
                self.diag_success_byte = "51"
                self.diag_reset(self.diag_btn_text)
            elif self.diag_btn_text == "btn_tester" \
                    or self.diag_btn_text == "btn_tester_nrc_12" or self.diag_btn_text == "btn_tester_nrc_13":
                self.diag_success_byte = "7e"
                self.diag_tester(self.diag_btn_text)
            elif self.diag_btn_text == "btn_sec_req_seed" or self.diag_btn_text == "btn_sec_send_key":
                self.diag_success_byte = "67"
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
                self.diag_success_byte = "6e"
                self.diag_write(self.diag_btn_text)
            elif self.diag_btn_text == "btn_mem_fault_num_check" or self.diag_btn_text == "btn_mem_fault_list_check":
                self.diag_success_byte = "59"
                self.diag_memory_fault(self.diag_btn_text)
            elif self.diag_btn_text == "btn_mem_fault_reset":
                self.diag_success_byte = "54"
                self.diag_memory_fault(self.diag_btn_text)

    def diag_sess(self, txt):
        self.flow_control_len = 1
        if txt == "btn_sess_default":
            self.data[0] = 0x02
            self.data[1] = 0x10
            self.data[2] = 0x01
        elif txt == "btn_sess_extended":
            self.data[0] = 0x02
            self.data[1] = 0x10
            self.data[2] = 0x03
        elif txt == "btn_sess_nrc_12":
            self.data[0] = 0x02
            self.data[1] = 0x10
            self.data[2] = 0xFF
        elif txt == "btn_sess_nrc_13":
            self.data[0] = 0x03
            self.data[1] = 0x10
            self.data[2] = 0x01
            self.data[3] = 0x01
        count = 0
        while count < self.flow_control_len:
            self.diag_console.appendPlainText("Thread trying to send message")
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            self.c_can_bus.send(message)
            time.sleep(0.2)
            zzz = copy.copy(self.tx_worker.ggg)
            for qqq in zzz:
                if qqq[3] == "18daf141":
                    temp = qqq
                    count += 1
            self.tx_worker.ggg = []
            QtCore.QCoreApplication.processEvents()
        if self.test_mode_basic:
            if temp[9] == self.diag_success_byte:
                if temp[10] == "01":
                    self.btn_sess_default.setEnabled(False)
                    self.label_sess_default.setText("Success")
                elif temp[10] == "03":
                    self.btn_sess_extended.setEnabled(False)
                    self.label_sess_extended.setText("Success")
            else:
                if temp[11] == "12":
                    self.btn_sess_nrc_12.setEnabled(False)
                    self.label_sess_nrc_12.setText("Success")
                elif temp[11] == "13":
                    self.btn_sess_nrc_13.setEnabled(False)
                    self.label_sess_nrc_13.setText("Success")
        self.diag_console.appendPlainText(str(temp))
        # **need to add test failed scenario

    def diag_reset(self, txt):
        if txt == "btn_reset_sw":
            self.diag_sess("btn_sess_extended")
            self.data[0] = 0x02
            self.data[1] = 0x11
            self.data[2] = 0x01
        # elif txt == "btn_sess_extended":
        #     self.data[0] = 0x02
        #     self.data[1] = 0x10
        #     self.data[2] = 0x03
        # elif txt == "btn_sess_nrc_12":
        #     self.data[0] = 0x02
        #     self.data[1] = 0x10
        #     self.data[2] = 0xFF
        # elif txt == "btn_sess_nrc_13":
        #     self.data[0] = 0x03
        #     self.data[1] = 0x10
        #     self.data[2] = 0x01
        #     self.data[3] = 0x01
        # while len(self.diag_list) == 0:
        message = can.Message(arbitration_id=0x18da41f1, data=self.data)
        self.c_can_bus.send(message)
            # try:
            #     self.c_can_bus.send(message)
            # except:
            #     print("aaaa")
            #     time.sleep(0.5)
            #     self.diag_reset(txt)
            # self.diag_console.appendPlainText("Thread trying to send message once more")
            # time.sleep(0.5)
        while len(self.diag_list) == 0:
            time.sleep(0.5)
            QtCore.QCoreApplication.processEvents()
        li_len = len(self.diag_list)
        temp = self.diag_list[li_len - 1]
        if temp[9] == self.diag_success_byte:
            if temp[10] == "01":
                self.btn_reset_sw.setEnabled(False)
                self.label_reset_sw.setText("Success")
            elif temp[10] == "03":
                self.btn_sess_extended.setEnabled(False)
                self.label_sess_extended.setText("Success")
        else:
            if temp[11] == "12":
                self.btn_sess_nrc_12.setEnabled(False)
                self.label_sess_nrc_12.setText("Success")
            elif temp[11] == "13":
                self.btn_sess_nrc_13.setEnabled(False)
                self.label_sess_nrc_13.setText("Success")
        for tt in self.diag_list:
            self.diag_console.appendPlainText(str(tt))
        # need to add test failed scenario
        # self.diag_console.appendPlainText("Test Failed")

    def diag_tester(self, txt):
        self.flow_control_len = 1
        if txt == "btn_tester":
            self.data[0] = 0x02
            self.data[1] = 0x3E
            self.data[2] = 0x00
        elif txt == "btn_tester_nrc_12":
            self.data[0] = 0x02
            self.data[1] = 0x3E
            self.data[2] = 0x03
        elif txt == "btn_tester_nrc_13":
            self.data[0] = 0x03
            self.data[1] = 0x3E
            self.data[2] = 0x00
            self.data[3] = 0x01
        count = 0
        while count < self.flow_control_len:
            self.diag_console.appendPlainText("Thread trying to send message")
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            self.c_can_bus.send(message)
            time.sleep(0.5)
            zzz = copy.copy(self.tx_worker.ggg)
            for qqq in zzz:
                if qqq[3] == "18daf141":
                    temp = qqq
            QtCore.QCoreApplication.processEvents()
        if self.test_mode_basic:
            if temp[9] == self.diag_success_byte:
                if temp[10] == "00":
                    self.btn_tester.setEnabled(False)
                    self.label_tester.setText("Success")
            else:
                if temp[11] == "12":
                    self.btn_tester_nrc_12.setEnabled(False)
                    self.label_tester_nrc_12.setText("Success")
                elif temp[11] == "13":
                    self.btn_tester_nrc_13.setEnabled(False)
                    self.label_tester_nrc_13.setText("Success")
        self.diag_console.appendPlainText(str(temp))
        self.tx_worker.ggg = []
        # **need to add test failed scenario

    def diag_did(self, txt):
        self.flow_control_len = 1
        if self.chkbox_diag_test_mode_did.isChecked():
            test_mode = True
        else:
            test_mode = False
        if txt == "btn_id_ecu_num":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x87
            self.flow_control_len = 4
        elif txt == "btn_id_ecu_supp":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x8A
            self.flow_control_len = 2
        elif txt == "btn_id_vin":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x90
            self.flow_control_len = 3
        elif txt == "btn_id_install_date":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0xA2
        elif txt == "btn_id_diag_ver":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x13
        elif txt == "btn_id_sys_name":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x97
            self.flow_control_len = 2
        elif txt == "btn_id_active_sess":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x86
        elif txt == "btn_id_veh_name":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x12
            self.flow_control_len = 2
        elif txt == "btn_id_ecu_serial":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x8C
            self.flow_control_len = 4
        elif txt == "btn_id_hw_ver":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x93
            self.flow_control_len = 3
        elif txt == "btn_id_sw_ver":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x95
            self.flow_control_len = 3
        elif txt == "btn_id_ecu_manu_date":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x8B
        elif txt == "btn_id_assy_num":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x8E
            self.flow_control_len = 3
        elif txt == "btn_id_net_config":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0xF1
            self.data[3] = 0x10
            self.flow_control_len = 2
        elif txt == "btn_sess_nrc_13":
            self.data[0] = 0x03
            self.data[1] = 0x22
            self.data[2] = 0x01
            self.data[3] = 0x01
            self.data[4] = 0x01
        elif txt == "btn_sess_nrc_31":
            self.data[0] = 0x22
            self.data[1] = 0xFF
            self.data[2] = 0xFF
        temp_li = []
        while len(temp_li) < self.flow_control_len:
            self.diag_console.appendPlainText("Thread trying to send message")
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            self.c_can_bus.send(message)
            time.sleep(0.5)
            zzz = copy.copy(self.tx_worker.ggg)
            for qqq in zzz:
                if qqq[3] == "18daf141":
                    temp_li.append(qqq)
            QtCore.QCoreApplication.processEvents()
        # if test_mode:
        #     if temp[9] == self.diag_success_byte:
        #         if temp[10] == "01":
        #             self.btn_sess_default.setEnabled(False)
        #             self.label_sess_default.setText("Success")
        #         elif temp[10] == "03":
        #             self.btn_sess_extended.setEnabled(False)
        #             self.label_sess_extended.setText("Success")
        #     else:
        #         if temp[11] == "12":
        #             self.btn_sess_nrc_12.setEnabled(False)
        #             self.label_sess_nrc_12.setText("Success")
        #         elif temp[11] == "13":
        #             self.btn_sess_nrc_13.setEnabled(False)
        #             self.label_sess_nrc_13.setText("Success")
        # self.diag_console.appendPlainText(str(temp))
        self.tx_worker.ggg = []
        # **need to add test failed scenario

    def diag_write(self, txt):
        self.flow_control_len = 1
        if self.chkbox_diag_test_mode_write.isChecked():
            test_mode = True
        else:
            test_mode = False
        if txt == "btn_write_vin":
            data_len = len(self.write_txt_ascii)
            if data_len != 17:
                self.write_data_not_correct(txt)
            else:
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
                for i, mess in zip(range(len(temp_li)), temp_li):
                    mess = can.Message(arbitration_id=0x18da41f1, data=self.data)
                    self.c_can_bus.send(mess)
                    if i == 0:
                        time.sleep(0.030)

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

    def diag_memory_fault(self, txt=None):
        self.flow_control_len = 1
        rrrr = []
        temp_li = []
        bb = []
        flag = False
        if txt == "btn_mem_fault_num_check":
            self.data[0] = 0x03
            self.data[1] = 0x19
            self.data[2] = 0x01
            self.data[3] = 0x09
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            count = 0
            while count < self.flow_control_len:
                self.diag_console.appendPlainText("Thread trying to send message")
                self.c_can_bus.send(message)
                time.sleep(0.2)
                zzz = copy.copy(self.tx_worker.ggg)
                for qqq in zzz:
                    if qqq[9] == self.diag_success_byte and qqq[10] == '01':
                        self.diag_console.appendPlainText(str(qqq))
                        count += 1
                self.tx_worker.ggg = []
                QtCore.QCoreApplication.processEvents()
        elif txt == "btn_mem_fault_list_check":
            self.data[0] = 0x03
            self.data[1] = 0x19
            self.data[2] = 0x02
            self.data[3] = 0x09
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            count = 0
            while count < self.flow_control_len:
                self.diag_console.appendPlainText("Thread trying to send message")
                self.c_can_bus.send(message)
                time.sleep(0.2)
                zzz = copy.copy(self.tx_worker.ggg)
                for qqq in zzz:
                    if qqq[8] == "10":
                        count = int(int(qqq[9], 16) / 7) + 1
                        self.diag_console.appendPlainText(str(qqq))
                self.tx_worker.ggg = []
                QtCore.QCoreApplication.processEvents()
            self.flow_control_len = count

            while len(temp_li) < self.flow_control_len:
                self.data[0] = 0x03
                self.data[1] = 0x19
                self.data[2] = 0x02
                self.data[3] = 0x09
                message = can.Message(arbitration_id=0x18da41f1, data=self.data)
                self.c_can_bus.send(message)
                time.sleep(0.020)
                self.data[0] = 0x30
                self.data[1] = 0x00
                self.data[2] = 0x00
                self.data[3] = 0xFF
                message = can.Message(arbitration_id=0x18da41f1, data=self.data)
                self.c_can_bus.send(message)
                time.sleep(0.3)
                zzz = copy.copy(self.tx_worker.ggg)
                if flag:
                    for qqq in zzz:
                        if qqq[8] == '03':
                            continue
                        for q in bb:
                            uni = bb | {qqq[8]}
                            if bb != uni:
                                bb.add(qqq[8])
                                temp_li.append(qqq)
                                break
                else:
                    # if len(zzz) != 0:
                    for qqq in zzz:
                        if qqq[8] == '03':
                            continue
                        bb.append(qqq[8])
                        temp_li.append(qqq)
                    bb = set(bb)
                    flag = True
                self.tx_worker.ggg = []
                QtCore.QCoreApplication.processEvents()
            for i in range(self.flow_control_len):
                for j in range(self.flow_control_len):
                    a = int(temp_li[j][8][-1], 16)
                    if i == a:
                        self.diag_console.appendPlainText(str(temp_li[j]))
                        rrrr.append(temp_li[j])
                        break
            print(rrrr)
        elif txt == "btn_mem_fault_reset":
            self.data[0] = 0x04
            self.data[1] = 0x14
            self.data[2] = 0xFF
            self.data[3] = 0xFF
            self.data[4] = 0xFF
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            self.c_can_bus.send(message)
            count = 0
            while count < self.flow_control_len:
                self.diag_console.appendPlainText("Thread trying to send message")
                self.c_can_bus.send(message)
                time.sleep(0.2)
                zzz = copy.copy(self.tx_worker.ggg)
                for qqq in zzz:
                    if qqq[9] == self.diag_success_byte:
                        self.diag_console.appendPlainText(str(qqq))
                        count += 1
                self.tx_worker.ggg = []
                QtCore.QCoreApplication.processEvents()
        # for zz in temp_li:
            # print(zz)
            # self.diag_console.appendPlainText(str(zz))
        # self.data[4] = 0x00
        # self.data[5] = 0x00
        # self.data[6] = 0x00
        # self.data[7] = 0x00
        # li_len = len(self.diag_list)
        # temp = self.diag_list[li_len - 1]
        # if temp[8] == "10":
        #     print("aaaaa")
        # self.diag_console_mem.appendPlainText("Flow Control")
        # self.diag_console.appendPlainText(str)
                # self.diag_console.appendPlainText(str(qqq))
                # QtCore.QCoreApplication.processEvents()
        # message = can.Message(arbitration_id=0x18da41f1, data=self.data)
        # self.c_can_bus.send(message)
        # QtCore.QCoreApplication.processEvents()
        # time.sleep(2)
        # print(self.diag_list)
        # for tt in self.diag_list:
        #     self.diag_console_mem.appendPlainText(str(tt))

        # while len(self.temp_list) == 0:
        #     self.c_can_bus.send(message)
        #     self.diag_console.appendPlainText("Thread trying to send message once more")
        #     QtCore.QCoreApplication.processEvents()
        # li_len = len(self.temp_list)
        # temp = self.temp_list[li_len-1]
        # print(temp)

        #     message = can.Message(arbitration_id=0x18da41f1, data=self.data)
        #     self.c_can_bus.send(message)

    def diag_security_access(self, txt=None):
        self.flow_control_len = 1
        if txt == "btn_sec_req_seed":
            self.diag_sess("btn_sess_extended")
            time.sleep(0.2)
            self.data[0] = 0x02
            self.data[1] = 0x27
            self.data[2] = 0x01
            count = 0
            while count < self.flow_control_len:
                self.diag_console.appendPlainText("Thread trying to send message")
                message = can.Message(arbitration_id=0x18da41f1, data=self.data)
                self.c_can_bus.send(message)
                time.sleep(0.3)
                zzz = copy.copy(self.tx_worker.ggg)
                for qqq in zzz:
                    if qqq[3] == "18daf141":
                        temp = qqq
                        count += 1
                self.tx_worker.ggg = []
                QtCore.QCoreApplication.processEvents()
            self.diag_console.appendPlainText(str(temp))
            self.req_seed = temp[11:15]
        elif txt == "btn_sec_send_key":
            count = 0
            while count < self.flow_control_len:
                self.diag_console.appendPlainText("Thread trying to send message")
                self.diag_security_access("btn_sec_req_seed")
                time.sleep(0.2)
                good = algo.secu_algo(self.req_seed)
                self.data[0] = 0x06
                self.data[1] = 0x27
                self.data[2] = 0x02
                self.data[3] = good[0]
                self.data[4] = good[1]
                self.data[5] = good[2]
                self.data[6] = good[3]
                message = can.Message(arbitration_id=0x18da41f1, data=self.data)
                self.c_can_bus.send(message)
                time.sleep(0.5)
                zzz = copy.copy(self.tx_worker.ggg)
                for qqq in zzz:
                    if qqq[3] == "18daf141":
                        temp = qqq
                        count += 1
                self.tx_worker.ggg = []
                QtCore.QCoreApplication.processEvents()
            self.diag_console.appendPlainText(str(temp))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Main()
    mywindow.show()
    sys.exit(app.exec_())
    # app.exec_()
