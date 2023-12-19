import os
import sys
import can
import time
import serial.tools.list_ports
from datetime import datetime
import security_algorithm as algo
import data_identifier as data_id
import sig_generator as sig_gen
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtCore
from PyQt5.QtGui import *
from can import interfaces
import can.interfaces.vector
import can.interfaces.slcan
import can_thread as worker
import pyqtgraph as pg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Ui_MainWindow, QtBaseClass = pg.Qt.loadUiType(BASE_DIR + r"./src/can_basic_ui.ui")


class Main(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowIcon(QIcon("./src/drimaes_icon.ico"))
        self.setWindowTitle("Main Window for E-51 IVI CAN Simulator")
        self.show()

        self.curve = self.graph_widget.plot()

        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        self.temp_list = []
        self.graph_x_list = []
        self.graph_y_list = []
        self.log_data = []

        self.curve = self.graph_widget.plot()

        self.tx_chronicle = False
        self.recv_flag = False

        self.graphic_sig_flag = False

        self.time_init = None

        self.pre_message = None

        self.diag_tester_id = 0x18da41f1

        self.c_can_bus = None
        self.p_can_bus = None

        self.bus_flag = False

        self.drv_state = False

        self.tx_time_rel = None

        self.tester_present_flag = None

        self.user_filter_obj = None

        self.user_signal_obj = None

        self.serial_selection_obj = None
        self.serial_devices = []

        self.sub_mess_designated = None
        self.sub_data_designated = None

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

        self.btn_ok.pressed.connect(self.btn_press_handler)
        self.btn_ok.released.connect(self.btn_release_handler)
        self.btn_undo.pressed.connect(self.btn_press_handler)
        self.btn_undo.released.connect(self.btn_release_handler)
        self.btn_mode.pressed.connect(self.btn_press_handler)
        self.btn_mode.released.connect(self.btn_release_handler)
        self.btn_mute.pressed.connect(self.btn_press_handler)
        self.btn_mute.released.connect(self.btn_release_handler)
        self.btn_left.pressed.connect(self.btn_press_handler)
        self.btn_left.released.connect(self.btn_release_handler)
        self.btn_right.pressed.connect(self.btn_press_handler)
        self.btn_right.released.connect(self.btn_release_handler)

        self.btn_call.pressed.connect(self.btn_press_handler)
        self.btn_call.released.connect(self.btn_release_handler)
        self.btn_vol_up.pressed.connect(self.btn_press_handler)
        self.btn_vol_up.released.connect(self.btn_release_handler)
        self.btn_vol_down.pressed.connect(self.btn_press_handler)
        self.btn_vol_down.released.connect(self.btn_release_handler)

        # self.btn_reset.pressed.connect(self.btn_press_handler)
        # self.btn_reset.released.connect(self.btn_release_handler)

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

        self.btn_tpms_success.clicked.connect(self.tpms_handler)
        self.btn_tpms_fail.clicked.connect(self.tpms_handler)

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

        self.tester_worker = worker.TesterPresent(parent=self)

        self.user_signal_worker = worker.UserSignal(parent=self)
        self.user_signal_worker.user_defined_signal.connect(self.can_signal_sender)

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
        self.btn_filter_user.toggled.connect(self.console_text_clear)

        self.btn_time_absolute.setChecked(True)
        self.btn_time_absolute.toggled.connect(self.console_text_clear)
        self.btn_time_relative.toggled.connect(self.console_text_clear)
        self.btn_time_delta.toggled.connect(self.console_text_clear)

        self.btn_bus_peak.setChecked(True)

        self.treeWidget_tx.setColumnWidth(0, 120)
        self.treeWidget_tx.setColumnWidth(1, 105)
        self.treeWidget_tx.setColumnWidth(2, 200)
        self.treeWidget_tx.setColumnWidth(4, 170)

        self.comboBox_num.addItem("1")
        self.comboBox_num.addItem("2")
        self.comboBox_num.addItem("3")

        self.comboBox_id.addItem("---Select signal---")
        self.comboBox_id_specific.addItem("---Select signal---")

        self.graph_widget.showGrid(x=True, y=True)

        self.set_mmi_labels_init(False)
        self.set_general_btns_labels(True)
        self.set_node_btns(True)
        self.set_can_basic_btns_labels(False)

        self.pbar_save_log.setValue(0)
        self.pbar_save_log.setVisible(False)

        self.image_initialization()
        self.diag_obj = None
        self.chkbox_diag_console.clicked.connect(self.diag_main)

        self.chkbox_arbitrary_signal_1.clicked.connect(self.user_signal_handler)

        self.btn_bus_canable.clicked.connect(self.serial_selector_handler)
        self.btn_bus_peak.clicked.connect(self.serial_selector_handler)
        self.btn_bus_vector.clicked.connect(self.serial_selector_handler)
        self.selected_ports = []

        self.btn_0th_byte_up.clicked.connect(self.temp_distance)
        self.btn_1st_byte_up.clicked.connect(self.temp_distance)

    def bus_connect(self):
        if not self.bus_flag:
            bus_count = 0
            if self.chkbox_can_dump.isChecked():
                if self.btn_bus_peak.isChecked():
                    try:
                        temp1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
                        self.bus_console.appendPlainText("PEAK-CAN bus is connected")
                        try:
                            temp2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')
                            while bus_count < 1000:
                                bus_count += 1
                                if temp1.recv().arbitration_id == 0x18ffd741:
                                    self.c_can_bus = temp1
                                    self.p_can_bus = temp2
                                    break
                                elif temp1.recv().arbitration_id == 0x0cfa01ef:
                                    self.c_can_bus = temp2
                                    self.p_can_bus = temp1
                                    break
                            self.bus_console.appendPlainText("2 Channel is connected.")
                        except can.interfaces.pcan.pcan.PcanError as e2:
                            print(e2)
                            while bus_count < 1000:
                                bus_count += 1
                                if temp1.recv().arbitration_id == 0x18ffd741:
                                    self.c_can_bus = temp1
                                    break
                                else:
                                    self.p_can_bus = temp1
                            self.bus_console.appendPlainText("1 Channel is connected.")
                        self.bus_connect_success()
                    except ImportError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("PEAK-CAN driver is not installed.")
                    except can.interfaces.pcan.pcan.PcanError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Connect the PEAK-CAN device.")
                elif self.btn_bus_vector.isChecked():
                    try:
                        self.c_can_bus = can.interface.Bus(bustype='vector', channel=0, bitrate='500000')
                        self.bus_console.appendPlainText("Vector bus is connected.")
                        try:
                            self.p_can_bus = can.interface.Bus(bustype='vector', channel=1, bitrate='500000')
                            self.bus_console.appendPlainText("2 Channel is connected.")
                        except interfaces.vector.VectorError as e2:
                            print(e2)
                            self.bus_console.appendPlainText("1 Channel is connected.")
                        self.bus_connect_success()
                    except interfaces.vector.VectorError as e1:
                        print(e1)
                        try:
                            self.p_can_bus = can.interface.Bus(bustype='vector', channel=1, bitrate='500000')
                            self.bus_console.appendPlainText("Vector bus is connected.")
                            self.bus_console.appendPlainText("1 Channel is connected.")
                            self.bus_connect_success()
                        except interfaces.vector.VectorError as e2:
                            print(e2)
                            self.bus_console.appendPlainText("Connect the Vector(CANoe) device.")
                    except ImportError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Vector(CANoe) driver is not installed.")
                elif self.btn_bus_canable.isChecked():
                    try:
                        temp1 = can.interface.Bus(bustype='slcan', channel=self.selected_ports[0], bitrate='500000')
                        self.bus_console.appendPlainText("Serial bus(CANable bus) is connected.")
                        try:
                            temp2 = can.interface.Bus(bustype='slcan', channel=self.selected_ports[1], bitrate='500000')
                            while bus_count < 1000:
                                bus_count += 1
                                if temp1.recv().arbitration_id == 0x18ffd741:
                                    self.c_can_bus = temp1
                                    self.p_can_bus = temp2
                                    break
                                elif temp1.recv().arbitration_id == 0x0cfa01ef:
                                    self.c_can_bus = temp2
                                    self.p_can_bus = temp1
                                    break
                            self.bus_console.appendPlainText("2 Channel is connected.")
                        except IndexError:
                            while bus_count < 1000:
                                bus_count += 1
                                if temp1.recv().arbitration_id == 0x18ffd741:
                                    self.c_can_bus = temp1
                                    break
                                else:
                                    self.p_can_bus = temp1
                            self.bus_console.appendPlainText("1 Channel is connected.")
                        self.bus_connect_success()
                    except serial.serialutil.SerialException:
                        self.bus_console.appendPlainText("Select appropriate serial port.")
                    except IndexError:
                        self.bus_console.appendPlainText("Select the serial port first.")
            else:
                if self.btn_bus_peak.isChecked():
                    try:
                        temp1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
                        self.bus_console.appendPlainText("PEAK-CAN bus is connected")
                        try:
                            temp2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')
                            if temp1.recv(1):
                                self.c_can_bus = temp1
                                self.p_can_bus = temp2
                            else:
                                self.c_can_bus = temp2
                                self.p_can_bus = temp1
                            self.bus_console.appendPlainText("2 Channel is connected")
                        except can.interfaces.pcan.pcan.PcanError:
                            if temp1.recv(1):
                                self.c_can_bus = temp1
                            else:
                                self.p_can_bus = temp1
                            self.bus_console.appendPlainText("1 Channel is connected")
                        self.bus_connect_success()
                    except ImportError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("PEAK-CAN driver is not installed.")
                    except can.interfaces.pcan.pcan.PcanError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Connect the PEAK-CAN device.")
                elif self.btn_bus_vector.isChecked():
                    try:
                        self.c_can_bus = can.interface.Bus(bustype='vector', channel=0, bitrate='500000')
                        try:
                            self.p_can_bus = can.interface.Bus(bustype='vector', channel=1, bitrate='500000')
                            while bus_count < 100:
                                self.can_signal_sender('p', 0x0cfa01ef, self.data)
                                self.console_text_clear("tx_console_clear")
                                bus_count += 1
                            self.bus_connect_success()
                            self.bus_console.appendPlainText("Vector bus is connected")
                        except can.interfaces.vector.exceptions.VectorError as e2:
                            print(e2)
                            self.console_text_clear("tx_console_clear")
                            self.bus_connect_success()
                            self.p_can_bus = None
                            self.bus_console.appendPlainText("1 Channel is connected")
                    except ImportError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Vector(CANoe) driver is not installed.")
                    except can.interfaces.vector.exceptions.VectorError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Connect the Vector device.")
                elif self.btn_bus_canable.isChecked():
                    try:
                        temp1 = can.interface.Bus(bustype='slcan', channel=self.selected_ports[0], bitrate='500000')
                        self.bus_console.appendPlainText("Serial bus(CANable bus) is connected.")
                        try:
                            temp2 = can.interface.Bus(bustype='slcan', channel=self.selected_ports[1], bitrate='500000')
                            if temp1.recv():
                                self.c_can_bus = temp1
                                self.p_can_bus = temp2
                            else:
                                self.c_can_bus = temp2
                                self.p_can_bus = temp1
                            self.bus_console.appendPlainText("2 Channel is connected.")
                        except IndexError:
                            if temp1.recv(1):
                                self.c_can_bus = temp1
                            else:
                                self.p_can_bus = temp1
                            self.bus_console.appendPlainText("1 Channel is connected.")
                        self.bus_connect_success()
                    except serial.serialutil.SerialException:
                        self.bus_console.appendPlainText("Select appropriate serial port.")
                    except IndexError:
                        self.bus_console.appendPlainText("Select the serial port first.")
        else:
            self.bus_console.appendPlainText("CAN bus is already connected.")

    def bus_connect_success(self):
        self.bus_flag = True
        self.btn_bus_peak.setEnabled(False)
        self.btn_bus_vector.setEnabled(False)
        self.btn_bus_canable.setEnabled(False)

    def thread_start(self):
        if self.bus_flag:
            self.thread_worker._isRunning = True
            self.tester_worker._isRunning = True

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
            self.tester_worker.start()

            self.set_mmi_labels_init(True)
            self.set_general_btns_labels(True)
            self.set_can_basic_btns_labels(True)
            if self.diag_obj:
                self.diag_handle(True)

            self.chkbox_can_dump.setEnabled(False)
        else:
            self.bus_console.appendPlainText("CAN bus is not connected")

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
        self.tester_worker.stop()

        self.chkbox_can_dump.setEnabled(True)

        if self.diag_obj:
            self.diag_handle(False)

    def send_message(self, bus_str, sig_id, send_data, time_delta_diff):
        if bus_str == 'c':
            bus = self.c_can_bus
        elif bus_str == 'p':
            bus = self.p_can_bus
        message = can.Message(timestamp=time.time(), arbitration_id=sig_id, data=send_data, channel=bus)
        #message = can.Message(arbitration_id=sig_id, data=send_data, channel=bus)
        if sig_id == 0x18da41f1:
            self.diag_obj.diag_console.appendPlainText(f"{str(message)} (Physical Tester)")
            # print(message)
        elif sig_id == 0x18db33f1:
            self.diag_obj.diag_console.appendPlainText(f"{str(message)} (Functional Tester)")
            # print(message)
        if self.chkbox_save_log.isChecked():
            self.log_data.append(message)
        bus.send(message)
        self.thread_worker.signal_emit(message, bus_str, time_delta_diff)

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
                if path:
                    if self.chkbox_save_log.isChecked():
                        self.bus_console.appendPlainText("Can Log Writing Stop")
                        self.chkbox_save_log.toggle()
                    self.bus_console.appendPlainText("Can Log saving Start")
                    log_path = path + f"/log{self.comboBox_log_format.currentText()}"
                    # log_dir = path[0]
                    f = open(log_path, 'w')
                    count = 0
                    self.pbar_save_log.setVisible(True)
                    while count < len(self.log_data):
                        sig_id = self.log_data[count].arbitration_id
                        if sig_id == 0x18ffd741 or sig_id == 0x18ffd841 or sig_id == 0x0c0ba021 or sig_id == 0x18a9e821 or sig_id == 0x18ff6341 or sig_id == 0x18ff4b41:
                            data = 'tx ' + str(self.log_data[count])
                        else:
                            data = 'rx ' + str(self.log_data[count])
                        f.write(data)
                        f.write('\n')
                        count += 1
                        save_progress = int((count / len(self.log_data)) * 100)
                        self.pbar_save_log.setValue(save_progress)
                        QtCore.QCoreApplication.processEvents()
                    f.close()
                    self.bus_console.appendPlainText("Can Log saving End")
                    QMessageBox.information(self, "Log Save", "CAN Log Saving complete")
                    self.pbar_save_log.setVisible(False)
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

            self.slider_stwhl_angle.sliderMoved.connect(self.thread_worker.slider_stwhl_func)
            self.slider_stwhl_angle.valueChanged.connect(self.thread_worker.slider_stwhl_func)

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
        self.btn_right.setEnabled(flag)
        self.btn_undo.setEnabled(flag)
        self.btn_mode.setEnabled(flag)
        self.btn_mute.setEnabled(flag)

        self.btn_call.setEnabled(flag)
        self.btn_vol_up.setEnabled(flag)
        self.btn_vol_down.setEnabled(flag)

        self.btn_reset.setEnabled(flag)

        self.btn_ota_cond.setEnabled(flag)

        self.chkbox_h_brake.setEnabled(flag)

        self.btn_tpms_success.setEnabled(flag)
        self.btn_tpms_fail.setEnabled(flag)

        self.btn_bright_afternoon.setEnabled(flag)
        self.btn_bright_night.setEnabled(flag)

        self.slider_speed.setEnabled(flag)
        self.slider_stwhl_angle.setEnabled(flag)
        self.slider_battery.setEnabled(flag)
        self.chkbox_charge.setEnabled(flag)
        if self.p_can_bus:
            self.slider_battery.setEnabled(flag)
            self.chkbox_charge.setEnabled(flag)

        self.tick_0_speed.setStyleSheet(f"color: {color}")
        self.tick_120_speed.setStyleSheet(f"color: {color}")
        self.tick_240_speed.setStyleSheet(f"color: {color}")
        self.label_speed.setStyleSheet(f"color: {color}")

        self.tick_0_batt.setStyleSheet(f"color: {color}")
        self.tick_50_batt.setStyleSheet(f"color: {color}")
        self.tick_100_batt.setStyleSheet(f"color: {color}")
        self.label_battery.setStyleSheet(f"color: {color}")

        self.tick_0_stwhl.setStyleSheet(f"color: {color}")
        self.tick_10_stwhl.setStyleSheet(f"color: {color}")
        self.tick_minus_10_stwhl.setStyleSheet(f"color: {color}")

        self.btn_mscs_ok.setEnabled(flag)
        self.btn_mscs_CmnFail.setEnabled(flag)
        self.btn_mscs_NotEdgePress.setEnabled(flag)
        self.btn_mscs_EdgeSho.setEnabled(flag)
        self.btn_mscs_SnsrFltT.setEnabled(flag)
        self.btn_mscs_FltPwrSplyErr.setEnabled(flag)
        self.btn_mscs_FltSwtHiSide.setEnabled(flag)
        self.btn_mscs_SigFailr.setEnabled(flag)

        self.btn_0th_byte_up.setEnabled(False)
        self.btn_1st_byte_up.setEnabled(False)

        self.chkbox_drv_invalid.setEnabled(flag)
        self.chkbox_pass_invalid.setEnabled(flag)

    def console_text_clear(self, txt=None):
        btn_name = self.sender().objectName()
        if btn_name == "btn_diag_console_clear":
            if self.diag_obj:
                self.diag_obj.diag_console.clear()
        elif btn_name == "btn_tx_console_clear" or btn_name == "btn_chronicle_watch" or btn_name == "btn_fixed_watch" \
                or btn_name == "btn_filter_all" or btn_name == "btn_filter_tx" or btn_name == "btn_filter_rx" \
                or btn_name == "btn_filter_c_can" or btn_name == "btn_filter_p_can" or btn_name == "btn_filter_diag" \
                or btn_name == "btn_filter_user" or btn_name == "btn_time_absolute" or btn_name == "btn_time_relative" \
                or btn_name == "btn_time_delta" or btn_name == "btn_bus_start" or txt == "tx_console_clear":
            self.tx_set = set()
            self.item = []
            self.treeWidget_tx.clear()
        elif btn_name == "btn_write_data_clear" or txt:
            if self.diag_obj:
                self.diag_obj.label_flag_send.setText("Fill the data")
                self.diag_obj.lineEdit_write_data.clear()
        elif btn_name == "btn_diag_dtc_console_clear":
            if self.diag_obj:
                self.diag_obj.diag_initialization()

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

    @pyqtSlot(can.Message, str, float)
    def signal_presenter(self, tx_single, bus_num, time_delta_diff):
        tx_time = self.time_mode(tx_single.timestamp, time_delta_diff)
        tx_id = hex(tx_single.arbitration_id)
        if bus_num == 'c':
            tx_channel = "C-CAN"
        elif bus_num == 'p':
            tx_channel = "P-CAN"
        tx_message_info = data_id.message_info_by_can_id(tx_single.arbitration_id, tx_channel)
        tx_name = tx_message_info[0]
        tx_data = ''
        for hex_val in tx_single.data:
            tx_data += (hex(hex_val)[2:].upper().zfill(2) + ' ')
        if not self.tx_filter(tx_single.arbitration_id, tx_name, tx_channel):
            return False
        if self.btn_chronicle_watch.isChecked():
            item = QTreeWidgetItem()
            item.setText(0, tx_id)
            item.setText(1, tx_time)
            item.setText(2, tx_name)
            item.setText(3, tx_channel)
            item.setText(4, tx_data)
            self.treeWidget_tx.addTopLevelItems([item])
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
                        specific_signals = []
                        for i, sub_mess in zip(range(item.childCount()), tx_message_info[1:]):
                            try:
                                sub_data = sub_mess[int(data_id.data_matcher(tx_single, sub_mess))]
                            except KeyError:
                                sub_data = str(data_id.data_matcher(tx_single, sub_mess))
                            item.child(i).setText(4, sub_data)
                            specific_signals.append(sub_mess["name"])
                            if self.sub_mess_designated == sub_mess["name"]:
                                self.sub_data_designated = data_id.data_matcher(tx_single, sub_mess)
                        if self.comboBox_id.currentText() == "---Select signal---":
                            if self.comboBox_id_specific.count() > 1:
                                self.comboBox_id_specific.clear()
                                self.comboBox_id_specific.addItem("---Select signal---")
                        else:
                            if self.comboBox_id.currentText() == tx_name:
                                if self.comboBox_id_specific.count() == 1:
                                    self.comboBox_id_specific.addItems(specific_signals)
                                    self.pre_message = self.comboBox_id.currentText()
                                if self.pre_message != self.comboBox_id.currentText():
                                    self.comboBox_id_specific.clear()
                                    self.comboBox_id_specific.addItem("---Select signal---")
                                    self.comboBox_id_specific.addItems(specific_signals)
                                    self.pre_message = self.comboBox_id.currentText()
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
                    try:
                        sub_item.setText(4, sub_message[int(data_id.data_matcher(tx_single, sub_message))])
                    except KeyError:
                        sub_item.setText(4, str(data_id.data_matcher(tx_single, sub_message)))
                self.item.append(item)
                self.treeWidget_tx.addTopLevelItems(self.item)
                self.comboBox_id.addItem(tx_name)
        if self.comboBox_id.currentText() == tx_name:
            if self.tx_time_rel and self.sub_data_designated:
                if len(self.graph_x_list) == 10:
                    self.graph_x_list.pop(0)
                    self.graph_y_list.pop(0)
                self.graph_x_list.append(float(self.tx_time_rel))

                self.graph_y_list.append(int(self.sub_data_designated))
                # print(int(self.sub_data_designated))

        self.graph_presenter(self.graph_x_list, self.graph_y_list)

        if self.comboBox_id_specific.currentText() != "---Select signal---":
            self.sub_mess_designated = self.comboBox_id_specific.currentText()

    def graph_presenter(self, graph_x_list, graph_y_list):
        self.curve.setData(graph_x_list, graph_y_list)

    @pyqtSlot(str, int, list, float)
    def can_signal_sender(self, bus_mess, send_id, send_data, time_diff_delta):
        if send_id == 0xFF:
            if not self.chkbox_can_dump.isChecked():
                self.bus_console.appendPlainText(bus_mess)
        else:
            self.send_message(bus_mess, send_id, send_data, time_diff_delta)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Enter:
            self.write_data_sender()

    def tpms_handler(self):
        if self.sender().objectName() == "btn_tpms_success":
            self.esc_tpms_worker.tpms_val = 1
        elif self.sender().objectName() == "btn_tpms_fail":
            self.esc_tpms_worker.tpms_val = 2

    def temp_distance(self):
        if self.sender().objectName() == "btn_0th_byte_up":
            self.ic_distance_worker.dist_0_up += 1
        elif self.sender().objectName() == "btn_1st_byte_up":
            self.ic_distance_worker.dist_1_up += 1

    def image_initialization(self):
        self.img_drv_heat_off = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_off.png").scaledToWidth(80)
        self.img_drv_heat_1 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_01_on.png").scaledToWidth(80)
        self.img_drv_heat_2 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_02_on.png").scaledToWidth(80)
        self.img_drv_heat_3 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_03_on.png").scaledToWidth(80)
        self.img_drv_vent_off = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_off.png").scaledToWidth(80)
        self.img_drv_vent_1 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_01_on.png").scaledToWidth(80)
        self.img_drv_vent_2 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_02_on.png").scaledToWidth(80)
        self.img_drv_vent_3 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_03_on.png").scaledToWidth(80)
        self.img_pass_heat_off = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_off.png").scaledToWidth(80)
        self.img_pass_heat_1 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_01_on.png").scaledToWidth(80)
        self.img_pass_heat_2 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_02_on.png").scaledToWidth(80)
        self.img_pass_heat_3 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_03_on.png").scaledToWidth(80)
        self.img_pass_vent_off = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_off.png").scaledToWidth(80)
        self.img_pass_vent_1 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_01_on.png").scaledToWidth(80)
        self.img_pass_vent_2 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_02_on.png").scaledToWidth(80)
        self.img_pass_vent_3 = QPixmap(BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_03_on.png").scaledToWidth(80)

        self.img_side_mani_on = QPixmap(BASE_DIR + r"./src/images/side/btn_navi_sidemirror_normal.png").scaledToWidth(80)
        self.img_side_mani_off = QPixmap(BASE_DIR + r"./src/images/side/btn_navi_sidemirror_fold.png").scaledToWidth(80)
        self.img_side_heat_on = QPixmap(BASE_DIR + r"./src/images/side/sidemirrorheat_on.png").scaledToWidth(80)
        self.img_side_heat_off = QPixmap(BASE_DIR + r"./src/images/side/sidemirrorheat_off.png").scaledToWidth(80)

        self.img_str_whl_heat_off = QPixmap(BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_off.png").scaledToWidth(
            80)
        self.img_str_whl_heat_1 = QPixmap(BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_01_on.png").scaledToWidth(
            80)
        self.img_str_whl_heat_2 = QPixmap(BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_02_on.png").scaledToWidth(
            80)
        self.img_str_whl_heat_3 = QPixmap(BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_03_on.png").scaledToWidth(
            80)

    def tx_filter(self, tx_id, tx_name, tx_channel):
        if self.btn_filter_user.isChecked():
            return self.user_filter_handler(tx_name=tx_name)
        else:
            if self.user_filter_obj:
                self.user_filter_obj.ui_close()
                self.user_filter_obj = None

        if self.user_signal_obj and tx_name[:3] != "MMI":
            self.user_signal_handler(tx_name=tx_name, tx_channel=tx_channel, tx_id=tx_id)

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

    def time_mode(self, tx_timestamp, time_delta_diff):
        if not self.time_init:
            self.time_init = tx_timestamp
        else:
            self.tx_time_rel = '%0.3f' % (tx_timestamp - self.time_init)
        if self.btn_time_absolute.isChecked():
            tx_datetime = datetime.fromtimestamp(tx_timestamp)
            tx_time = str(tx_datetime)[11:-4]
        elif self.btn_time_relative.isChecked():
            tx_time = self.tx_time_rel
        elif self.btn_time_delta.isChecked():
            if self.btn_chronicle_watch.isChecked():
                self.btn_time_relative.setChecked(True)
                tx_time = self.time_mode(tx_timestamp, time_delta_diff)
            else:
                tx_time_f = '%0.3f' % time_delta_diff
                tx_time = str(tx_time_f)
        return tx_time

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

    def btn_press_handler(self):
        self.bcm_swrc_worker.btn_name = self.sender().objectName()

    def btn_release_handler(self):
        self.bcm_swrc_worker.btn_name = False

    def diag_main(self):
        if self.chkbox_diag_console.isChecked():
            self.diag_obj = Diag_Main()
            if self.bus_flag and self.thread_worker._isRunning:
                self.diag_handle(True)
        else:
            self.diag_obj.ui_close()

    def diag_handle(self, flag):
        self.diag_obj.set_diag_basic_btns_labels(flag)
        self.diag_obj.set_diag_did_btns_labels(flag)
        self.diag_obj.set_diag_sec_btns_labels(flag)
        self.diag_obj.set_diag_write_btns_labels(flag)
        self.diag_obj.set_diag_comm_cont_btns_labels(flag)
        self.diag_obj.set_diag_mem_fault_btns_labels(flag)
        self.diag_obj.set_diag_dtc_cont_btns_labels(flag)

    def user_filter_handler(self, tx_name):
        if not self.user_filter_obj:
            self.user_filter_obj = User_Filter()
        if self.user_filter_obj.node_filter(tx_name):
            return True
        else:
            return self.user_filter_obj.user_filter(tx_name)

    def user_signal_handler(self, tx_name=None, tx_channel=None, tx_id=None):
        if not self.chkbox_arbitrary_signal_1.isChecked():
            self.user_signal_obj.ui_close()
            self.user_signal_obj = None
            return 0
        if not self.user_signal_obj:
            self.user_signal_obj = User_Signal()
        if type(tx_name) != bool:
            self.user_signal_obj.user_signal_list(tx_name, tx_channel, tx_id)
        if self.user_signal_obj.chkbox_period.isChecked():
            self.user_signal_obj.lineEdit_period.setEnabled(True)
        else:
            self.user_signal_obj.lineEdit_period.setEnabled(False)

    def serial_selector_handler(self):
        if self.btn_bus_peak.isChecked() or self.btn_bus_vector.isChecked():
            if not self.serial_selection_obj:
                pass
            else:
                self.serial_selection_obj.ui_close()
        else:
            if not self.serial_selection_obj:
                self.serial_selection_obj = Serial_Port_Selection()
                self.serial_selection_obj.search_serial()
            else:
                self.serial_selection_obj.ui_open()


class Diag_Main(QDialog):

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(BASE_DIR + r"./src/can_diagnosis_ui.ui", self)
        self.setWindowTitle("Diagnosic Console for E-51 IVI CAN Simulator")
        self.show()

        if mywindow.c_can_bus:
            self.c_can_bus = mywindow.c_can_bus
        if mywindow.p_can_bus:
            self.p_can_bus = mywindow.p_can_bus

        # print(self.c_can_bus, self.p_can_bus)

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

        mywindow.tester_worker.tester_signal.connect(self.diag_data_collector)
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

        self.btn_diag_console_clear.clicked.connect(mywindow.console_text_clear)
        self.btn_write_data_clear.clicked.connect(mywindow.console_text_clear)
        self.btn_diag_dtc_console_clear.released.connect(mywindow.console_text_clear)

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
        mywindow.send_message('c', self.diag_tester_id, self.data, 0)
        time.sleep(0.030)
        if multi:
            self.data[0] = 0x30
            mywindow.send_message('c', self.diag_tester_id, self.data, 0)
        time.sleep(0.300)
        self.res_data = mywindow.thread_worker.reservoir[:]
        mywindow.thread_worker.reservoir = []
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
        mywindow.console_text_clear(err)

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
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data)
            sig_li = [0x02, 0x11, 0x01]
        elif txt == "btn_reset_nrc_22_hw":
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
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

        mywindow.drv_state = False
        mywindow.set_drv_state()
        mywindow.thread_worker.slider_speed_func(0)

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
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = 'abcdefghijklmnopq'
            self.diag_write("btn_write_vin")
        elif txt == "btn_write_nrc_22_install_date":
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = '12345678'
            self.diag_write("btn_write_install_date")
        elif txt == "btn_write_nrc_22_veh_name":
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = 'rstuvwxy'
            self.diag_write("btn_write_veh_name")
        elif txt == "btn_write_nrc_22_sys_name":
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended")
            self.write_txt = 'zabcdefg'
            self.diag_write("btn_write_veh_name")
        elif txt == "btn_write_nrc_22_net_config":
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
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
            if mywindow.drv_state:
                mywindow.set_drv_state()
                mywindow.thread_worker.slider_speed_func(20)
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
                mywindow.send_message('c', self.diag_tester_id, self.data, 0)
            time.sleep(0.3)
            reservoir = mywindow.thread_worker.reservoir[:]
            for qqq in reservoir:
                if qqq.arbitration_id == 0x18daf141:
                    self.res_data.append(qqq)
            mywindow.thread_worker.reservoir = []
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

        mywindow.drv_state = False
        mywindow.thread_worker.slider_speed_func(0)
        mywindow.set_drv_state()
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
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x00, 0x01]
        elif txt == "btn_comm_cont_nrc_22_tx_dis":
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x03, 0x28, 0x01, 0x01]
        elif txt == "btn_comm_cont_nrc_22_all_dis":
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
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

        mywindow.thread_worker.slider_speed_func(0)
        mywindow.drv_state = False
        mywindow.set_drv_state()

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
                mywindow.drv_state = True
                mywindow.set_drv_state()
                mywindow.thread_worker.slider_speed_func(20)
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
            mywindow.thread_worker.slider_speed_func(0)
            mywindow.drv_state = False
            mywindow.set_drv_state()

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
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
            self.diag_sess("btn_sess_extended", ex_comp_data=ex_comp_data, ex_comp_sig=ex_comp_sig)
            sig_li = [0x02, 0x85, 0x01]
        elif txt == "btn_dtc_cont_nrc_22_dis":
            mywindow.drv_state = True
            mywindow.set_drv_state()
            mywindow.thread_worker.slider_speed_func(20)
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

        mywindow.drv_state = False
        mywindow.set_drv_state()
        mywindow.thread_worker.slider_speed_func(0)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Enter:
            self.write_data_sender()

    def tester_present_handler(self):
        if self.chkbox_tester_present.isChecked():
            mywindow.tester_present_flag = True
        else:
            mywindow.tester_present_flag = False

    def ui_close(self):
        self.close()


class User_Filter(QDialog):

    def __init__(self):
        super().__init__()
        self.filter_ui = uic.loadUi(BASE_DIR + r"./src/can_basic_user_filter_ui.ui", self)
        self.setWindowTitle("User Defined Filter for E-51 IVI CAN Simulator")
        self.show()

        self.tx_name_set = set()
        self.default_item = "--Select signal--"
        self.comboBox_user_filter.addItem(self.default_item)

        self.filtered_list = []

        self.filter_list_flag = True

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
        mywindow.console_text_clear("tx_console_clear")

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
            mywindow.console_text_clear("tx_console_clear")
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


class User_Signal(QDialog):

    def __init__(self):
        super().__init__()
        self.signal_ui = uic.loadUi(BASE_DIR + r"./src/can_basic_user_signal_ui.ui", self)
        self.setWindowTitle("User Defined Signal for E-51 IVI CAN Simulator")
        self.show()

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
        mywindow.user_signal_worker._isRunning = True
        mywindow.user_signal_worker.start()
        mywindow.user_signal_worker.bus_selector = tx_channel
        mywindow.user_signal_worker.send_id = tx_id

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


class Serial_Port_Selection(QDialog):

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(BASE_DIR + r"./src/can_serial_bus_selection_ui.ui", self)

        self.setWindowTitle("Serial Port Selection for E-51 IVI CAN Simulator")
        self.ui_open()

        self.port_chkboxes = [self.chkbox_serial_port_1, self.chkbox_serial_port_2,
                              self.chkbox_serial_port_3, self.chkbox_serial_port_4,
                              self.chkbox_serial_port_5, self.chkbox_serial_port_6]

        self.btn_ports_apply.clicked.connect(self.selected_port_handler)
        self.btn_ports_refresh.clicked.connect(self.search_serial)

        self.ui_visibility()

    def port_setting(self, port_list=None):
        if len(port_list) != 0:
            self.ui_visibility(True)
            for num, device in zip(range(len(port_list)), port_list):
                self.port_chkboxes[num].setEnabled(True)
                self.port_chkboxes[num].setText(device.device)
        else:
            self.ui_visibility(False)

    def ui_visibility(self, flag=True):
        for device in self.port_chkboxes:
            device.setText("Serial port")
            device.setVisible(flag)
            device.setChecked(False)
        self.label_no_port.setVisible(not flag)

    def ui_open(self):
        self.show()

    def ui_close(self):
        self.close()

    def search_serial(self):
        ports = serial.tools.list_ports.comports()
        if len(ports) == 0:
            mywindow.serial_devices = []
        else:
            mywindow.serial_devices = ports
        self.port_setting(mywindow.serial_devices)

    def selected_port_handler(self):
        selected_list = []
        for port in self.port_chkboxes:
            if port.isChecked():
                selected_list.append(port.text())
        mywindow.selected_ports = selected_list
        mywindow.bus_console.appendPlainText("Serial port is selected")
        self.ui_close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Main()
    mywindow.show()
    sys.exit(app.exec_())
