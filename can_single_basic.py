import os
import sys
import can
import time
from datetime import datetime
import data_identifier as data_id
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from can import interfaces
import can.interfaces.vector
import can_thread as worker
import pyqtgraph as pg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Ui_MainWindow, QtBaseClass = pg.Qt.loadUiType(BASE_DIR + r"./src/can_basic_ui.ui")
# Ui_MainWindow, QtBaseClass = uic.loadUiType(BASE_DIR + r"./src/master_ui.ui")


class Main(QMainWindow, Ui_MainWindow):
    custom_signal = pyqtSignal("PyQt_PyObject")

    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.graph_data_list = []

        self.log_data = []

        self.tx_chronicle = False
        self.recv_flag = False

        self.c_can_bus = None
        self.c_can_name = ''
        self.p_can_bus = None
        self.bus_flag = False

        self.drv_state = False
        self.test_mode_basic = False

        self.tx_set = set()

        self.pms_s_hvsm_worker = worker.PMS_S_HVSM(parent=self)
        self.pms_s_hvsm_worker.pms_s_hvsm_signal.connect(self.can_signal_sender)

        self.pms_c_strwhl_worker = worker.PMS_C_StrWhl(parent=self)
        self.pms_c_strwhl_worker.pms_c_strwhl_signal.connect(self.can_signal_sender)

        self.pms_bodycont_c_worker = worker.PMS_BodyCont_C(parent=self)
        self.pms_bodycont_c_worker.pms_bodycont_c_signal.connect(self.can_signal_sender)

        self.pms_ptinfo_worker = worker.PMS_PTInfo(parent=self)
        self.pms_ptinfo_worker.pms_ptinfo_signal.connect(self.can_signal_sender)

        self.btn_drv_state.clicked.connect(self.set_drv_state)

        # Default value of Power mode radio button
        self.btn_acc.setChecked(True)

        self.bcm_mmi_worker = worker.BCM_MMI(parent=self)
        self.bcm_mmi_worker.bcm_mmi_signal.connect(self.can_signal_sender)

        # Default value of Gear radio button
        self.btn_gear_n.setChecked(True)

        self.bcm_swrc_worker = worker.BCM_SWRC(parent=self)
        self.bcm_swrc_worker.bcm_swrc_signal.connect(self.can_signal_sender)

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

        self.bcm_strwhl_heat_worker = worker.BCM_StrWhl_Heat(parent=self)
        self.bcm_strwhl_heat_worker.bcm_strwhl_heat_signal.connect(self.can_signal_sender)

        self.bcm_lightchime_worker = worker.BCM_LightChime(parent=self)
        self.bcm_lightchime_worker.bcm_lightchime_signal.connect(self.can_signal_sender)

        self.bcm_stateupdate_worker = worker.BCM_StateUpdate(parent=self)
        self.bcm_stateupdate_worker.bcm_stateupdate_signal.connect(self.can_signal_sender)

        self.ic_tachospeed_worker = worker.IC_TachoSpeed(parent=self)
        self.ic_tachospeed_worker.ic_tachospeed_signal.connect(self.can_signal_sender)

        self.ic_distance_worker = worker.IC_Distance(parent=self)
        self.ic_distance_worker.ic_distance_signal.connect(self.can_signal_sender)

        self.btn_ota_cond.clicked.connect(self.set_ota_cond)

        self.esc_tpms_worker = worker.ESC_TPMS(parent=self)
        self.esc_tpms_worker.esc_tpms_signal.connect(self.can_signal_sender)

        self.btn_tpms_success.clicked.connect(self.esc_tpms_worker.thread_func)
        self.btn_tpms_fail.clicked.connect(self.esc_tpms_worker.thread_func)

        self.btn_bright_afternoon.setChecked(True)

        self.fcs_aeb_worker = worker.FCS_AEB(parent=self)
        self.fcs_aeb_worker.fcs_aeb_signal.connect(self.can_signal_sender)

        self.fcs_ldw_worker = worker.FCS_LDW(parent=self)
        self.fcs_ldw_worker.fcs_ldw_signal.connect(self.can_signal_sender)

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
        self.acu_seatbelt_worker.acu_seatbelt_signal.connect(self.can_signal_sender)

        self.chkbox_drv_invalid.stateChanged.connect(self.acu_seatbelt_worker.drv_invalid)
        self.chkbox_pass_invalid.stateChanged.connect(self.acu_seatbelt_worker.pass_invalid)

        self.pms_bodycont_p_worker = worker.PMS_BodyCont_P(parent=self)
        self.pms_bodycont_p_worker.pms_bodycont_p_signal.connect(self.can_signal_sender)

        self.pms_vri_worker = worker.PMS_VRI(parent=self)
        self.pms_vri_worker.pms_vri_signal.connect(self.can_signal_sender)

        self.bms_batt_worker = worker.BMS_Batt(parent=self)
        self.bms_batt_worker.bms_batt_signal.connect(self.can_signal_sender)

        self.bms_charge_worker = worker.BMS_Charge(parent=self)
        self.bms_charge_worker.bms_charge_signal.connect(self.can_signal_sender)

        self.mcu_motor_worker = worker.MCU_Motor(parent=self)
        self.mcu_motor_worker.mcu_motor_signal.connect(self.can_signal_sender)

        self.thread_worker = worker.ThreadWorker(parent=self)
        self.thread_worker.signal_presenter.connect(self.signal_presenter)

        self.btn_bus_connect.clicked.connect(self.bus_connect)

        self.btn_tx_console_clear.clicked.connect(self.console_text_clear)

        self.btn_bus_start.clicked.connect(self.thread_start)
        self.btn_bus_stop.clicked.connect(self.thread_stop)

        self.chkbox_node_acu.released.connect(self.node_acu_control)
        self.chkbox_node_bcm.released.connect(self.node_bcm_control)
        self.chkbox_node_esc.released.connect(self.node_esc_control)
        self.chkbox_node_fcs.released.connect(self.node_fcs_control)
        self.chkbox_node_ic.released.connect(self.node_ic_control)
        self.chkbox_node_pms.released.connect(self.node_pms_control)
        self.chkbox_node_pms_s.released.connect(self.node_pms_s_control)
        self.chkbox_node_pms_c.released.connect(self.node_pms_c_control)
        self.chkbox_node_bms.released.connect(self.node_bms_control)
        self.chkbox_node_mcu.released.connect(self.node_mcu_control)

        self.btn_save_log.released.connect(self.save_log)
        self.chkbox_save_log.released.connect(self.save_log)
        self.chkbox_can_dump.released.connect(self.can_dump_mode)
        # self.comboBox_log_format.addItem(".blf")
        self.comboBox_log_format.addItem(".asc")

        self.item = []
        self.btn_fixed_watch.setChecked(True)
        self.btn_fixed_watch.toggled.connect(self.console_text_clear)
        self.btn_chronicle_watch.toggled.connect(self.console_text_clear)

        self.btn_filter_all.setChecked(True)
        self.btn_filter_all.toggled.connect(self.console_text_clear)
        self.btn_filter_tx.toggled.connect(self.console_text_clear)
        self.btn_filter_rx.toggled.connect(self.console_text_clear)
        self.btn_filter_c_can.toggled.connect(self.console_text_clear)
        self.btn_filter_p_can.toggled.connect(self.console_text_clear)
        self.btn_filter_diag.toggled.connect(self.console_text_clear)

        self.treeWidget_tx.setColumnWidth(0, 130)
        self.treeWidget_tx.setColumnWidth(1, 150)
        self.treeWidget_tx.setColumnWidth(2, 300)
        self.treeWidget_tx.setColumnWidth(4, 350)

        self.comboBox_num.addItem("1")
        self.comboBox_num.addItem("2")
        self.comboBox_num.addItem("3")

        self.graph_widget.showGrid(x=True, y=True)

        self.set_mmi_labels_init(False)
        self.set_general_btns_labels(True)
        self.set_node_btns(True)
        self.set_can_basic_btns_labels(False)

        self.image_initialization()

    def bus_connect(self):
        if not self.bus_flag:
            try:
                temp1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
                self.bus_console.appendPlainText("1 Channel is connected")
                try:
                    temp2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')
                    if temp1.recv(1):
                        self.c_can_bus = temp1
                        self.c_can_name = temp1.channel_info
                        self.p_can_bus = temp2
                    else:
                        self.c_can_bus = temp2
                        self.c_can_name = temp2.channel_info
                        self.p_can_bus = temp1
                    self.bus_console.appendPlainText("2 Channel is connected")
                except:
                    if temp1.recv(1):
                        self.c_can_bus = temp1
                        self.c_can_name = temp1.channel_info
                    else:
                        self.p_can_bus = temp1

                self.bus_flag = True
                self.bus_console.appendPlainText("PEAK-CAN bus is connected")
            except interfaces.pcan.pcan.PcanCanInitializationError as e1:
                print(e1)
                self.bus_console.appendPlainText("PEAK-CAN bus is not connected")
                self.c_can_bus = can.interface.Bus(bustype='vector', channel=0, bitrate='500000')
                self.c_can_name = self.c_can_bus.channel_info
                try:
                    temp_num = 0
                    self.p_can_bus = can.interface.Bus(bustype='vector', channel=1, bitrate='500000')
                    while temp_num < 10000:
                        self.can_signal_sender('p', 0x0cfa01ef, self.data)
                        temp_num += 1
                    self.bus_flag = True
                    self.bus_console.appendPlainText("Vector bus is connected")
                except interfaces.vector.VectorError as e2:
                    print(e2)
                    self.console_text_clear("tx_console_clear")
                    self.bus_flag = True
                    self.p_can_bus = None
                    self.bus_console.appendPlainText("1 Channel is connected")
                except can.exceptions.CanInterfaceNotImplementedError as e3:
                    print(e3)
                    self.bus_console.appendPlainText("CAN device is not connected")
                self.bus_console.appendPlainText("Vector bus is connected")
        else:
            self.bus_console.appendPlainText("CAN bus is already connected")

    def thread_start(self):
        if self.bus_flag:
            self.thread_worker._isRunning = True

            self.node_acu_control()
            self.node_bcm_control()
            self.node_esc_control()
            self.node_fcs_control()
            self.node_ic_control()
            self.node_pms_control()
            self.node_pms_s_control()
            self.node_pms_c_control()
            self.node_bms_control()
            self.node_mcu_control()

            self.thread_worker.start()

            self.set_mmi_labels_init(True)
            self.set_general_btns_labels(True)
            self.set_can_basic_btns_labels(True)

            self.chkbox_can_dump.setEnabled(False)
        else:
            self.bus_console.appendPlainText("Can bus is not connected")

    def thread_stop(self):
        self.set_mmi_labels_init(False)
        self.set_general_btns_labels(False)
        self.set_can_basic_btns_labels(False)

        self.comboBox_log_format.setEnabled(False)

        self.node_acu_control(flag=False)
        self.node_bcm_control(flag=False)
        self.node_esc_control(flag=False)
        self.node_fcs_control(flag=False)
        self.node_ic_control(flag=False)
        self.node_pms_control(flag=False)
        self.node_pms_s_control(flag=False)
        self.node_pms_c_control(flag=False)
        self.node_bms_control(flag=False)
        self.node_mcu_control(flag=False)

        self.thread_worker.stop()

        self.chkbox_can_dump.setEnabled(True)

    def send_message(self, bus, sig_id, send_data):
        if sig_id == 0x18da41f1:
            self.diag_console.appendPlainText("Tester sends the (physical) diagnosis message")
        elif sig_id == 0x18db33f1:
            self.diag_console.appendPlainText("Tester sends the (functional) diagnosis message")
        message = can.Message(timestamp=time.time(), arbitration_id=sig_id, data=send_data, channel=bus)
        if self.chkbox_save_log.isChecked():
            self.log_data.append(message)
        self.thread_worker.signal_emit(message)
        bus.send(message)

    def can_dump_mode(self):
        if self.chkbox_can_dump.isChecked():
            node_flag = False
        else:
            node_flag = True
        self.chkbox_node_acu.setChecked(node_flag)
        self.chkbox_node_acu.setEnabled(node_flag)
        self.chkbox_node_bcm.setChecked(node_flag)
        self.chkbox_node_bcm.setEnabled(node_flag)
        self.chkbox_node_esc.setChecked(node_flag)
        self.chkbox_node_esc.setEnabled(node_flag)
        self.chkbox_node_fcs.setChecked(node_flag)
        self.chkbox_node_fcs.setEnabled(node_flag)
        self.chkbox_node_ic.setChecked(node_flag)
        self.chkbox_node_ic.setEnabled(node_flag)
        self.chkbox_node_pms.setChecked(node_flag)
        self.chkbox_node_pms.setEnabled(node_flag)
        self.chkbox_node_pms_s.setChecked(node_flag)
        self.chkbox_node_pms_s.setEnabled(node_flag)
        self.chkbox_node_pms_c.setChecked(node_flag)
        self.chkbox_node_pms_c.setEnabled(node_flag)
        self.chkbox_node_bms.setChecked(node_flag)
        self.chkbox_node_bms.setEnabled(node_flag)
        self.chkbox_node_mcu.setChecked(node_flag)
        self.chkbox_node_mcu.setEnabled(node_flag)

    def save_log(self):
        if self.sender().objectName() == "btn_save_log":
            if len(self.log_data) > 0:
                # path = QFileDialog.getOpenFileName(self)
                path = QFileDialog.getExistingDirectory(self)
                # print(path)
                if path:
                    if self.chkbox_save_log.isChecked():
                        self.bus_console.appendPlainText("Can Log Writing Stop")
                        self.chkbox_save_log.toggle()
                    self.bus_console.appendPlainText("Can Log saving Start")
                    log_path = path + f"/log{self.comboBox_log_format.currentText()}"
                    # log_dir = path[0]
                    f = open(log_path, 'w')
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
                else:
                    QMessageBox.warning(self, "Log Save", "Set appropriate directory")
            else:
                QMessageBox.warning(self, "Log Save", "Check the Log Save checkbox first")
        elif self.sender().objectName() == "chkbox_save_log":
            if self.chkbox_save_log.isChecked():
                self.bus_console.appendPlainText("Can Log Writing Start")
            else:
                self.bus_console.appendPlainText("Can Log Writing Stop")
                self.comboBox_log_format.setEnabled(True)

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

    def set_mmi_labels_init(self, flag):
        if flag:
            color = "black"
        else:
            color = "gray"

        self.txt_aeb.setStyleSheet(f"color: {color}")
        self.txt_drv_heat.setStyleSheet(f"color: {color}")
        self.txt_drv_vent.setStyleSheet(f"color: {color}")
        self.txt_pass_heat.setStyleSheet(f"color: {color}")
        self.txt_pass_vent.setStyleSheet(f"color: {color}")
        self.txt_side_mani.setStyleSheet(f"color: {color}")
        self.txt_side_heat.setStyleSheet(f"color: {color}")
        self.txt_st_whl_heat.setStyleSheet(f"color: {color}")
        self.txt_light.setStyleSheet(f"color: {color}")

        self.txt_res_aeb.setText("None")
        self.txt_res_aeb.setStyleSheet(f"color: {color}")
        self.txt_res_drv_heat.setText("OFF")
        self.txt_res_drv_heat.setStyleSheet(f"color: {color}")
        self.txt_res_drv_vent.setText("OFF")
        self.txt_res_drv_vent.setStyleSheet(f"color: {color}")
        self.txt_res_pass_heat.setText("OFF")
        self.txt_res_pass_heat.setStyleSheet(f"color: {color}")
        self.txt_res_pass_vent.setText("OFF")
        self.txt_res_pass_vent.setStyleSheet(f"color: {color}")
        self.txt_res_side_mani.setText("None")
        self.txt_res_side_mani.setStyleSheet(f"color: {color}")
        self.txt_res_side_heat.setText("None")
        self.txt_res_side_heat.setStyleSheet(f"color: {color}")
        self.txt_res_st_whl_heat.setText("OFF")
        self.txt_res_st_whl_heat.setStyleSheet(f"color: {color}")
        self.txt_res_light.setText("OFF")
        self.txt_res_light.setStyleSheet(f"color: {color}")

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

    def set_general_btns_labels(self, flag):
        self.chkbox_save_log.setEnabled(flag)
        self.btn_save_log.setEnabled(flag)
        self.chkbox_can_dump.setEnabled(flag)
        self.comboBox_log_format.setEnabled(flag)

    def set_can_basic_btns_labels(self, flag):
        if flag:
            color = "black"
            self.slider_speed.sliderMoved.connect(self.thread_worker.slider_speed_func)
            self.slider_speed.valueChanged.connect(self.thread_worker.slider_speed_func)

            if self.p_can_bus:
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

        self.slider_speed.setEnabled(flag)
        if self.p_can_bus:
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

    def console_text_clear(self, txt=None):
        btn_name = self.sender().objectName()
        if btn_name == "btn_diag_console_clear":
            self.diag_console.clear()
        elif btn_name == "btn_tx_console_clear" or btn_name == "btn_chronicle_watch" or btn_name == "btn_fixed_watch" \
                or btn_name == "btn_filter_all" or btn_name == "btn_filter_tx" or btn_name == "btn_filter_rx" \
                or btn_name == "btn_filter_c_can" or btn_name == "btn_filter_p_can" or btn_name == "btn_filter_diag" \
                or btn_name == "btn_bus_start" or txt == "tx_console_clear":
            self.tx_set = set()
            self.item = []
            self.treeWidget_tx.clear()
        elif btn_name == "btn_write_data_clear" or txt:
            self.label_flag_send.setText("Fill the data")
            self.lineEdit_write_data.clear()
        elif btn_name == "btn_diag_dtc_console_clear":
            self.diag_initialization()

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

    @pyqtSlot(can.Message)
    def signal_presenter(self, tx_single):
        tx_datetime = datetime.fromtimestamp(tx_single.timestamp)
        tx_time = str(tx_datetime)[11:-4]
        tx_id = hex(tx_single.arbitration_id)
        if tx_single.channel:
            if str(tx_single.channel) == self.c_can_name:
                tx_channel = "C-CAN"
            else:
                tx_channel = "P-CAN"
        else:
            tx_channel = "C-CAN"
        tx_message_info = data_id.message_info_by_can_id(tx_single.arbitration_id, tx_channel)
        tx_name = tx_message_info[0]
        tx_data = ''
        for hex_val in tx_single.data:
            tx_data += (hex(hex_val)[2:].upper().zfill(2) + ' ')
        if not self.tx_filter(tx_single.arbitration_id, tx_name, tx_channel):
            return 0
        if self.btn_chronicle_watch.isChecked():
            item = QTreeWidgetItem()
            item.setText(0, tx_id)
            item.setText(1, tx_time)
            item.setText(2, tx_name)
            item.setText(3, tx_channel)
            item.setText(4, tx_data)
            self.treeWidget_tx.addTopLevelItems([item])
            # self.treeWidget_tx.invisibleRootItem().addChild(item)
        elif self.btn_fixed_watch.isChecked():
            len_prev = len(self.tx_set)
            identifier = str(tx_single.arbitration_id) + str(tx_single.channel)
            self.tx_set.add(identifier)
            len_now = len(self.tx_set)
            if len_now - len_prev == 0:
                for item in self.item:
                    if tx_id == item.text(0) and tx_channel == item.text(3):
                        item.setText(1, tx_time)
                        item.setText(4, tx_data)
                        for i, sub_mess in zip(range(item.childCount()), tx_message_info[1:]):
                            item.child(i).setText(4, data_id.data_matcher(tx_single, sub_mess))
                        break
            else:
                item = QTreeWidgetItem()
                item.setText(0, tx_id)
                item.setText(1, tx_time)
                item.setText(2, tx_name)
                item.setText(3, tx_channel)
                item.setText(4, tx_data)
                for sub_message in tx_message_info[1:]:
                    sub_item = QTreeWidgetItem(item)
                    sub_item.setText(2, sub_message["name"])
                    sub_item.setText(4, data_id.data_matcher(tx_single, sub_message))
                self.item.append(item)
                self.treeWidget_tx.addTopLevelItems(self.item)
                self.comboBox_id.addItem(tx_name)
                # self.treeWidget_tx.clear()
        if tx_id == "0x18ffa57f":
            # print(tx_data, type(tx_data))
            if len(self.graph_data_list) == 10:
                self.graph_data_list.pop(0)
            self.graph_data_list.append(int(tx_data[:2], 16))
        self.graph_presenter(self.graph_data_list)

    def graph_presenter(self, graph_list):
        plot_num = self.comboBox_num.currentText()
        # print(plot_num)
        # print(graph_list)
        # x = [1, 2, 3, 4]
        # y = [1, 4, 9, 16]
        # self.curve = self.graph_widget.plot()
        # self.curve.setData(graph_list)

    @pyqtSlot(str, int, list)
    def can_signal_sender(self, bus_mess, send_id, send_data):
        if send_id == 0xFF:
            self.bus_console.appendPlainText(bus_mess)
        else:
            if bus_mess == 'c':
                self.send_message(self.c_can_bus, send_id, send_data)
            elif bus_mess == 'p':
                self.send_message(self.p_can_bus, send_id, send_data)

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

    def tx_filter(self, tx_id, tx_name, tx_channel):
        if self.btn_filter_all.isChecked():
            return True
        elif self.btn_filter_tx.isChecked():
            if tx_name[:3] == "MMI":
                return True
            else:
                return False
        elif self.btn_filter_rx.isChecked():
            if tx_name[:3] != "MMI":
                return True
            else:
                return False
        elif self.btn_filter_c_can.isChecked():
            if tx_channel == "C-CAN":
                return True
            else:
                return False
        elif self.btn_filter_p_can.isChecked():
            if tx_channel == "P-CAN":
                return True
            else:
                return False
        elif self.btn_filter_diag.isChecked():
            if tx_id == 0x18DA41F1 or tx_id == 0x18DAF141 or tx_id == 0x18DB33F1:
                return True
            else:
                return False

    def node_acu_control(self, flag=True):
        if self.chkbox_node_acu.isChecked() and flag:
            self.acu_seatbelt_worker._isRunning = True
            self.acu_seatbelt_worker.start()
        else:
            self.acu_seatbelt_worker.stop()

    def node_bcm_control(self, flag=True):
        if self.chkbox_node_bcm.isChecked() and flag:
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

    def node_esc_control(self, flag=True):
        if self.chkbox_node_esc.isChecked() and flag:
            self.esc_tpms_worker._isRunning = True
            self.esc_tpms_worker.start()
        else:
            self.esc_tpms_worker.stop()

    def node_fcs_control(self, flag=True):
        if self.chkbox_node_fcs.isChecked() and flag:
            self.fcs_aeb_worker._isRunning = True
            self.fcs_ldw_worker._isRunning = True
            self.fcs_aeb_worker.start()
            self.fcs_ldw_worker.start()
        else:
            self.fcs_aeb_worker.stop()
            self.fcs_ldw_worker.stop()

    def node_ic_control(self, flag=True):
        if self.chkbox_node_ic.isChecked() and flag:
            self.ic_distance_worker._isRunning = True
            self.ic_tachospeed_worker._isRunning = True
            self.ic_distance_worker.start()
            self.ic_tachospeed_worker.start()
        else:
            self.ic_distance_worker.stop()
            self.ic_tachospeed_worker.stop()

    def node_pms_control(self, flag=True):
        if self.chkbox_node_pms.isChecked() and flag:
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

    def node_pms_s_control(self, flag=True):
        if self.chkbox_node_pms_s.isChecked() and flag:
            self.pms_s_hvsm_worker.start()
            self.pms_s_hvsm_worker._isRunning = True
        else:
            self.pms_s_hvsm_worker.stop()

    def node_pms_c_control(self, flag=True):
        if self.chkbox_node_pms_c.isChecked() and flag:
            self.pms_c_strwhl_worker._isRunning = True
            self.pms_c_strwhl_worker.start()
        else:
            self.pms_c_strwhl_worker.stop()

    def node_bms_control(self, flag=True):
        if self.chkbox_node_bms.isChecked() and flag:
            self.bms_batt_worker._isRunning = True
            self.bms_charge_worker._isRunning = True
            self.bms_batt_worker.start()
            self.bms_charge_worker.start()
        else:
            self.bms_batt_worker.stop()
            self.bms_charge_worker.stop()

    def node_mcu_control(self, flag=True):
        if self.chkbox_node_mcu.isChecked() and flag:
            self.mcu_motor_worker._isRunning = True
            self.mcu_motor_worker.start()
        else:
            self.mcu_motor_worker.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Main()
    mywindow.show()
    sys.exit(app.exec_())
