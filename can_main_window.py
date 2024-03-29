import os
import sys
import can
import time
from datetime import datetime
import serial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from can import interfaces
import can.interfaces.vector
import can.interfaces.slcan
import pyqtgraph as pg
import data_identifier as data_id
import can_thread as worker
import diagnosis
import user_filter
import user_signal
import serial_port_selection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Ui_MainWindow, QtBaseClass = pg.Qt.loadUiType(BASE_DIR + r"./src/can_basic_ui.ui")


class SimulatorMain(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowIcon(QIcon(BASE_DIR + r"./src/drimaes_icon.ico"))
        self.setWindowTitle("Main Window for E-51 IVI CAN Simulator")

        self.bot_connection_text_init = "NOT connected     "
        self.bot_label_font_set = QFont('Arial', 10)
        self.bot_label_font_set.setBold(True)
        self.bot_connection_label = QLabel(self.bot_connection_text_init)
        self.bot_connection_label.setFont(self.bot_label_font_set)
        self.bot_connection_label.setStyleSheet("Color : red")

        self.bot_disconnect_btn = QPushButton()
        self.bot_disconnect_btn.setFixedSize(QSize(100, 35))
        self.bot_disconnect_btn.setText("Disconnect")
        self.bot_disconnect_btn.released.connect(self.bot_disconnect_btn_handler)
        self.bot_disconnect_btn.setEnabled(False)

        self.bottom_bar = self.statusBar()
        self.bottom_bar.setFixedHeight(50)

        self.bottom_bar.addPermanentWidget(self.bot_connection_label)
        self.bottom_bar.addPermanentWidget(self.bot_disconnect_btn)

        self.graph_widget.showGrid(x=False, y=False)
        self.curve = self.graph_widget.plot(x=[], y=[])

        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        self.graph_comboBox_init = "---Select signal---"
        self.graph_comboBox_id.addItem(self.graph_comboBox_init)
        self.graph_comboBox_id_specific.addItem(self.graph_comboBox_init)

        self.temp_list = []
        self.graph_x_list = []
        self.graph_y_list = []
        self.log_data = []
        self.graph_y_axis = None
        self.graph_y_axis_init_flag = True

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

        self.sub_mess_designated = None
        self.sub_data_designated = None

        self.tx_set = set()
        self.sig_dict = dict()

        self.btn_drv_state.clicked.connect(self.set_drv_state)

        self.btn_ota_cond.clicked.connect(self.set_ota_cond)

        # PMS_S
        self.pms_s_hvsm_worker = worker.PMS_S_HVSM(parent=self)
        self.pms_s_hvsm_worker.pms_s_hvsm_signal.connect(self.can_signal_sender)
        pms_s_worker_list = [self.pms_s_hvsm_worker]
        self.pms_s_worker_handler = NodeHandler(self.chkbox_node_pms_s, pms_s_worker_list).node_handler

        # PMS_C
        self.pms_c_strwhl_worker = worker.PMS_C_StrWhl(parent=self)
        self.pms_c_strwhl_worker.pms_c_strwhl_signal.connect(self.can_signal_sender)
        pms_c_worker_list = [self.pms_c_strwhl_worker]
        self.pms_c_worker_handler = NodeHandler(self.chkbox_node_pms_c, pms_c_worker_list).node_handler

        # PMS (Separated to C-CAN & P-CAN)
        # PMS (C-CAN)
        self.pms_bodycont_c_worker = worker.PMS_BodyCont_C(parent=self)
        self.pms_bodycont_c_worker.pms_bodycont_c_signal.connect(self.can_signal_sender)
        self.btn_gear_n.setChecked(True)  # Default value of Gear radio button
        self.pms_ptinfo_worker = worker.PMS_PTInfo(parent=self)
        self.pms_ptinfo_worker.pms_ptinfo_signal.connect(self.can_signal_sender)
        self.label_pt_ready.setStyleSheet("Color : red")
        # PMS (P-CAN)
        self.pms_bodycont_p_worker = worker.PMS_BodyCont_P(parent=self)
        self.pms_bodycont_p_worker.pms_bodycont_p_signal.connect(self.can_signal_sender)
        self.pms_vri_worker = worker.PMS_VRI(parent=self)
        self.pms_vri_worker.pms_vri_signal.connect(self.can_signal_sender)
        pms_worker_list = [self.pms_bodycont_c_worker, self.pms_ptinfo_worker, self.pms_bodycont_p_worker,
                           self.pms_vri_worker]
        self.pms_worker_handler = NodeHandler(self.chkbox_node_pms, pms_worker_list).node_handler

        # BCM
        self.bcm_mmi_worker = worker.BCM_MMI(parent=self)
        self.bcm_mmi_worker.bcm_mmi_signal.connect(self.can_signal_sender)
        self.btn_mscs_ok.setChecked(True)  # Default value of StWhlDiag signal radio button
        self.btn_mscs_ok.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_CmnFail.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_NotEdgePress.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_EdgeSho.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_SnsrFltT.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_FltPwrSplyErr.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_FltSwtHiSide.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.btn_mscs_SigFailr.clicked.connect(self.bcm_mmi_worker.thread_func)
        self.bcm_swrc_worker = worker.BCM_SWRC(parent=self)
        self.bcm_swrc_worker.bcm_swrc_signal.connect(self.can_signal_sender)
        self.btn_ok.pressed.connect(self.btn_press_handler)  # SWRC OK button
        self.btn_ok.released.connect(self.btn_release_handler)
        self.btn_undo.pressed.connect(self.btn_press_handler)  # SWRC Undo button
        self.btn_undo.released.connect(self.btn_release_handler)
        self.btn_mode.pressed.connect(self.btn_press_handler)  # SWRC Mode button
        self.btn_mode.released.connect(self.btn_release_handler)
        self.btn_mute.pressed.connect(self.btn_press_handler)  # SWRC Mute button
        self.btn_mute.released.connect(self.btn_release_handler)
        self.btn_left.pressed.connect(self.btn_press_handler)  # SWRC Left button
        self.btn_left.released.connect(self.btn_release_handler)
        self.btn_right.pressed.connect(self.btn_press_handler)  # SWRC Right button
        self.btn_right.released.connect(self.btn_release_handler)
        self.btn_call.pressed.connect(self.btn_press_handler)  # SWRC Call button
        self.btn_call.released.connect(self.btn_release_handler)
        self.btn_vol_up.pressed.connect(self.btn_press_handler)  # SWRC Volume Up button
        self.btn_vol_up.released.connect(self.btn_release_handler)
        self.btn_vol_down.pressed.connect(self.btn_press_handler)  # SWRC Volume Down button
        self.btn_vol_down.released.connect(self.btn_release_handler)
        self.bcm_strwhl_heat_worker = worker.BCM_StrWhl_Heat(parent=self)
        self.bcm_strwhl_heat_worker.bcm_strwhl_heat_signal.connect(self.can_signal_sender)
        self.bcm_lightchime_worker = worker.BCM_LightChime(parent=self)
        self.bcm_lightchime_worker.bcm_lightchime_signal.connect(self.can_signal_sender)
        self.bcm_stateupdate_worker = worker.BCM_StateUpdate(parent=self)
        self.bcm_stateupdate_worker.bcm_stateupdate_signal.connect(self.can_signal_sender)
        self.btn_acc.setChecked(True)  # Default value of Power mode radio button
        self.btn_bright_afternoon.setChecked(True)  # Default value of auto brightness radio button
        bcm_worker_list = [self.bcm_mmi_worker, self.bcm_swrc_worker, self.bcm_strwhl_heat_worker,
                           self.bcm_lightchime_worker, self.bcm_stateupdate_worker]
        self.bcm_worker_handler = NodeHandler(self.chkbox_node_bcm, bcm_worker_list).node_handler

        # IC
        self.ic_tachospeed_worker = worker.IC_TachoSpeed(parent=self)
        self.ic_tachospeed_worker.ic_tachospeed_signal.connect(self.can_signal_sender)
        self.ic_distance_worker = worker.IC_Distance(parent=self)
        self.ic_distance_worker.ic_distance_signal.connect(self.can_signal_sender)
        ic_worker_list = [self.ic_tachospeed_worker, self.ic_distance_worker]
        self.ic_worker_handler = NodeHandler(self.chkbox_node_ic, ic_worker_list).node_handler

        # ESC
        self.esc_tpms_worker = worker.ESC_TPMS(parent=self)
        self.esc_tpms_worker.esc_tpms_signal.connect(self.can_signal_sender)
        self.btn_tpms_success.clicked.connect(self.tpms_handler)
        self.btn_tpms_fail.clicked.connect(self.tpms_handler)
        esc_worker_list = [self.esc_tpms_worker]
        self.esc_worker_handler = NodeHandler(self.chkbox_node_esc, esc_worker_list).node_handler

        # FCS
        self.fcs_aeb_worker = worker.FCS_AEB(parent=self)
        self.fcs_aeb_worker.fcs_aeb_signal.connect(self.can_signal_sender)
        self.fcs_ldw_worker = worker.FCS_LDW(parent=self)
        self.fcs_ldw_worker.fcs_ldw_signal.connect(self.can_signal_sender)
        fcs_worker_list = [self.fcs_aeb_worker, self.fcs_ldw_worker]
        self.fcs_worker_handler = NodeHandler(self.chkbox_node_fcs, fcs_worker_list).node_handler

        # ACU
        self.acu_seatbelt_worker = worker.ACU_SeatBelt(parent=self)
        self.acu_seatbelt_worker.acu_seatbelt_signal.connect(self.can_signal_sender)
        self.chkbox_drv_invalid.stateChanged.connect(self.acu_seatbelt_worker.drv_invalid)
        self.chkbox_pass_invalid.stateChanged.connect(self.acu_seatbelt_worker.pass_invalid)
        acu_worker_list = [self.acu_seatbelt_worker]
        self.acu_worker_handler = NodeHandler(self.chkbox_node_acu, acu_worker_list).node_handler

        # BMS
        self.bms_batt_worker = worker.BMS_Batt(parent=self)
        self.bms_batt_worker.bms_batt_signal.connect(self.can_signal_sender)
        self.bms_charge_worker = worker.BMS_Charge(parent=self)
        self.bms_charge_worker.bms_charge_signal.connect(self.can_signal_sender)
        bms_worker_list = [self.bms_batt_worker, self.bms_charge_worker]
        self.bms_worker_handler = NodeHandler(self.chkbox_node_bms, bms_worker_list).node_handler

        # MCU
        self.mcu_motor_worker = worker.MCU_Motor(parent=self)
        self.mcu_motor_worker.mcu_motor_signal.connect(self.can_signal_sender)
        mcu_worker_list = [self.mcu_motor_worker]
        self.mcu_worker_handler = NodeHandler(self.chkbox_node_mcu, mcu_worker_list).node_handler

        self.chkbox_node_acu.released.connect(self.acu_worker_handler)
        self.chkbox_node_bcm.released.connect(self.bcm_worker_handler)
        self.chkbox_node_esc.released.connect(self.esc_worker_handler)
        self.chkbox_node_fcs.released.connect(self.fcs_worker_handler)
        self.chkbox_node_ic.released.connect(self.ic_worker_handler)
        self.chkbox_node_pms.released.connect(self.pms_worker_handler)
        self.chkbox_node_pms_s.released.connect(self.pms_s_worker_handler)
        self.chkbox_node_pms_c.released.connect(self.pms_c_worker_handler)
        self.chkbox_node_bms.released.connect(self.bms_worker_handler)
        self.chkbox_node_mcu.released.connect(self.mcu_worker_handler)

        self.thread_worker = worker.ThreadWorker(parent=self)
        self.thread_worker.signal_presenter.connect(self.signal_presenter)
        self.thread_worker.tx_img_presenter.connect(self.tx_image_present)

        self.tester_worker = worker.TesterPresent(parent=self)

        self.btn_tx_console_clear.clicked.connect(self.console_text_clear)

        self.btn_bus_peak.setChecked(True)
        self.btn_bus_peak.clicked.connect(self.serial_selector_handler)
        self.btn_bus_vector.clicked.connect(self.serial_selector_handler)
        self.btn_bus_canable.clicked.connect(self.serial_selector_handler)
        self.selected_ports = set()
        self.btn_bus_connect.clicked.connect(self.bus_connect)
        self.btn_bus_start.clicked.connect(self.thread_start)
        self.btn_bus_stop.clicked.connect(self.thread_stop)

        self.mmi_hvac = [0x00] * 8

        self.img_drv_heat_off = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_off.png").scaledToWidth(80)
        self.img_drv_heat_1 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_01_on.png").scaledToWidth(80)
        self.img_drv_heat_2 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_02_on.png").scaledToWidth(80)
        self.img_drv_heat_3 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_left_03_on.png").scaledToWidth(80)
        self.img_drv_vent_off = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_off.png").scaledToWidth(80)
        self.img_drv_vent_1 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_01_on.png").scaledToWidth(80)
        self.img_drv_vent_2 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_02_on.png").scaledToWidth(80)
        self.img_drv_vent_3 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_left_03_on.png").scaledToWidth(80)
        self.img_pass_heat_off = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_off.png").scaledToWidth(80)
        self.img_pass_heat_1 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_01_on.png").scaledToWidth(80)
        self.img_pass_heat_2 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_02_on.png").scaledToWidth(80)
        self.img_pass_heat_3 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_heating_seat_right_03_on.png").scaledToWidth(80)
        self.img_pass_vent_off = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_off.png").scaledToWidth(80)
        self.img_pass_vent_1 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_01_on.png").scaledToWidth(80)
        self.img_pass_vent_2 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_02_on.png").scaledToWidth(80)
        self.img_pass_vent_3 = QPixmap(
            BASE_DIR + r"./src/images/hvac/btn_hvac_ventilation_seat_right_03_on.png").scaledToWidth(80)
        self.img_side_mani_on = QPixmap(
            BASE_DIR + r"./src/images/side/btn_navi_sidemirror_normal.png").scaledToWidth(80)
        self.img_side_mani_off = QPixmap(
            BASE_DIR + r"./src/images/side/btn_navi_sidemirror_fold.png").scaledToWidth(80)
        self.img_side_heat_on = QPixmap(
            BASE_DIR + r"./src/images/side/sidemirrorheat_on.png").scaledToWidth(80)
        self.img_side_heat_off = QPixmap(
            BASE_DIR + r"./src/images/side/sidemirrorheat_off.png").scaledToWidth(80)
        self.img_str_whl_heat_off = QPixmap(
            BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_off.png").scaledToWidth(80)
        self.img_str_whl_heat_1 = QPixmap(
            BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_01_on.png").scaledToWidth(80)
        self.img_str_whl_heat_2 = QPixmap(
            BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_02_on.png").scaledToWidth(80)
        self.img_str_whl_heat_3 = QPixmap(
            BASE_DIR + r"./src/images/str_whl_heat/btn_navi_heatedsteeringwheel_03_on.png").scaledToWidth(80)

        self.btn_save_log.released.connect(self.save_log)
        self.chkbox_save_log.released.connect(self.save_log)
        self.pbar_save_log.setValue(0)
        self.pbar_save_log.setVisible(False)

        self.chkbox_can_dump.released.connect(self.can_dump_mode)

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

        self.treeWidget_tx.setColumnWidth(0, 120)
        self.treeWidget_tx.setColumnWidth(1, 105)
        self.treeWidget_tx.setColumnWidth(2, 200)
        self.treeWidget_tx.setColumnWidth(4, 170)

        self.graph_comboBox_num.addItem("1")
        self.graph_comboBox_num.addItem("2")
        self.graph_comboBox_num.addItem("3")

        self.graph_widget.showGrid(x=True, y=True)

        self.set_mmi_labels_init(False)
        self.set_general_btns_labels(True)
        self.set_node_btns(True)
        self.set_can_basic_btns_labels(False)

        self.comboBox_log_data_init = "All data"

        self.comboBox_log_data.currentIndexChanged.connect(self.tree_widget_log_target_adder)

        self.log_str_list = []
        self.data_entire_list = []
        self.data_selected_list = []
        self.select_specific_log_data = False
        self.logging_init_flag = True

        self.diag_obj = None
        self.chkbox_diag_console.clicked.connect(self.diag_main)

        self.chkbox_arbitrary_signal_1.clicked.connect(self.user_signal_handler)

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
                        self.bus_connect_handler(True)
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
                        self.bus_connect_handler(True)
                    except interfaces.vector.VectorError as e1:
                        print(e1)
                        try:
                            self.p_can_bus = can.interface.Bus(bustype='vector', channel=1, bitrate='500000')
                            self.bus_console.appendPlainText("Vector bus is connected.")
                            self.bus_console.appendPlainText("1 Channel is connected.")
                            self.bus_connect_handler(True)
                        except interfaces.vector.VectorError as e2:
                            print(e2)
                            self.bus_console.appendPlainText("Connect the Vector(CANoe) device.")
                    except ImportError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Vector(CANoe) driver is not installed.")
                elif self.btn_bus_canable.isChecked():
                    self.selected_ports = list(self.selected_ports)
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
                        self.bus_connect_handler(True)
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
                            if temp1.recv(0.3):
                                self.c_can_bus = temp1
                            else:
                                self.p_can_bus = temp1
                            self.bus_console.appendPlainText("1 Channel is connected")
                        self.bus_connect_handler(True)
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
                            self.bus_connect_handler(True)
                            self.bus_console.appendPlainText("Vector bus is connected")
                        except can.interfaces.vector.exceptions.VectorError as e2:
                            print(e2)
                            self.console_text_clear("tx_console_clear")
                            self.bus_connect_handler(True)
                            self.p_can_bus = None
                            self.bus_console.appendPlainText("1 Channel is connected")
                    except ImportError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Vector(CANoe) driver is not installed.")
                    except can.interfaces.vector.exceptions.VectorError as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Connect the Vector device.")
                elif self.btn_bus_canable.isChecked():
                    self.selected_ports = list(self.selected_ports)
                    try:
                        temp1 = can.interface.Bus(bustype='slcan', channel=self.selected_ports[0], bitrate='500000')
                        self.bus_console.appendPlainText("Serial bus(CANable bus) is connected.")
                        try:
                            temp2 = can.interface.Bus(bustype='slcan', channel=self.selected_ports[1], bitrate='500000')
                            if temp1.recv(0.3):
                                self.c_can_bus = temp1
                                self.p_can_bus = temp2
                            else:
                                self.c_can_bus = temp2
                                self.p_can_bus = temp1
                            self.bus_console.appendPlainText("2 Channel is connected.")
                        except IndexError:
                            if temp1.recv(0.3):
                                self.c_can_bus = temp1
                            else:
                                self.p_can_bus = temp1
                            self.bus_console.appendPlainText("1 Channel is connected.")
                        self.bus_connect_handler(True)
                    except serial.serialutil.SerialException as e1:
                        print(e1)
                        self.bus_console.appendPlainText("Select appropriate serial port.")
                    except IndexError:
                        self.bus_console.appendPlainText("Select the serial port first.")
        else:
            self.bus_console.appendPlainText("CAN bus is already connected.")

    def bus_connect_handler(self, flag=True):
        self.bus_flag = flag
        self.btn_bus_peak.setEnabled(not flag)
        self.btn_bus_vector.setEnabled(not flag)
        self.btn_bus_canable.setEnabled(not flag)
        if self.c_can_bus:
            if self.p_can_bus:
                self.bot_connection_label.setText("C-CAN & P-CAN buses are connected.     ")
                self.bot_connection_label.setStyleSheet("Color : blue")
            else:
                self.bot_connection_label.setText("C-CAN bus is connected.     ")
                self.bot_connection_label.setStyleSheet("Color : blue")
        elif self.p_can_bus:
            self.bot_connection_label.setText("P-CAN bus is connected.     ")
            self.bot_connection_label.setStyleSheet("Color : blue")
        else:
            self.bot_connection_label.setText(self.bot_connection_text_init)
            self.bot_connection_label.setStyleSheet("Color : red")
        self.bot_connection_label.setFont(self.bot_label_font_set)
        self.btn_bus_connect.setEnabled(not flag)
        self.bot_disconnect_btn.setEnabled(flag)
        if not flag:
            self.btn_bus_peak.setChecked(True)
            self.bus_console.appendPlainText("Current bus is disconnected.")
        self.drv_state = False
        self.set_drv_state()

    def thread_start(self):
        if self.bus_flag:
            self.thread_worker._isRunning = True
            self.tester_worker._isRunning = True

            self.acu_worker_handler()
            self.bcm_worker_handler()
            self.esc_worker_handler()
            self.fcs_worker_handler()
            self.ic_worker_handler()
            self.pms_worker_handler()
            self.pms_s_worker_handler()
            self.pms_c_worker_handler()
            self.bms_worker_handler()
            self.mcu_worker_handler()

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

        self.comboBox_log_data.setEnabled(False)

        self.acu_worker_handler(flag=False)
        self.bcm_worker_handler(flag=False)
        self.esc_worker_handler(flag=False)
        self.fcs_worker_handler(flag=False)
        self.ic_worker_handler(flag=False)
        self.pms_worker_handler(flag=False)
        self.pms_s_worker_handler(flag=False)
        self.pms_c_worker_handler(flag=False)
        self.bms_worker_handler(flag=False)
        self.mcu_worker_handler(flag=False)

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
        if self.chkbox_save_log.isChecked():
            self.log_data.append(message)
        if bus:
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
                path = QFileDialog.getExistingDirectory(self)
                if path:
                    if self.chkbox_save_log.isChecked():
                        self.bus_console.appendPlainText("Can Log Writing Stop")
                        self.chkbox_save_log.toggle()
                    self.bus_console.appendPlainText("Can Log saving Start")
                    if self.comboBox_log_format.currentText() == "blf":
                        log_path = path + f"/log.blf"
                        dup_num = 1
                        while os.path.isfile(log_path):
                            log_path = path + f"/log ({dup_num}).blf"
                            dup_num += 1
                        log_writer = can.BLFWriter(log_path)
                    elif self.comboBox_log_format.currentText() == "asc":
                        log_path = path + f"/log.asc"
                        dup_num = 1
                        while os.path.isfile(log_path):
                            log_path = path + f"/log ({dup_num}).asc"
                            dup_num += 1
                        log_writer = can.ASCWriter(log_path)
                    else:
                        QMessageBox.information(self, "Format Error", "Select the log file format")
                        return False
                    self.pbar_save_log.setVisible(True)
                    select_flag = {}
                    for comp in self.data_entire_list:
                        select_flag[int(comp["data_id"][2:], 16)] = False
                        for selected_comp in self.data_selected_list:
                            if comp["data_name"] == selected_comp["data_name"]:
                                select_flag[int(comp["data_id"][2:], 16)] = True
                                break
                    for i in range(len(self.log_data)):
                        if select_flag[self.log_data[i].arbitration_id]:
                            log_writer.on_message_received(self.log_data[i])
                        save_progress = int((i / (len(self.log_data)-1)) * 100)
                        self.pbar_save_log.setValue(save_progress)
                        QtCore.QCoreApplication.processEvents()
                    log_writer.stop()
                    self.bus_console.appendPlainText("Can Log saving End")
                    QMessageBox.information(self, "Log Save", f"CAN Log Saving complete\n({log_path})")
                    self.pbar_save_log.setVisible(False)
                    self.log_data = []
                else:
                    QMessageBox.warning(self, "Log Save", "Set appropriate directory")
                    return False
            else:
                QMessageBox.warning(self, "Log Save", "Check the Log Save checkbox first")
                return False
        elif self.sender().objectName() == "chkbox_save_log":
            if self.chkbox_save_log.isChecked():
                if self.logging_init_flag:
                    self.comboBox_log_data.addItem(self.comboBox_log_data_init)
                    self.comboBox_log_data.addItems(self.log_str_list)
                    self.comboBox_log_format.addItem("---Select format---")
                    self.comboBox_log_format.addItem("blf")
                    self.comboBox_log_format.addItem("asc")
                    self.logging_init_flag = False
                self.bus_console.appendPlainText("Can Log Writing Start")
                self.tree_widget_log_target_adder()
                return True
            else:
                self.bus_console.appendPlainText("Can Log Writing Stop")
                self.comboBox_log_data.setCurrentIndex(0)
        if len(self.log_data) == 0:
            self.treeWidget_log_target.clear()
            self.comboBox_log_data.clear()
            self.comboBox_log_format.clear()
            self.logging_init_flag = True

    def tree_widget_log_target_adder(self):
        if len(self.data_entire_list) == 0:
            for i in range(1, self.comboBox_log_data.count()):
                data = self.comboBox_log_data.itemText(i)
                id_index = data.find("(")
                data_name = data[:id_index]
                data_id = data[id_index + 1:-1]
                single_dict = {"data_name": data_name, "data_id": data_id}
                self.data_entire_list.append(single_dict)
        index = self.comboBox_log_data.currentIndex()
        if index < 0:
            return False
        elif index == 0:
            self.treeWidget_log_target.clear()
            for comp in self.data_entire_list:
                item = QTreeWidgetItem()
                item.setText(0, comp["data_id"])
                item.setText(1, comp["data_name"])
                self.treeWidget_log_target.addTopLevelItems([item])
            self.select_specific_log_data = True
            self.data_selected_list = self.data_entire_list[:]
        else:
            if self.select_specific_log_data:
                self.treeWidget_log_target.clear()
                self.select_specific_log_data = False
                self.data_selected_list = []
            for comp in self.data_selected_list:
                if comp["data_name"][:7] == self.comboBox_log_data.currentText()[:7]:
                    return False
            selected_signal = self.data_entire_list[index-1]
            item = QTreeWidgetItem()
            item.setText(0, selected_signal["data_id"])
            item.setText(1, selected_signal["data_name"])
            self.treeWidget_log_target.addTopLevelItems([item])
            self.data_selected_list.append(selected_signal)
        header = self.treeWidget_log_target.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def set_drv_state(self):
        if self.drv_state or self.sender().text() == 'Set Driving State':
            self.btn_gear_d.setChecked(True)
            self.btn_ign.setChecked(True)
            self.pms_ptinfo_worker.ptready_flag = True
        else:
            self.btn_gear_n.setChecked(True)
            self.btn_acc.setChecked(True)
            self.pms_ptinfo_worker.ptready_flag = False
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
        self.comboBox_log_data.setEnabled(flag)

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
        self.tick_14p5_stwhl.setStyleSheet(f"color: {color}")
        self.tick_minus_10_stwhl.setStyleSheet(f"color: {color}")
        self.tick_minus_14p5_stwhl.setStyleSheet(f"color: {color}")

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
            self.graph_comboBox_id.clear()
            self.comboBox_log_data.clear()
            self.comboBox_log_data.addItem(self.comboBox_log_data_init)
        elif btn_name == "btn_write_data_clear" or txt:
            if self.diag_obj:
                self.diag_obj.label_flag_send.setText("Fill the data")
                self.diag_obj.lineEdit_write_data.clear()
        elif btn_name == "btn_diag_dtc_console_clear":
            if self.diag_obj:
                self.diag_obj.diag_initialization()

    @pyqtSlot(can.Message, str, float)
    def signal_presenter(self, tx_single, bus_num, time_delta_diff):
        tx_time = self.time_mode(tx_single.timestamp, time_delta_diff)
        tx_id = hex(tx_single.arbitration_id)
        if bus_num == 'c':
            tx_channel = "C-CAN"
        elif bus_num == 'p':
            tx_channel = "P-CAN"
        tx_message_info = data_id.message_info(bus=tx_channel, can_id=tx_single.arbitration_id)
        tx_name = tx_message_info["mess_name"]
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
            self.sig_dict[tx_single.arbitration_id] = tx_single.channel
            identifier = str(tx_single.arbitration_id) + str(tx_single.channel)
            self.tx_set.add(identifier)
            len_now = len(self.tx_set)
            if len_now - len_prev == 0:
                for item in self.item:
                    if tx_id == item.text(0) and tx_channel == item.text(3):
                        item.setText(1, tx_time)
                        item.setText(4, tx_data)
                        specific_signals = []
                        for i in range(item.childCount()):
                            for j in range(len(tx_message_info["data_set"])):
                                if tx_message_info["data_set"][j]["name"] == item.child(i).text(2):
                                    sub_num = j
                                    break
                            sub_mess = tx_message_info["data_set"][sub_num]
                            try:
                                sub_data = sub_mess[int(data_id.data_matcher(tx_single, sub_mess))]
                            except KeyError:
                                sub_data = str(data_id.data_matcher(tx_single, sub_mess))
                            except ValueError:
                                sub_data = ''
                            item.child(i).setText(4, sub_data)
                            specific_signals.append(sub_mess["name"])
                            if self.sub_mess_designated == sub_mess["name"]:
                                self.sub_data_designated = data_id.data_matcher(tx_single, sub_mess)
                        if self.graph_comboBox_id.currentText() == "---Select signal---":
                            if self.graph_comboBox_id_specific.count() > 1:
                                self.graph_comboBox_id_specific.clear()
                                self.graph_comboBox_id_specific.addItem("---Select signal---")
                        else:
                            if self.graph_comboBox_id.currentText() == tx_name:
                                if self.graph_comboBox_id_specific.count() == 1:
                                    self.graph_comboBox_id_specific.addItems(specific_signals)
                                    self.pre_message = self.graph_comboBox_id.currentText()
                                if self.pre_message != self.graph_comboBox_id.currentText():
                                    self.graph_comboBox_id_specific.clear()
                                    self.graph_comboBox_id_specific.addItem("---Select signal---")
                                    self.graph_comboBox_id_specific.addItems(specific_signals)
                                    self.pre_message = self.graph_comboBox_id.currentText()
                        break
            else:
                item = QTreeWidgetItem()
                item.setText(0, tx_id)
                item.setText(1, tx_time)
                item.setText(2, tx_name)
                item.setText(3, tx_channel)
                item.setText(4, tx_data)
                for sub_message in tx_message_info["data_set"]:
                    sub_item = QTreeWidgetItem(item)
                    sub_item.setText(2, sub_message["name"])
                    try:
                        sub_item.setText(4, sub_message[int(data_id.data_matcher(tx_single, sub_message))])
                    except KeyError:
                        sub_item.setText(4, str(data_id.data_matcher(tx_single, sub_message)))
                    except ValueError:
                        sub_item.setText(4, "")
                self.item.append(item)
                self.treeWidget_tx.addTopLevelItems(self.item)
                self.graph_comboBox_id.addItem(tx_name)
                self.log_str_list.append(f'{tx_name} ({tx_id})')

        if self.graph_comboBox_id.currentText() == tx_name:
            if self.graph_comboBox_id_specific.currentText() == self.graph_comboBox_init:
                self.graph_y_axis_init_flag = True
            else:
                if self.graph_y_axis_init_flag:
                    # self.graph_y_axis = YAxisItem(orientation='left', txt=self.graph_comboBox_id_specific.currentText())
                    self.graph_y_axis = pg.AxisItem(orientation='left')
                    self.graph_y_axis.setTicks([dict(enumerate(range(0, 20))).items()])
                    # self.graph_widget.setAxisItems(axisItems={'left':self.graph_y_axis})
                    # print(self.graph_y_axis)
                    self.graph_y_axis_init_flag = False
            if self.tx_time_rel and self.sub_data_designated:
                # if len(self.graph_x_list) == 10:
                #     self.graph_x_list.pop(0)
                #     self.graph_y_list.pop(0)
                self.graph_x_list.append(float(self.tx_time_rel))
                self.graph_y_list.append(int(self.sub_data_designated))

        if len(self.graph_x_list) > 0:
            self.graph_presenter(self.graph_x_list, self.graph_y_list)

        if self.graph_comboBox_id_specific.currentText() != "---Select signal---":
            self.sub_mess_designated = self.graph_comboBox_id_specific.currentText()

    def graph_presenter(self, graph_x_list, graph_y_list):
        if len(graph_x_list) < 10:
            start_x = graph_x_list[0]
        else:
            start_x = graph_x_list[-10]
        end_x = graph_x_list[-1]
        self.graph_widget.setXRange(start_x, end_x, padding=0)
        self.curve.setData(graph_x_list, graph_y_list, symbol='o', pen='r')

    @pyqtSlot(str, int, list, float)
    def can_signal_sender(self, bus_mess, send_id, send_data, time_diff_delta):
        if send_id == 0xFF:
            if not self.chkbox_can_dump.isChecked():
                self.bus_console.appendPlainText(bus_mess)
        else:
            self.send_message(bus_mess, send_id, send_data, time_diff_delta)

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

    @pyqtSlot(can.Message, int)
    def tx_image_present(self, tx_mess, tx_id):
        if tx_id == 0x18ffd741:
            self.pms_s_hvsm_worker.data[0] = tx_mess.data[1]
            hvsm_tx = bin(tx_mess.data[1])[2:].zfill(8)

            self.mmi_hvac[2] = int(hvsm_tx[6:], 2)
            if int(hvsm_tx[6:], 2) == 3:
                self.txt_res_drv_heat.setPixmap(self.img_drv_heat_3)
            elif int(hvsm_tx[6:], 2) == 2:
                self.txt_res_drv_heat.setPixmap(self.img_drv_heat_2)
            elif int(hvsm_tx[6:], 2) == 1:
                self.txt_res_drv_heat.setPixmap(self.img_drv_heat_1)
            elif int(hvsm_tx[6:], 2) == 0:
                self.txt_res_drv_heat.setPixmap(self.img_drv_heat_off)

            self.mmi_hvac[4] = int(hvsm_tx[2:4], 2)
            if int(hvsm_tx[2:4], 2) == 3:
                self.txt_res_drv_vent.setPixmap(self.img_drv_vent_3)
            elif int(hvsm_tx[2:4], 2) == 2:
                self.txt_res_drv_vent.setPixmap(self.img_drv_vent_2)
            elif int(hvsm_tx[2:4], 2) == 1:
                self.txt_res_drv_vent.setPixmap(self.img_drv_vent_1)
            elif int(hvsm_tx[2:4], 2) == 0:
                self.txt_res_drv_vent.setPixmap(self.img_drv_vent_off)

            self.mmi_hvac[3] = int(hvsm_tx[4:6], 2)
            if int(hvsm_tx[4:6], 2) == 3:
                self.txt_res_pass_heat.setPixmap(self.img_pass_heat_3)
            elif int(hvsm_tx[4:6], 2) == 2:
                self.txt_res_pass_heat.setPixmap(self.img_pass_heat_2)
            elif int(hvsm_tx[4:6], 2) == 1:
                self.txt_res_pass_heat.setPixmap(self.img_pass_heat_1)
            elif int(hvsm_tx[4:6], 2) == 0:
                self.txt_res_pass_heat.setPixmap(self.img_pass_heat_off)

            self.mmi_hvac[5] = int(hvsm_tx[:2], 2)
            if int(hvsm_tx[:2], 2) == 3:
                self.txt_res_pass_vent.setPixmap(self.img_pass_vent_3)
            elif int(hvsm_tx[:2], 2) == 2:
                self.txt_res_pass_vent.setPixmap(self.img_pass_vent_2)
            elif int(hvsm_tx[:2], 2) == 1:
                self.txt_res_pass_vent.setPixmap(self.img_pass_vent_1)
            elif int(hvsm_tx[:2], 2) == 0:
                self.txt_res_pass_vent.setPixmap(self.img_pass_vent_off)

            str_whl_heat_tx = tx_mess.data[0]
            if str_whl_heat_tx == 0xc0:
                self.txt_res_st_whl_heat.setPixmap(self.img_str_whl_heat_off)
            elif str_whl_heat_tx == 0xc3:
                self.txt_res_st_whl_heat.setPixmap(self.img_str_whl_heat_3)
            elif str_whl_heat_tx == 0xc2:
                self.txt_res_st_whl_heat.setPixmap(self.img_str_whl_heat_2)
            elif str_whl_heat_tx == 0xc1:
                self.txt_res_st_whl_heat.setPixmap(self.img_str_whl_heat_1)

            self.bcm_mmi_worker.single_tx_side_mani = tx_mess.data[2]
            side_mani_tx = tx_mess.data[2]
            if side_mani_tx == 0xf4:
                self.txt_res_side_mani.setPixmap(self.img_side_mani_off)
            elif side_mani_tx == 0xf8:
                self.txt_res_side_mani.setPixmap(self.img_side_mani_on)
            # else:
            #     self.txt_res_side_mani.setText("None")

        elif tx_id == 0x18ffd841:
            self.bcm_mmi_worker.single_tx_softswset = tx_mess.data
            light_tx = tx_mess.data[3]
            if light_tx == 0xcf:
                self.txt_res_light.setText("30s")
            elif light_tx == 0xd7:
                self.txt_res_light.setText("60s")
            elif light_tx == 0xdf:
                self.txt_res_light.setText("90s")
            else:
                self.txt_res_light.setText("OFF")

            side_heat_tx = tx_mess.data[7]
            if side_heat_tx == 0x7f:
                self.txt_res_side_heat.setPixmap(self.img_side_heat_off)
            elif side_heat_tx == 0xbf:
                self.txt_res_side_heat.setPixmap(self.img_side_heat_on)
            # else:
            #     self.txt_res_side_heat.setText("None")

        elif tx_id == 0x0c0ba021:
            self.fcs_aeb_worker.single_tx = tx_mess.data[0]
            aeb_tx = tx_mess.data[0]
            if aeb_tx == 0xfd:
                self.txt_res_aeb.setText("ON")
            elif aeb_tx == 0xfc:
                self.txt_res_aeb.setText("OFF")
            else:
                self.txt_res_aeb.setText("None")

    def tx_filter(self, tx_id, tx_name, tx_channel):
        if self.btn_filter_user.isChecked():
            return self.user_filter_handler(tx_name=tx_name)
        else:
            if self.user_filter_obj:
                self.user_filter_obj.ui_close()
                self.user_filter_obj = None

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

    def btn_press_handler(self):
        self.bcm_swrc_worker.btn_name = self.sender().objectName()

    def btn_release_handler(self):
        self.bcm_swrc_worker.btn_name = False

    def diag_main(self):
        if self.chkbox_diag_console.isChecked():
            self.diag_obj = diagnosis.DiagMain(BASE_DIR, self)
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
            self.user_filter_obj = user_filter.UserFilter(BASE_DIR, self)
        if self.user_filter_obj.node_filter(tx_name):
            return True
        else:
            return self.user_filter_obj.user_filter(tx_name)

    def user_signal_handler(self):
        if not self.chkbox_arbitrary_signal_1.isChecked():
            self.user_signal_obj.ui_close()
            self.user_signal_obj = None
            return 0
        if not self.user_signal_obj:
            self.user_signal_obj = user_signal.UserSignal(BASE_DIR, self)

    def serial_selector_handler(self):
        if self.btn_bus_peak.isChecked() or self.btn_bus_vector.isChecked():
            if self.serial_selection_obj:
                self.serial_selection_obj.ui_close()
        else:
            if not self.serial_selection_obj:
                self.serial_selection_obj = serial_port_selection.SerialPortSelection(BASE_DIR, self)
            if self.serial_selection_obj.open_flag:
                self.serial_selection_obj.ui_close()
            self.serial_selection_obj.search_serial()
            self.serial_selection_obj.ui_open()

    def bot_disconnect_btn_handler(self):
        self.thread_stop()
        time.sleep(0.3)

        if self.c_can_bus:
            self.c_can_bus.shutdown()
            self.c_can_bus = None

        if self.p_can_bus:
            self.p_can_bus.shutdown()
            self.p_can_bus = None
        self.bus_connect_handler(False)


class NodeHandler(object):
    def __init__(self, chkbox_component, worker_list):
        self.chkbox_comp = chkbox_component
        self.worker_list = worker_list

    def node_handler(self, flag=True):
        for node_worker in self.worker_list:
            if self.chkbox_comp.isChecked() and flag:
                node_worker._isRunning = True
                node_worker.start()
            else:
                node_worker.stop()


class YAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enableAutoSIPrefix(False)
        if "txt" in kwargs:
            self.txt = kwargs["txt"]
        self.entire_signals = []
        self.y_tick_list()

    def y_tick_list(self):
        for single_mess in data_id.master_set.values():
            for single_sig in single_mess["data_set"]:
                self.entire_signals.append(single_sig)

    def setTicks(self, ticks):
        pass

    def set_tick_lists(self, values):
        for single_sig in self.entire_signals:
            if single_sig["name"] == self.txt:
                target_sig = single_sig
                break
        res_list = []
        for val in values:
            if val in target_sig:
                res_list.append(target_sig[val])
            else:
                res_list.append(int(val))
        return res_list

    def tickStrings(self, values, scale, spacing):
        return self.set_ticks(values)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = SimulatorMain()
    main_window.show()
    sys.exit(app.exec_())

