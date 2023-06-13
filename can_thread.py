import copy
import time
import uptime

import can
import can.interfaces.vector
import can.interfaces.pcan
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap

import threading

import images_rc


def sig_generator(hex_val, pos, bit_len, val):
    tt = bin(hex_val)[2:].zfill(8)
    val_bin = bin(val)[2:].zfill(bit_len)
    if pos > 0:
        temp = tt[pos - 1] + val_bin + tt[pos + len(val_bin):]
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


class TxOnlyWorker(QThread):
    sig2 = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.abc = None
        self.parent = parent
        self._isRunning = True

    def run(self):
        while self._isRunning:
            if self.parent.c_can_bus:
                a = str(self.parent.c_can_bus.recv()).split()
                # print(self.parent.c_can_bus.recv())
                # self.parent.mmi_console.appendPlainText(str(a))
                self.sig2.emit(a)
            else:
                print("no good")
                self._isRunning = False

    # @pyqtSlot("PyQt_PyObject")
    # def good2(self, good2):
    #     pass
    #     print(good2)

    def stop(self):
        self._isRunning = False


class Hvac(NodeThread):

    def __init__(self, parent):
        super().__init__(parent)
        self.sig = '0x00'

    def run(self):
        while self._isRunning:
            if self.parent.c_can_bus:
                a = str(self.parent.c_can_bus.recv()).split()
                if a[3] == "18ffd741":  # 100ms
                    self.sig = a[9]
                    self.thread_func()
            else:
                print("no good hvac")
                self._isRunning = False

    def thread_func(self):
        self.data[0] = int(self.sig, 16)
        message = can.Message(arbitration_id=0x18ffa57f, data=self.data)
        self.parent.c_can_bus.send(message)


class Swrc(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050

    def thread_func(self):
        self.data[0] = 0x00
        self.data[1] = 0x00
        if self.sender():
            btn_text = self.sender().objectName()
            if btn_text == "btn_ok":
                self.data[0] = 0x01
            elif btn_text == "btn_left":
                self.data[0] = 0x02
            elif btn_text == "btn_left_long":
                self.data[0] = 0x04
            elif btn_text == "btn_right":
                self.data[0] = 0x08
            elif btn_text == "btn_right_long":
                self.data[0] = 0x10
            elif btn_text == "btn_undo":
                self.data[0] = 0x20
            elif btn_text == "btn_mode":
                self.data[0] = 0x40
            elif btn_text == "btn_mute":
                self.data[0] = 0x80
            elif btn_text == "btn_call":
                self.data[1] = 0x01
            elif btn_text == "btn_call_long":
                self.data[1] = 0x02
            elif btn_text == "btn_vol_up":
                self.data[1] = 0x10
            elif btn_text == "btn_vol_up_long":
                self.data[1] = 0x20
            elif btn_text == "btn_vol_down":
                self.data[1] = 0x40
            elif btn_text == "btn_vol_down_long":
                self.data[1] = 0x80
            elif btn_text == "btn_reset":
                self.data[0] = 0x04
                self.data[1] = 0x80
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
        self.data[3] = 0x01
        a = str(self.parent.c_can_bus.recv()).split()
        if a[3] == "18ffd741":
            if a[10] == 'f4':
                # print("aaa")
                self.data[3] = sig_generator(self.data[3], 0, 2, 1)
            elif a[10] == 'f8':
                self.data[3] = sig_generator(self.data[3], 0, 2, 2)
        if a[3] == "18ffd841":
            if a[11] == "c7":
                self.data[1] = 0xE3
            elif a[11] == "cf":
                self.data[1] = 0xE7
            elif a[11] == "d7":
                self.data[1] = 0xEB
            elif a[11] == "df":
                self.data[1] = 0xEF

            if a[15] == "7f":
                self.data[3] = sig_generator(self.data[3], 2, 2, 1)
            elif a[15] == "bf":
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

        if self.parent.c_can_bus:
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
            print("no good tirepressure")
            self._isRunning = False


class AEB(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050

    def thread_func(self):
        a = str(self.parent.c_can_bus.recv()).split()
        if a[8] == "fd":
            self.data[0] = 0xF1
        elif a[8] == "fc":
            self.data[0] = 0xF2
        message = can.Message(arbitration_id=0x0cf02fa0, data=self.data)
        if self.parent.c_can_bus:
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


class ThreadWorker(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.diag_state = None
        self.diag_btn_text = None
        self.diag_success_byte = None
        self.diag_failure_byte = "7f"

    def run(self):
        while self._isRunning:
            self.thread_func()

    def thread_func(self):
        a = str(self.parent.c_can_bus.recv()).split()
        if a[3] == "18daf141":
            self.parent.diag_console.appendPlainText(str(a))
            if self.diag_state == "sess_cont":
                self.diag_sess(self.diag_btn_text, a)


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

        if a[3] == "0c0ba021":
            self.parent.aeb_worker.value = a[8]

    def slider_speed_func(self, value):
        speed = f'Speed : {value} km/h'
        if self._isRunning:
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

    def diag_func(self):
        if self.sender():
            self.diag_btn_text = self.sender().objectName()
            if self.diag_btn_text == "btn_sess_default" or self.diag_btn_text == "btn_sess_extended" or self.diag_btn_text == "btn_nrc_sess_12" or self.diag_btn_text == "btn_nrc_sess_13":
                self.diag_state = "sess_cont"
                self.diag_success_byte = "50"
                self.diag_sess(self.diag_btn_text)

    def diag_sess(self, txt=None, res=None):
        if txt:
            if txt == "btn_sess_default":
                if res:
                    if res[9] == self.diag_success_byte:
                        if res[10] == "01":
                            self.parent.btn_sess_default.setEnabled(False)
                            self.parent.label_sess_default.setText("Success")
                else:
                    self.data[0] = 0x02
                    self.data[1] = 0x10
                    self.data[2] = 0x01
            elif txt == "btn_sess_extended":
                if res:
                    if res[9] == self.diag_success_byte:
                        if res[10] == "03":
                            self.parent.btn_sess_extended.setEnabled(False)
                            self.parent.label_sess_extended.setText("Success")
                else:
                    self.data[0] = 0x02
                    self.data[1] = 0x10
                    self.data[2] = 0x03
            elif txt == "btn_nrc_sess_12":
                print("aaa")
                if res:
                    if res[9] == self.diag_failure_byte:
                        if res[10] == "10" and res[11] == "12":
                            self.parent.btn_nrc_sess_12.setEnabled(False)
                            self.parent.label_nrc_sess_12.setText("Success")
                else:
                    self.data[0] = 0x02
                    self.data[1] = 0x10
                    self.data[2] = 0xFF
            elif txt == "btn_nrc_sess_13":
                if res:
                    if res[9] == self.diag_failure_byte:
                        if res[10] == "10" and res[11] == "13":
                            self.parent.btn_nrc_sess_13.setEnabled(False)
                            self.parent.label_nrc_sess_13.setText("Success")
                else:
                    self.data[0] = 0x03
                    self.data[1] = 0x10
                    self.data[2] = 0x01
                    self.data[3] = 0x01
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            self.parent.c_can_bus.send(message)


        # if res[9] == "50":



        # message = can.Message(arbitration_id=0x18da41f1, data=[0x03, 0x19, 0x01, 0x09, 0xFF, 0xFF, 0xFF, 0xFF])


        # pixmap = QPixmap(':/icon/OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # self.sig_side_mirrorb = QPixmap(':/icon/OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # pixmap.save("aaa.jpg")
        # pixmap2 = QPixmap()
        # pixmap2.load('./OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # print(pixmap)
        # self.parent.test_label.setPixmap(pixmap)
        # self.parent.test_label.setPixmap(pixmap2)
        # self.parent.test_label.setPixmap(self.sig_side_mirrorb)
        # self.parent.test_label.setText("Aaaaa")

    # def diagnosis(self):
    #     # session control
    #     self.parent.btn_sess_default.clicked.connect(self.session_cont)
    #     self.parent.btn_sess_ext.clicked.connect(self.session_cont)
    #
    # def session_cont(self):
    #     btn_text = self.sender().objectName()
    #     if len(btn_text) > 0:
    #         if btn_text == "btn_sess_default":
    #             message = can.Message(arbitration_id=0x18da41f1,
    #                                   data=[0x02, 0x10, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #         elif btn_text == "btn_sess_ext":
    #             message = can.Message(arbitration_id=0x18da41f1,
    #                                   data=[0x02, 0x10, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #         self.parent.c_can_bus1.send(message)
        # try:
        #     btn_text = self.sender().objectName()
        #     if len(btn_text) > 0:
        #         if btn_text == "def_sess":
        #             message = can.Message(arbitration_id=0x18da41f1,
        #                                   data=[0x02, 0x10, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        #         elif btn_text == "ext_sess":
        #             message = can.Message(arbitration_id=0x18da41f1,
        #                                   data=[0x02, 0x10, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        #         elif btn_text == "nrc_sess_12":
        #             message = can.Message(arbitration_id=0x18da41f1,
        #                                   data=[0x02, 0x10, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        #         elif btn_text == "nrc_sess_13":
        #             message = can.Message(arbitration_id=0x18da41f1,
        #                                   data=[0x03, 0x10, 0x01, 0x01, 0xFF, 0xFF, 0xFF, 0xFF])
        #         self.parent.c_can_bus.send(message)
        #     time.sleep(0.5)
        #     if l:
        #         data_str = str([l[8], l[9], l[10], l[11], l[12], l[13], l[14], l[15]])
        #         if l[9] == "50":
        #             pf_flag = "Success"
        #             if l[10] == "01":
        #                 sess_name = "Default"
        #                 self.def_sess_label.setText("Tested Success")
        #             elif l[10] == "03":
        #                 sess_name = "Extended"
        #                 self.ext_sess_label.setText("Tested Success")
        #             console_str = f'{sess_name} Session {pf_flag}'
        #         elif l[9] == "7f":
        #             if l[11] == "12":
        #                 reason = "Not Supported Subfunction"
        #                 self.nrc_sess_12_label.setText("Tested Success")
        #             elif l[11] == "13":
        #                 reason = "Data Length Error"
        #                 self.nrc_sess_13_label.setText("Tested Success")
        #             console_str = f'Diagnosis Error - {reason} (NRC Code : {l[11]})'
        #
        #         self.diag_console.appendPlainText(console_str)
        #         self.diag_console.appendPlainText(data_str)
        # except AttributeError:
        #     pass


# ************************************
# temp in run()
# ************************************
# sig1 = pyqtSignal(list)
# flowControl = False
# temp = []
# @pyqtSlot("PyQt_PyObject")
#     def good1(self, good1):
#         print(good1)
    #     # if good1 == 0xF8:
    #     # elif good1 == 0xF9:
    #     # elif good1 == 0xFA:
    #     # elif good1 == 0xFC:
    #             # message = 0
    #         # while True:
    #         #     print(good1)
    #             # message = can.Message(arbitration_id=0x18ff8621, data=[0x97, 0x7A, 0xDF, 0xFF, good1, 0xFF, 0xFF, 0xFF])
    #             # self.parent.c_can_bus.send_periodic(message, 0.1)
    #             # print(task)
    #             # time.sleep(0.1)
    #         # time.sleep(0.1)
    #
    #     # else:
    #     #     xor = [0x69, 0x1d, 0xbe, 0x55]
    #     #     cal_data = []
    #     #     res = []
    #     #     print("10 03 service")
    #     #     message = can.Message(arbitration_id=0x18da41f1, data=[0x02, 0x10, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #     #     self.parent.c_can_bus.send(message)
    #     #     time.sleep(1)
    #     #     print("27 01 service")
    #     #     message = can.Message(arbitration_id=0x18da41f1, data=[0x02, 0x27, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #     #     self.parent.c_can_bus.send(message)
    #     #     time.sleep(1)
    #     #     print(self.abc)
    #     #     new = []
    #     #     for i in range(4):
    #     #         temp = int(self.abc[i], 16) ^ xor[i]
    #     #         cal_data.append(temp)
    #     #     res.append(((cal_data[3] & 0x0f) << 4) | (cal_data[3] & 0xf0))
    #     #     res.append(((cal_data[1] & 0x0f) << 4) | ((cal_data[0] & 0xf0) >> 4))
    #     #     res.append((cal_data[1] & 0xf0) | ((cal_data[2] & 0xf0) >> 4))
    #     #     res.append(((cal_data[0] & 0x0f) << 4) | (cal_data[2] & 0x0f))
    #     #     time.sleep(1)
    #     #     message = can.Message(arbitration_id=0x18da41f1, data=[0x06, 0x27, 0x02, res[0], res[1], res[2], res[3], 0xFF])
    #     #     self.parent.c_can_bus.send(message)
    #     #     time.sleep(5)
    #     #     if good1 == "write":
    #     #         message = can.Message(arbitration_id=0x18da41f1, data=[0x10, 0x0B, 0x2E, 0xF1, 0x12, 0x41, 0x42, 0x43])
    #     #         self.parent.c_can_bus.send(message)
    #     #         time.sleep(0.5)
    #     #         message = can.Message(arbitration_id=0x18da41f1, data=[0x21, 0x44, 0x45, 0x46, 0x47, 0x48, 0xFF, 0xFF])
    #     #         self.parent.c_can_bus.send(message)
    #     #         time.sleep(0.5)
    #     #         message = can.Message(arbitration_id=0x18da41f1, data=[0x03, 0x22, 0xF1, 0x12, 0xFF, 0xFF, 0xFF, 0xFF])
    #     #         self.parent.c_can_bus.send(message)

            # print(b, now - start)
            # if now - start == 0.010:
            #     aaaa = now - start
            #     # print(aaaa)
            #     # print(aaaa)

    #     while True:
    #         start = time.time()
    #         a = str(self.parent.c_can_bus.recv()).split()
    #         if self.parent.acc_off.isChecked():
    #             power_sig = 0xF8
    #         elif self.parent.acc.isChecked():
    #             power_sig = 0xF9
    #         elif self.parent.ign.isChecked():
    #             power_sig = 0xFA
    #         elif self.parent.start.isChecked():
    #             power_sig = 0xFC
    #         message = can.Message(arbitration_id=0x18ff8621, data=[0x97, 0x7A, 0xDF, 0xFF, power_sig, 0xFF, 0xFF, 0xFF])
    #         self.parent.c_can_bus.send(message)
    #         # time.sleep(0.001)
    #         self.sig1.emit(a)
    #         # # print(a)
    #         # if a[3] == '18ff8621':
    #         #     print(a)
    #         # Seat HAVC
    #
    #             self.sig1.emit(a)
    #         # self.sig.emit(a)
    #         if a[3] == '18daf141':
    #             # print(a)
    #             if a[9] == "67" and a[10] == "01":
    #                 self.abc = [a[11], a[12], a[13], a[14]]
    #             # if a[9] == "67" and a[10] == "02":
    #             #     temp = [a[11], a[12], a[13], a[14]]
    #             #     print(temp)
    #             #     self.sig1.emit(temp)
    #             if flowControl:
    #                 temp.append(a)
    #             if a[8] == '10':
    #                 temp.append(a)
    #                 message = can.Message(arbitration_id=0x18da41f1, data=[0x30, 0x00, 0x00, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA])
    #                 self.parent.c_can_bus.send(message)
    #                 print("flow control")
    #                 flowControl = True
    #         if len(temp) == 10:
    #             print("good")
    #             # self.sig1.emit(temp)
    #             flowControl = False
    #             temp = []
    #         now = time.time()
    #         print(now - start)
    #
