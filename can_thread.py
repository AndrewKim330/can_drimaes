import copy
import time
import uptime

import can
import can.interfaces.vector
import can.interfaces.pcan
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap

import threading

import images_rc


def sig_generator(hex_val, pos, bit_len, val):
    tt = bin(hex_val)[2:].zfill(8)
    val_bin = bin(val)[2:].zfill(bit_len)
    if pos > 0:
        temp = tt[:pos] + val_bin + tt[pos + len(val_bin):]
    else:
        temp = val_bin + tt[pos + len(val_bin):]
    return int(temp, 2)


class NodeThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._isRunning = True
        self.period = 0.100
        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    def run(self):
        while self._isRunning:
            self.thread_func()
            time.sleep(self.period)

    def thread_func(self):
        pass

    def stop(self):
        self._isRunning = False


class ThreadWorker(NodeThread):
    sig2 = pyqtSignal(can.Message)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._isRunning = True
        self.reservoir = []
        self.period = 0.050

    def run(self):
        while self._isRunning:
            a = self.parent.c_can_bus.recv()
            if a.arbitration_id == 0x18daf141:
                self.reservoir.append(a)
            self.sig2.emit(a)
            QtCore.QCoreApplication.processEvents()

    def thread_func(self):
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
            self.parent.slider_speed.setValue(value)
            self.parent.label_speed.setText(speed)
            self.parent.speed_worker.value = hex(int(value / (1 / 256)))[2:].zfill(4)

    def slider_battery_func(self, value):
        if self._isRunning:
            if value % 2 == 1 and value != 0:
                new_value = value + 1
            else:
                new_value = value
            battery = f'Battery : {new_value} %'
            self.parent.slider_battery.setValue(new_value)
            self.parent.label_battery.setText(battery)
            self.parent.battery_worker.value = hex(int(new_value / 0.4))[2:].zfill(2)


class Hvac(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.sig = '0x00'

    def run(self):
        while self._isRunning:
            if self.parent.c_can_bus:
                a = self.parent.c_can_bus.recv()
                if a.arbitration_id == 0x18ffd741:  # 100ms
                    self.data[0] = a.data[1]
                    self.thread_func()
            else:
                print("no good hvac")
                self._isRunning = False

    def thread_func(self):
        message = can.Message(arbitration_id=0x18ffa57f, data=self.data)
        self.parent.c_can_bus.send(message)


class Swrc(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.long_count = 0
        self.long_threshold = 40

    def thread_func(self):
        self.data[0] = 0x00
        self.data[1] = 0x00
        if self.parent.btn_left_long.isChecked():
            if self.long_count < self.long_threshold:
                self.data[0] = 0x02
                self.long_count += 1
            else:
                self.data[0] = 0x04
        elif self.parent.btn_right_long.isChecked():
            if self.long_count < self.long_threshold:
                self.data[0] = 0x08
                self.long_count += 1
            else:
                self.data[0] = 0x10
        elif self.parent.btn_call_long.isChecked():
            if self.long_count < self.long_threshold:
                self.data[1] = 0x01
                self.long_count += 1
            else:
                self.data[1] = 0x02
        elif self.parent.btn_vol_up_long.isChecked():
            if self.long_count < self.long_threshold:
                self.data[1] = 0x10
                self.long_count += 1
            else:
                self.data[1] = 0x20
        elif self.parent.btn_vol_down_long.isChecked():
            if self.long_count < self.long_threshold:
                self.data[1] = 0x40
                self.long_count += 1
            else:
                self.data[1] = 0x80
        elif self.parent.btn_reset.isChecked():
            if self.long_count < self.long_threshold:
                self.data[0] = 0x02
                self.data[1] = 0x40
                self.long_count += 1
            else:
                self.data[0] = 0x04
                self.data[1] = 0x80
        else:
            self.long_count = 0

        if self.sender():
            btn_text = self.sender().objectName()
            if btn_text == "btn_ok":
                self.data[0] = 0x01
            elif btn_text == "btn_left":
                self.data[0] = 0x02
            elif btn_text == "btn_right":
                self.data[0] = 0x08
            elif btn_text == "btn_undo":
                self.data[0] = 0x20
            elif btn_text == "btn_mode":
                self.data[0] = 0x40
            elif btn_text == "btn_mute":
                self.data[0] = 0x80
            elif btn_text == "btn_call":
                self.data[1] = 0x01
            elif btn_text == "btn_vol_up":
                self.data[1] = 0x10
            elif btn_text == "btn_vol_down":
                self.data[1] = 0x40
        message = can.Message(arbitration_id=0x18fa7f21, data=self.data)
        if self.parent.c_can_bus:
            self.parent.c_can_bus.send(message)
        else:
            print("no good swrc")
            self._isRunning = False


class PowerTrain(NodeThread):
    def thread_func(self):
        self.data[0] = 0xCF
        self.data[5] = 0xFC
        self.data[6] = 0xF3
        self.data[7] = 0x3F
        # initial value for gear N (for convenience)
        if self.parent.btn_gear_n.isChecked():
            self.data[4] = 0x7D
        elif self.parent.btn_gear_r.isChecked():
            self.data[4] = 0xDF
        elif self.parent.btn_gear_d.isChecked():
            self.data[4] = 0xFC
        if self.parent.chkbox_pt_ready.isChecked():
            self.data[0] = 0xDF
        message = can.Message(arbitration_id=0x18fab027, data=self.data)
        if self.parent.c_can_bus:
            self.parent.c_can_bus.send(message)
        else:
            print("no good powertrain")
            self._isRunning = False


class BCMState(NodeThread):
    def thread_func(self):
        self.data[0] = 0x97
        self.data[1] = 0x7A
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
        message = can.Message(arbitration_id=0x18ff8621, data=self.data)
        if self.parent.c_can_bus:
            self.parent.c_can_bus.send(message)
        else:
            print("no good bcmstate")
            self._isRunning = False


class BCMMMI(NodeThread):
    def thread_func(self):
        if self.data[3] == 0xFF:
            self.data[3] = 0x01
        if self.parent.c_can_bus:
            a = self.parent.c_can_bus.recv()
            if a.arbitration_id == 0x18ffd741:
                if a.data[2] == 0xf4:
                    self.data[3] = sig_generator(self.data[3], 0, 2, 1)
                elif a.data[2] == 0xf8:
                    self.data[3] = sig_generator(self.data[3], 0, 2, 2)
            if a.arbitration_id == 0x18ffd841:
                if a.data[3] == 0xcf:
                    self.data[1] = 0xE7
                elif a.data[3] == 0xd7:
                    self.data[1] = 0xEB
                elif a.data[3] == 0xdf:
                    self.data[1] = 0xEF
                else:
                    self.data[1] = 0xE3

                if a.data[7] == 0x7f:
                    self.data[3] = sig_generator(self.data[3], 2, 2, 1)
                elif a.data[7] == 0xbf:
                    self.data[3] = sig_generator(self.data[3], 2, 2, 2)

            if self.parent.btn_mscs_ok.isChecked():
                self.data[3] = sig_generator(self.data[3], 4, 3, 0)
            elif self.parent.btn_mscs_CmnFail.isChecked():
                self.data[3] = sig_generator(self.data[3], 4, 3, 1)
            elif self.parent.btn_mscs_NotEdgePress.isChecked():
                self.data[3] = sig_generator(self.data[3], 4, 3, 2)
            elif self.parent.btn_mscs_EdgeSho.isChecked():
                self.data[3] = sig_generator(self.data[3], 4, 3, 3)
            elif self.parent.btn_mscs_SnsrFltT.isChecked():
                self.data[3] = sig_generator(self.data[3], 4, 3, 4)
            elif self.parent.btn_mscs_FltPwrSplyErr.isChecked():
                self.data[3] = sig_generator(self.data[3], 4, 3, 5)
            elif self.parent.btn_mscs_FltSwtHiSide.isChecked():
                self.data[3] = sig_generator(self.data[3], 4, 3, 6)
            elif self.parent.btn_mscs_SigFailr.isChecked():
                self.data[3] = sig_generator(self.data[3], 4, 3, 7)

            message = can.Message(arbitration_id=0x18ffd521, data=self.data)

            self.parent.c_can_bus.send(message)
        else:
            print("no good bcm mmi")
            self._isRunning = False


class TachoSpeed(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.value = '0000'

    def thread_func(self):
        self.data[6] = int(self.value[2:4], 16)
        self.data[7] = int(self.value[0:2], 16)
        message = can.Message(arbitration_id=0x0cfe6c17, data=self.data)
        if self.parent.c_can_bus:
            self.parent.c_can_bus.send(message)
        else:
            print("no good tachospeed")
            self._isRunning = False


class TirePressure(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010

    def thread_func(self):
        self.data[7] = 0xCF
        if self.sender():
            btn_text = self.sender().objectName()
            if btn_text == "btn_tpms_success":
                self.data[7] = 0xDF
            elif btn_text == "btn_tpms_fail":
                self.data[7] = 0xEF
        message = can.Message(arbitration_id=0x18f0120B, data=self.data)
        if self.parent.c_can_bus:
            self.parent.c_can_bus.send(message)
        else:
            print("no good tire pressure")
            self._isRunning = False


class AEB(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050

    def thread_func(self):
        if self.parent.c_can_bus:
            a = self.parent.c_can_bus.recv()
            if a.arbitration_id == 0x0c0ba021:
                if a.data[0] == "fd":
                    self.data[0] = 0xF1
                elif a.data[0] == "fc":
                    self.data[0] = 0xF2
            message = can.Message(arbitration_id=0x0cf02fa0, data=self.data)
            self.parent.c_can_bus.send(message)
        else:
            print("no good AEB")
            self._isRunning = False


class ACU(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.200

    def thread_func(self):
        message = can.Message(arbitration_id=0x18fac490, data=self.data)
        if self.parent.c_can_bus:
            self.parent.c_can_bus.send(message)
        else:
            print("no good ACU")
            self._isRunning = False

    def drv_invalid(self):
        if self.parent.chkbox_drv_invalid.isChecked():
            self.data[1] = sig_generator(self.data[1], 7, 1, 1)
        else:
            self.data[1] = sig_generator(self.data[1], 7, 1, 0)

    def pass_invalid(self):
        if self.parent.chkbox_pass_invalid.isChecked():
            self.data[1] = sig_generator(self.data[1], 6, 1, 1)
        else:
            self.data[1] = sig_generator(self.data[1], 6, 1, 0)


class BatteryManage(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.value = '7D'

    def thread_func(self):
        self.data[2] = 0x00
        self.data[3] = 0x7D
        self.data[4] = int(self.value, 16)
        self.data[5] = 0x7D
        message = can.Message(arbitration_id=0x18fa40f4, data=self.data)
        if self.parent.p_can_bus:
            self.parent.p_can_bus.send(message)
        else:
            print("no good battery")
            self._isRunning = False


class ChargingState(NodeThread):
    def thread_func(self):
        self.data[0] = 0x0F
        self.data[1] = 0xFC
        if self.parent.chkbox_charge.isChecked():
            self.data[0] = 0x1F
        message = can.Message(arbitration_id=0x18fa3ef4, data=self.data)
        if self.parent.p_can_bus:
            self.parent.p_can_bus.send(message)
        else:
            print("no good charge")
            self._isRunning = False


class TesterPresent(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 4.0

    def thread_func(self):
        if self.parent.chkbox_tester_present.isChecked():
            self.data[0] = 0x02
            self.data[1] = 0x3E
            self.data[2] = 0x00
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            if self.parent.c_can_bus:
                self.parent.c_can_bus.send(message)
            else:
                print("no good charge")
                self._isRunning = False

        # pixmap = QPixmap(':/icon/OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # self.sig_side_mirrorb = QPixmap(':/icon/OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # pixmap.save("aaa.jpg")
        # pixmap2 = QPixmap()
        # pixmap2.load('./OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # print(pixmap)
        # self.parent.test_label.setPixmap(pixmap)
        # self.parent.test_label.setPixmap(pixmap2)
        # self.parent.test_label.setPixmap(self.sig_side_mirrorb)