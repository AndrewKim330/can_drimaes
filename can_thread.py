import time
import datetime

import can.interfaces.pcan
import sig_generator as sig_gen
from PyQt5 import QtCore
from PyQt5.QtCore import *


class NodeThread(QThread):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._isRunning = True
        self.period = 0.100
        self.time_flag = False
        self.pre_time = None
        self.data = [0xFF] * 8
        self.mmi_hvac = [0x00] * 8

    def run(self):
        while self._isRunning:
            self.thread_func()
            QtCore.QCoreApplication.processEvents()

    def calc_delta(self, send_id, send_time):
        if self.time_flag:
            delta = time.time() - self.pre_time
        else:
            delta = self.period
            self.time_flag = True
        self.pre_time = send_time
        return delta

    def thread_func(self):
        pass

    def stop(self):
        self._isRunning = False


class ThreadWorker(NodeThread):
    signal_presenter = pyqtSignal(can.Message, str, float)

    def __init__(self, parent):
        super().__init__(parent)
        self._isRunning = True
        self.reservoir = []
        self.time_flag_li = [False] * 6
        self.delta_diff_li = [None] * 6
        self.pre_time_li = [None] * 6
        self.delta_recv = dict()

    def run(self):
        while self._isRunning:
            if self.parent.c_can_bus:
                c_recv = self.parent.c_can_bus.recv()
                self.calc_delta(c_recv)

                if self.parent.chkbox_save_log.isChecked():
                    self.parent.log_data.append(c_recv)
                if c_recv.arbitration_id == 0x18daf141:
                    self.reservoir.append(c_recv)
                if c_recv.arbitration_id == 0x18ffd741:
                    self.parent.pms_s_hvsm_worker.data[0] = c_recv.data[1]
                    hvsm_tx = bin(c_recv.data[1])[2:].zfill(8)

                    self.mmi_hvac[2] = int(hvsm_tx[6:], 2)
                    if int(hvsm_tx[6:], 2) == 3:
                        self.parent.txt_res_drv_heat.setPixmap(self.parent.img_drv_heat_3)
                    elif int(hvsm_tx[6:], 2) == 2:
                        self.parent.txt_res_drv_heat.setPixmap(self.parent.img_drv_heat_2)
                    elif int(hvsm_tx[6:], 2) == 1:
                        self.parent.txt_res_drv_heat.setPixmap(self.parent.img_drv_heat_1)
                    elif int(hvsm_tx[6:], 2) == 0:
                        self.parent.txt_res_drv_heat.setPixmap(self.parent.img_drv_heat_off)

                    self.mmi_hvac[4] = int(hvsm_tx[2:4], 2)
                    if int(hvsm_tx[2:4], 2) == 3:
                        self.parent.txt_res_drv_vent.setPixmap(self.parent.img_drv_vent_3)
                    elif int(hvsm_tx[2:4], 2) == 2:
                        self.parent.txt_res_drv_vent.setPixmap(self.parent.img_drv_vent_2)
                    elif int(hvsm_tx[2:4], 2) == 1:
                        self.parent.txt_res_drv_vent.setPixmap(self.parent.img_drv_vent_1)
                    elif int(hvsm_tx[2:4], 2) == 0:
                        self.parent.txt_res_drv_vent.setPixmap(self.parent.img_drv_vent_off)

                    self.mmi_hvac[3] = int(hvsm_tx[4:6], 2)
                    if int(hvsm_tx[4:6], 2) == 3:
                        self.parent.txt_res_pass_heat.setPixmap(self.parent.img_pass_heat_3)
                    elif int(hvsm_tx[4:6], 2) == 2:
                        self.parent.txt_res_pass_heat.setPixmap(self.parent.img_pass_heat_2)
                    elif int(hvsm_tx[4:6], 2) == 1:
                        self.parent.txt_res_pass_heat.setPixmap(self.parent.img_pass_heat_1)
                    elif int(hvsm_tx[4:6], 2) == 0:
                        self.parent.txt_res_pass_heat.setPixmap(self.parent.img_pass_heat_off)

                    self.mmi_hvac[5] = int(hvsm_tx[:2], 2)
                    if int(hvsm_tx[:2], 2) == 3:
                        self.parent.txt_res_pass_vent.setPixmap(self.parent.img_pass_vent_3)
                    elif int(hvsm_tx[:2], 2) == 2:
                        self.parent.txt_res_pass_vent.setPixmap(self.parent.img_pass_vent_2)
                    elif int(hvsm_tx[:2], 2) == 1:
                        self.parent.txt_res_pass_vent.setPixmap(self.parent.img_pass_vent_1)
                    elif int(hvsm_tx[:2], 2) == 0:
                        self.parent.txt_res_pass_vent.setPixmap(self.parent.img_pass_vent_off)

                    str_whl_heat_tx = c_recv.data[0]
                    if str_whl_heat_tx == 0xc0:
                        self.parent.txt_res_st_whl_heat.setPixmap(self.parent.img_str_whl_heat_off)
                    elif str_whl_heat_tx == 0xc3:
                        self.parent.txt_res_st_whl_heat.setPixmap(self.parent.img_str_whl_heat_3)
                    elif str_whl_heat_tx == 0xc2:
                        self.parent.txt_res_st_whl_heat.setPixmap(self.parent.img_str_whl_heat_2)
                    elif str_whl_heat_tx == 0xc1:
                        self.parent.txt_res_st_whl_heat.setPixmap(self.parent.img_str_whl_heat_1)

                    self.parent.bcm_mmi_worker.single_tx_side_mani = c_recv.data[2]
                    side_mani_tx = c_recv.data[2]
                    if side_mani_tx == 0xf4:
                        self.parent.txt_res_side_mani.setPixmap(self.parent.img_side_mani_off)
                    elif side_mani_tx == 0xf8:
                        self.parent.txt_res_side_mani.setPixmap(self.parent.img_side_mani_on)
                    # else:
                    #     self.parent.txt_res_side_mani.setText("None")

                if c_recv.arbitration_id == 0x18ffd841:
                    self.parent.bcm_mmi_worker.single_tx_softswset = c_recv.data
                    light_tx = c_recv.data[3]
                    if light_tx == 0xcf:
                        self.parent.txt_res_light.setText("30s")
                    elif light_tx == 0xd7:
                        self.parent.txt_res_light.setText("60s")
                    elif light_tx == 0xdf:
                        self.parent.txt_res_light.setText("90s")
                    else:
                        self.parent.txt_res_light.setText("OFF")

                    side_heat_tx = c_recv.data[7]
                    if side_heat_tx == 0x7f:
                        self.parent.txt_res_side_heat.setPixmap(self.parent.img_side_heat_off)
                    elif side_heat_tx == 0xbf:
                        self.parent.txt_res_side_heat.setPixmap(self.parent.img_side_heat_on)
                    # else:
                    #     self.parent.txt_res_side_heat.setText("None")

                if c_recv.arbitration_id == 0x0c0ba021:
                    self.parent.fcs_aeb_worker.single_tx = c_recv.data[0]
                    aeb_tx = c_recv.data[0]
                    if aeb_tx == 0xfd:
                        self.parent.txt_res_aeb.setText("ON")
                    elif aeb_tx == 0xfc:
                        self.parent.txt_res_aeb.setText("OFF")
                    else:
                        self.parent.txt_res_aeb.setText("None")

            if self.parent.chkbox_can_dump.isChecked() and self.parent.p_can_bus:
                pass
                # if self.parent.canable_device:
                #     frame_type, can_id, can_data, extended, ts = self.parent.c_can_bus.read(600000)
                #     p_recv = can.Message(timestamp=time.time(), arbitration_id=can_id, data=can_data, channel=self.parent.p_can_bus)
                # else:
                #     p_recv = self.parent.p_can_bus.recv()
                # self.calc_delta(p_recv)
                # self.signal_emit(p_recv, 'p')

            self.state_check()
            QtCore.QCoreApplication.processEvents()

    def calc_delta(self, recv_message):
        recv_id = recv_message.arbitration_id
        try:
            delta_time = recv_message.timestamp - self.delta_recv[recv_id]
        except KeyError:
            delta_time = 0
        self.delta_recv[recv_id] = recv_message.timestamp

        self.signal_emit(recv_message, 'c', delta_time)

    def signal_emit(self, sig, bus_str, time_delta_diff):
        self.signal_presenter.emit(sig, bus_str, time_delta_diff)

    def state_check(self):
        # driving state check
        if self.parent.btn_start.isChecked() and self.parent.btn_gear_d.isChecked() and self.parent.chkbox_pt_ready.isChecked():
            self.parent.btn_drv_state.setText("On Driving State")
        else:
            self.parent.btn_drv_state.setText("Set Driving State")

        # OTA condition check
        if self.parent.chkbox_h_brake.isChecked() and self.parent.btn_gear_n.isChecked():
            self.parent.btn_ota_cond.setText("On OTA Condition")
        else:
            self.parent.btn_ota_cond.setText("Set OTA Condition")

    def slider_speed_func(self, value):
        speed = f'Speed : {value} km/h'
        if self._isRunning:
            self.parent.label_speed.setText(speed)
            self.parent.pms_bodycont_c_worker.value = hex(int(value / (1 / 256)))[2:].zfill(4)
            self.parent.ic_tachospeed_worker.value = hex(int(value / (1 / 256)))[2:].zfill(4)

    def slider_battery_func(self, value):
        if self._isRunning:
            if value % 2 == 1 and value != 0:
                new_value = value + 1
            else:
                new_value = value
            battery = f'Battery : {new_value} %'
            self.parent.pms_vri_worker.value = new_value
            self.parent.label_battery.setText(battery)
            self.parent.bms_batt_worker.value = hex(int(new_value / 0.4))[2:].zfill(2)

    def slider_stwhl_func(self, value):
        if self._isRunning:
            value -= (value - 128) * 2
            self.parent.pms_c_strwhl_worker.value = value


class PMS_S_HVSM(NodeThread):
    pms_s_hvsm_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x18ffa57f

    def thread_func(self):  # HVSM_MMIFbSts
        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.pms_s_hvsm_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.pms_s_hvsm_signal.emit("C-CAN bus error (PMS_S - HVSM)", 0xFF, self.data, 0)
            self.parent.pms_s_hvsm_worker._isRunning = False


class PMS_C_StrWhl(NodeThread):
    pms_c_strwhl_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.send_id = 0x0cffb291
        self.data[0] = 0x00
        self.data[1] = 0x00
        self.value = 128

    def thread_func(self):  # SasChas1Fr01
        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.data[1] = self.value
            self.pms_c_strwhl_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.pms_c_strwhl_signal.emit("C-CAN bus error (PMS_C - StrWhl)", 0xFF, self.data, 0)
            self.parent.pms_c_strwhl_worker._isRunning = False


class BCM_MMI(NodeThread):
    bcm_mmi_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.single_tx_side_mani = None
        self.single_tx_softswset = None
        self.send_id = 0x18ffd521

    def thread_func(self):
        if self.data[3] == 0xFF:
            self.data[3] = 0x01

        if self.single_tx_side_mani:
            if self.single_tx_side_mani == 0xf4:
                self.data[3] = sig_gen.binary_sig(self.data[3], 0, 2, 1)
            elif self.single_tx_side_mani == 0xf8:
                self.data[3] = sig_gen.binary_sig(self.data[3], 0, 2, 2)

        if self.single_tx_softswset:
            if self.single_tx_softswset[3] == 0xcf:
                self.data[1] = 0xE7
            elif self.single_tx_softswset[3] == 0xd7:
                self.data[1] = 0xEB
            elif self.single_tx_softswset[3] == 0xdf:
                self.data[1] = 0xEF
            else:
                self.data[1] = 0xE3

            if self.single_tx_softswset[7] == 0x7f:
                self.data[3] = sig_gen.binary_sig(self.data[3], 2, 2, 1)
            elif self.single_tx_softswset[7] == 0xbf:
                self.data[3] = sig_gen.binary_sig(self.data[3], 2, 2, 2)

        if self.parent.btn_mscs_ok.isChecked():
            self.data[3] = sig_gen.binary_sig(self.data[3], 4, 3, 0)
        elif self.parent.btn_mscs_CmnFail.isChecked():
            self.data[3] = sig_gen.binary_sig(self.data[3], 4, 3, 1)
        elif self.parent.btn_mscs_NotEdgePress.isChecked():
            self.data[3] = sig_gen.binary_sig(self.data[3], 4, 3, 2)
        elif self.parent.btn_mscs_EdgeSho.isChecked():
            self.data[3] = sig_gen.binary_sig(self.data[3], 4, 3, 3)
        elif self.parent.btn_mscs_SnsrFltT.isChecked():
            self.data[3] = sig_gen.binary_sig(self.data[3], 4, 3, 4)
        elif self.parent.btn_mscs_FltPwrSplyErr.isChecked():
            self.data[3] = sig_gen.binary_sig(self.data[3], 4, 3, 5)
        elif self.parent.btn_mscs_FltSwtHiSide.isChecked():
            self.data[3] = sig_gen.binary_sig(self.data[3], 4, 3, 6)
        elif self.parent.btn_mscs_SigFailr.isChecked():
            self.data[3] = sig_gen.binary_sig(self.data[3], 4, 3, 7)

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.bcm_mmi_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.bcm_mmi_signal.emit("C-CAN bus error (BCM - MMI)", 0xFF, self.data, 0)
            self.parent.bcm_mmi_worker._isRunning = False


class BCM_SWRC(NodeThread):
    bcm_swrc_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.long_count = 0
        self.reset_count = 0
        self.long_threshold = 40
        self.count = 0
        self.btn_name = None
        self.send_id = 0x18fa7f21
        self.reset_flag = False

    def thread_func(self):  # SWS-LIN
        self.data[0] = 0x00
        self.data[1] = 0x00

        if self.parent.btn_reset.isChecked():
            self.reset_flag = True
            self.parent.btn_reset.setText("Reset\npressed")
        else:
            self.reset_flag = False
            self.reset_count = 0
            self.parent.btn_reset.setText("Reset")

        if self.btn_name:
            if self.btn_name == "btn_ok":
                self.data[0] = 0x01
            elif self.btn_name == "btn_undo":
                self.data[0] = 0x20
            elif self.btn_name == "btn_mode":
                self.data[0] = 0x40
            elif self.btn_name == "btn_mute":
                self.data[0] = 0x80
            elif self.btn_name == "btn_left":
                if self.long_count < self.long_threshold:
                    self.data[0] = 0x02
                    self.long_count += 1
                else:
                    self.data[0] = 0x04
            elif self.btn_name == "btn_right":
                if self.long_count < self.long_threshold:
                    self.data[0] = 0x08
                    self.long_count += 1
                else:
                    self.data[0] = 0x10
            elif self.btn_name == "btn_call":
                if self.long_count < self.long_threshold:
                    self.data[1] = 0x01
                    self.long_count += 1
                else:
                    self.data[1] = 0x02
            elif self.btn_name == "btn_vol_up":
                if self.long_count < self.long_threshold:
                    self.data[1] = 0x10
                    self.long_count += 1
                else:
                    self.data[1] = 0x20
            elif self.btn_name == "btn_vol_down":
                if self.long_count < self.long_threshold:
                    self.data[1] = 0x40
                    self.long_count += 1
                else:
                    self.data[1] = 0x80
        else:
            self.long_count = 0

        if self.reset_flag:
            if self.reset_count < self.long_threshold:
                self.data[0] = 0x02
                self.data[1] = 0x40
                self.reset_count += 1
            elif self.reset_count > 180:
                self.parent.btn_reset.setChecked(False)
                self.reset_count = 0
            else:
                self.data[0] = 0x04
                self.data[1] = 0x80
                self.reset_count += 1

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.bcm_swrc_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.bcm_swrc_signal.emit("C-CAN bus error (BCM - SWRC)", 0xFF, self.data, 0)
            self.parent.bcm_swrc_worker._isRunning = False


class BCM_StrWhl_Heat(NodeThread):
    bcm_strwhl_heat_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x18ff0721

    def thread_func(self):  # SwmCem_LinFr02
        self.data[0] = 0xFB  # need to fix

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.bcm_strwhl_heat_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.bcm_strwhl_heat_signal.emit("C-CAN bus error (BCM - StrWhl_Heat)", 0xFF, self.data, 0)
            self.parent.bcm_strwhl_heat_worker._isRunning = False


class BCM_LightChime(NodeThread):
    bcm_lightchime_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.send_id = 0x18ff8721
        self.data[0] = 0xCF
        self.data[1] = 0xF7

    def thread_func(self):  # BCM_LightChileReq
        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.bcm_lightchime_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.bcm_lightchime_signal.emit("C-CAN bus error (BCM - LightChime)", 0xFF, self.data, 0)
            self.parent.bcm_lightchime_worker._isRunning = False


class BCM_StateUpdate(NodeThread):
    bcm_stateupdate_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x18ff8621
        self.data[0] = 0x97
        self.data[1] = 0x7A

    def thread_func(self):  # BCM_StateUpdate

        # Initial mode for ACC (for convenience)
        if self.parent.btn_acc.isChecked():
            self.data[4] = 0xF9
        if self.parent.btn_acc_off.isChecked():
            self.data[4] = 0xF8
        elif self.parent.btn_ign.isChecked():
            self.data[4] = 0xFA
        elif self.parent.btn_start.isChecked():
            self.data[4] = 0xFC

        if self.parent.btn_bright_afternoon.isChecked():
            self.data[2] = 0xDF
        elif self.parent.btn_bright_night.isChecked():
            self.data[2] = 0xFF

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.bcm_stateupdate_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.bcm_stateupdate_signal.emit("C-CAN bus error (BCM - StateUpdate)", 0xFF, self.data, 0)
            self.parent.bcm_stateupdate_worker._isRunning = False


class PMS_BodyCont_C(NodeThread):
    pms_bodycont_c_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.value = '0000'
        self.send_id = 0x0cfab127
        self.data[0] = 0xBF
        self.data[6] = 0xF7

    def thread_func(self):  # PMS_BodyControlInfo (C-CAN)
        self.data[1] = int(self.value[2:4], 16)
        self.data[2] = int(self.value[0:2], 16)

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.pms_bodycont_c_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.pms_bodycont_c_signal.emit("C-CAN bus error (PMS - BodyCont CCAN)", 0xFF, self.data, 0)
            self.parent.pms_bodycont_c_worker._isRunning = False


class PMS_PTInfo(NodeThread):
    pms_ptinfo_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.value = '0000'
        self.send_id = 0x18fab027
        self.data[6] = 0xF3
        self.data[7] = 0x3F
        self.dist_init = True

    def thread_func(self):  # PMS_PTInfoIndicate
        self.data[5] = 0xFC

        # initial value for gear N (for convenience)
        if self.parent.btn_gear_n.isChecked():
            self.data[4] = 0x7D
        elif self.parent.btn_gear_r.isChecked():
            self.data[4] = 0xDF
        elif self.parent.btn_gear_d.isChecked():
            self.data[4] = 0xFC

        if self.parent.chkbox_pt_ready.isChecked():
            self.data[0] = 0xDF
            if self.dist_init:
                self.parent.ic_distance_worker.dist_init = True
            else:
                self.parent.btn_0th_byte_up.setEnabled(True)
                self.parent.btn_1st_byte_up.setEnabled(True)
        else:
            self.data[0] = 0xCF
            self.parent.btn_0th_byte_up.setEnabled(False)
            self.parent.btn_1st_byte_up.setEnabled(False)

        if self.parent.chkbox_h_brake.isChecked():
            self.data[5] = 0xFD

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.pms_ptinfo_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.pms_ptinfo_signal.emit("C-CAN bus error (PMS - PTInfo)", 0xFF, self.data, 0)
            self.parent.pms_ptinfo_worker._isRunning = False


class PMS_BodyCont_P(NodeThread):
    pms_bodycont_p_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.send_id = 0x0cfab127
        self.data[4] = 0x00

    def thread_func(self):  # PMS_BodyControlInfo (P-CAN)
        if self.parent.p_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.pms_bodycont_p_signal.emit('p', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.pms_bodycont_p_signal.emit("P-CAN bus error (PMS - BodyCont PCAN)", 0xFF, self.data, 0)
            self.parent.pms_bodycont_p_worker._isRunning = False


class PMS_VRI(NodeThread):
    pms_vri_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.send_id = 0x18fab327
        self.value = 50
        self.data[2] = 0x00
        self.data[3] = 0x00

    def thread_func(self):  # PMS_VRI
        unit_dist = self.value * 3 * 0x08
        unit_dist_quotient = int(unit_dist / 0xFF)
        unit_dist_remainder = unit_dist % 0xFF
        if self.value == 100:
            unit_dist_remainder = unit_dist % 0xFF - 2
        self.data[0] = unit_dist_remainder
        self.data[1] = unit_dist_quotient

        if self.parent.p_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.pms_vri_signal.emit('p', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.pms_vri_signal.emit("P-CAN bus error (PMS - VRI)", 0xFF, self.data, 0)
            self.parent.pms_vri_worker._isRunning = False


class FCS_AEB(NodeThread):
    fcs_aeb_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.single_tx = None
        self.send_id = 0x0cf02fa0

    def thread_func(self):  # FCS_AEBS1
        if self.single_tx:
            if self.single_tx == 0xfd:
                self.data[0] = 0xF3
            elif self.single_tx == 0xfc:
                self.data[0] = 0xF2

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.fcs_aeb_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.fcs_aeb_signal.emit("C-CAN bus error (FCS - AEB)", 0xFF, self.data, 0)
            self.parent.fcs_aeb_worker._isRunning = False


class FCS_LDW(NodeThread):
    fcs_ldw_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.single_tx = None
        self.send_id = 0x18fe5be8
        self.data[1] = 0xF0

    def thread_func(self):  # FCS_FLI2
        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.fcs_ldw_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.fcs_ldw_signal.emit("C-CAN bus error (FCS - LDW)", 0xFF, self.data, 0)
            self.parent.fcs_ldw_worker._isRunning = False


class IC_TachoSpeed(NodeThread):
    ic_tachospeed_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.value = '0000'
        self.send_id = 0x0cfe6c17

    def thread_func(self):
        self.data[6] = int(self.value[2:4], 16)
        self.data[7] = int(self.value[0:2], 16)

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.ic_tachospeed_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.ic_tachospeed_signal.emit("C-CAN bus error (IC - TachoSpeed)", 0xFF, self.data, 0)
            self.parent.ic_tachospeed_worker._isRunning = False


class IC_Distance(NodeThread):  # need to fix
    ic_distance_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 1.000
        self.send_id = 0x18fec117
        # need to fix (byte position 0~3)
        self.data[0] = 0x00
        self.data[1] = 0x00
        self.data[2] = 0x00
        self.data[3] = 0x00
        self.dist_0_up = 0
        self.dist_1_up = 0
        self.dist_init = False

    def thread_func(self):
        if self.parent.c_can_bus:
            if self.dist_init:
                self.data[0] += 0x01
                if self.data[0] > 0x01:
                    self.parent.pms_ptinfo_worker.dist_init = False
                    self.dist_init = False

            self.data[0] = self.dist_0_up * 0x01
            self.data[1] = self.dist_1_up * 0x01
            time_delta = self.calc_delta(self.send_id, time.time())
            self.ic_distance_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.ic_distance_signal.emit("C-CAN bus error (IC - Distance)", 0xFF, self.data, 0)
            self.parent.ic_distance_worker._isRunning = False


class ESC_TPMS(NodeThread):
    esc_tpms_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.send_id = 0x18f0120B
        self.tpms_val = 0
        self.tpms_count = 0

    def thread_func(self):
        self.data[7] = 0xCF
        if self.tpms_val == 1:
            self.data[7] = 0xDF
            self.tpms_count += 1
        elif self.tpms_val == 2:
            self.data[7] = 0xEF
            self.tpms_count += 1

        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.esc_tpms_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
            if self.tpms_count > 10:
                self.tpms_count = 0
                self.tpms_val = 0
        else:
            self.esc_tpms_signal.emit("C-CAN bus error (ESC - TPMS)", 0xFF, self.data, 0)
            self.parent.esc_tpms_worker._isRunning = False


class ACU_SeatBelt(NodeThread):
    acu_seatbelt_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.200
        self.send_id = 0x18fac490

    def thread_func(self):
        if self.parent.c_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.acu_seatbelt_signal.emit('c', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.acu_seatbelt_signal.emit("C-CAN bus error (ACU - Seatbelt)", 0xFF, self.data, 0)
            self.parent.acu_seatbelt_worker._isRunning = False

    def drv_invalid(self):
        if self.parent.chkbox_drv_invalid.isChecked():
            self.data[1] = sig_gen.binary_sig(self.data[1], 7, 1, 1)
        else:
            self.data[1] = sig_gen.binary_sig(self.data[1], 7, 1, 0)

    def pass_invalid(self):
        if self.parent.chkbox_pass_invalid.isChecked():
            self.data[1] = sig_gen.binary_sig(self.data[1], 6, 1, 1)
        else:
            self.data[1] = sig_gen.binary_sig(self.data[1], 6, 1, 0)


class BMS_Batt(NodeThread):
    bms_batt_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.value = '7D'
        self.send_id = 0x18fa40f4

    def thread_func(self):
        self.data[0] = 0x00
        self.data[1] = 0x00
        self.data[2] = 0x00
        self.data[3] = 0x7D
        self.data[4] = int(self.value, 16)
        self.data[5] = 0x7D

        if self.parent.p_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.bms_batt_signal.emit('p', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.bms_batt_signal.emit("P-CAN bus error (BMS - Battery)", 0xFF, self.data, 0)
            self.parent.bms_batt_worker._isRunning = False


class BMS_Charge(NodeThread):
    bms_charge_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x18fa3ef4
        self.data[1] = 0xFC

    def thread_func(self):
        self.data[0] = 0x0F
        if self.parent.chkbox_charge.isChecked():
            self.data[0] = 0x1F

        if self.parent.p_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.bms_charge_signal.emit('p', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.bms_charge_signal.emit("P-CAN bus error (BMS - Charging)", 0xFF, self.data, 0)
            self.parent.bms_charge_worker._isRunning = False


class MCU_Motor(NodeThread):
    mcu_motor_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x0cfa01ef
        self.data[4] = 0x00
        self.data[5] = 0x00

    def thread_func(self):
        if self.parent.p_can_bus:
            time_delta = self.calc_delta(self.send_id, time.time())
            self.mcu_motor_signal.emit('p', self.send_id, self.data, time_delta)
            time.sleep(self.period)
        else:
            self.mcu_motor_signal.emit("P-CAN bus error (MCU - Motor)", 0xFF, self.data, 0)
            self.parent.mcu_motor_worker._isRunning = False


class TesterPresent(NodeThread):
    tester_signal = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.period = 4.0
        self.send_id = 0x18da41f1

    def thread_func(self):
        if self.parent.tester_present_flag:
            self.data[0] = 0x02
            self.data[1] = 0x3E
            self.data[2] = 0x00
            self.tester_signal.emit(self.data)
            time.sleep(self.period)

            if self.parent.c_can_bus:
                self.tester_signal.emit(self.data)
                time.sleep(self.period)
            else:
                self.tester_signal.emit("C-CAN bus error (Diagnosis)", 0xFF, self.data)


class UserSignal(NodeThread):
    user_defined_signal = pyqtSignal(str, int, list, float)

    def __init__(self, parent):
        super().__init__(parent)
        # self.data = []
        self.bus_selector = None

    def thread_func(self):
        time_delta = self.calc_delta(self.send_id, time.time())
        if self.bus_selector == "C-CAN":
            self.bus_selector = "c"
        elif self.bus_selector == "P-CAN":
            self.bus_selector = "p"
        self.user_defined_signal.emit(self.bus_selector, self.send_id, self.data, time_delta)
