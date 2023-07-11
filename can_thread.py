import time

import can
import can.interfaces.vector
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
        self.data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    def run(self):
        while self._isRunning:
            self.thread_func()
            QtCore.QCoreApplication.processEvents()

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

    def run(self):
        while self._isRunning:
            a = self.parent.c_can_bus.recv()
            if self.parent.chkbox_save_log.isChecked():
                self.parent.log_data.append(a)
            if a.arbitration_id == 0x18daf141:
                self.reservoir.append(a)
            if a.arbitration_id == 0x18ffd741:
                self.parent.pms_s_hvsm_worker.data[0] = a.data[1]
                hvsm_tx = bin(a.data[1])[2:].zfill(8)
                if int(hvsm_tx[6:], 2) == 3:
                    self.parent.txt_res_drv_heat.setPixmap(self.parent.img_drv_heat_3)
                elif int(hvsm_tx[6:], 2) == 2:
                    self.parent.txt_res_drv_heat.setPixmap(self.parent.img_drv_heat_2)
                elif int(hvsm_tx[6:], 2) == 1:
                    self.parent.txt_res_drv_heat.setPixmap(self.parent.img_drv_heat_1)
                elif int(hvsm_tx[6:], 2) == 0:
                    self.parent.txt_res_drv_heat.setPixmap(self.parent.img_drv_heat_off)

                if int(hvsm_tx[2:4], 2) == 3:
                    self.parent.txt_res_drv_vent.setPixmap(self.parent.img_drv_vent_3)
                elif int(hvsm_tx[2:4], 2) == 2:
                    self.parent.txt_res_drv_vent.setPixmap(self.parent.img_drv_vent_2)
                elif int(hvsm_tx[2:4], 2) == 1:
                    self.parent.txt_res_drv_vent.setPixmap(self.parent.img_drv_vent_1)
                elif int(hvsm_tx[2:4], 2) == 0:
                    self.parent.txt_res_drv_vent.setPixmap(self.parent.img_drv_vent_off)

                if int(hvsm_tx[4:6], 2) == 3:
                    self.parent.txt_res_pass_heat.setPixmap(self.parent.img_pass_heat_3)
                elif int(hvsm_tx[4:6], 2) == 2:
                    self.parent.txt_res_pass_heat.setPixmap(self.parent.img_pass_heat_2)
                elif int(hvsm_tx[4:6], 2) == 1:
                    self.parent.txt_res_pass_heat.setPixmap(self.parent.img_pass_heat_1)
                elif int(hvsm_tx[4:6], 2) == 0:
                    self.parent.txt_res_pass_heat.setPixmap(self.parent.img_pass_heat_off)

                if int(hvsm_tx[:2], 2) == 3:
                    self.parent.txt_res_pass_vent.setPixmap(self.parent.img_pass_vent_3)
                elif int(hvsm_tx[:2], 2) == 2:
                    self.parent.txt_res_pass_vent.setPixmap(self.parent.img_pass_vent_2)
                elif int(hvsm_tx[:2], 2) == 1:
                    self.parent.txt_res_pass_vent.setPixmap(self.parent.img_pass_vent_1)
                elif int(hvsm_tx[:2], 2) == 0:
                    self.parent.txt_res_pass_vent.setPixmap(self.parent.img_pass_vent_off)

                str_whl_heat_tx = a.data[0]
                if str_whl_heat_tx == 0xc0:
                    self.parent.txt_res_st_whl_heat.setPixmap(self.parent.img_str_whl_heat_off)
                elif str_whl_heat_tx == 0xc3:
                    self.parent.txt_res_st_whl_heat.setPixmap(self.parent.img_str_whl_heat_3)
                elif str_whl_heat_tx == 0xc2:
                    self.parent.txt_res_st_whl_heat.setPixmap(self.parent.img_str_whl_heat_2)
                elif str_whl_heat_tx == 0xc1:
                    self.parent.txt_res_st_whl_heat.setPixmap(self.parent.img_str_whl_heat_1)

                self.parent.bcm_mmi_worker.single_tx_side_mani = a.data[2]
                side_mani_tx = a.data[2]
                if side_mani_tx == 0xf4:
                    self.parent.txt_res_side_mani.setPixmap(self.parent.img_side_mani_off)
                elif side_mani_tx == 0xf8:
                    self.parent.txt_res_side_mani.setPixmap(self.parent.img_side_mani_on)
                # else:
                #     self.parent.txt_res_side_mani.setText("None")

            if a.arbitration_id == 0x18ffd841:
                self.parent.bcm_mmi_worker.single_tx_softswset = a.data
                light_tx = a.data[3]
                if light_tx == 0xcf:
                    self.parent.txt_res_light.setText("30s")
                elif light_tx == 0xd7:
                    self.parent.txt_res_light.setText("60s")
                elif light_tx == 0xdf:
                    self.parent.txt_res_light.setText("90s")
                else:
                    self.parent.txt_res_light.setText("OFF")

                side_heat_tx = a.data[7]
                if side_heat_tx == 0x7f:
                    self.parent.txt_res_side_heat.setPixmap(self.parent.img_side_heat_off)
                elif side_heat_tx == 0xbf:
                    self.parent.txt_res_side_heat.setPixmap(self.parent.img_side_heat_on)
                # else:
                #     self.parent.txt_res_side_heat.setText("None")

            if a.arbitration_id == 0x0c0ba021:
                self.parent.fcs_aeb_worker.single_tx = a.data[0]
                aeb_tx = a.data[0]
                if aeb_tx == 0xfd:
                    self.parent.txt_res_aeb.setText("ON")
                elif aeb_tx == 0xfc:
                    self.parent.txt_res_aeb.setText("OFF")
                else:
                    self.parent.txt_res_aeb.setText("None")
            self.sig2.emit(a)
            self.state_check()
            QtCore.QCoreApplication.processEvents()

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
            self.parent.slider_speed.setValue(value)
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
            self.parent.slider_battery.setValue(new_value)
            self.parent.label_battery.setText(battery)
            self.parent.bms_batt_worker.value = hex(int(new_value / 0.4))[2:].zfill(2)


class PMS_S_HVSM(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x18ffa57f

    def thread_func(self):  # HVSM_MMIFbSts
        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class PMS_C_StrWhl(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.send_id = 0x0cffb291

    def thread_func(self):  # SasChas1Fr01
        self.data[0] = 0x00
        self.data[1] = 0x80
        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class BCM_MMI(NodeThread):
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

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class BCM_SWRC(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.long_count = 0
        self.long_threshold = 40
        self.count = 0
        self.btn_state = 0
        self.send_id = 0x18fa7f21

    def thread_func(self):  # SWS-LIN
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

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)

    # def long_press(self):
    #     while True:
    #         print(self.btn_state, time.time())
    #         message = can.Message(arbitration_id=0x18fa7f21, data=self.data)
    #         self.parent.c_can_bus.send(message)
    #         time.sleep(self.period)
    #         QtCore.QCoreApplication.processEvents()
    #         if self.btn_state == 2:
    #             self.btn_state = 0
    #             break
    #
    #     self.long_count = 0
    #     # print("bbb", self.parent.btn_right.released.signal)
    #     # print(self.parent.btn_right.released.signal, self.parent.btn_right.pressed.signal)


class BCM_StrWhlHeat(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x18ff0721

    def thread_func(self):  # SwmCem_LinFr02
        self.data[0] = 0xFB
        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class BCM_LightChime(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.send_id = 0x18ff8721

    def thread_func(self):  # BCM_LightChileReq
        self.data[0] = 0xCF
        self.data[1] = 0xF7
        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class BCM_StateUpdate(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x18ff8621

    def thread_func(self):  # BCM_StateUpdate
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

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class PMS_BodyCont_C(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.value = '0000'
        self.send_id = 0x0cfab127

    def thread_func(self):  # PMS_BodyControlInfo (C-CAN)
        self.data[1] = int(self.value[2:4], 16)
        self.data[2] = int(self.value[2:4], 16)
        self.data[6] = 0xF7
        self.data[7] = int(self.value[2:4], 16)

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class PMS_PTInfo(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.value = '0000'
        self.send_id = 0x18fab027

    def thread_func(self):  # PMS_PTInfoIndicate
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

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class PMS_BodyCont_P(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.send_id = 0x0cfab127

    def thread_func(self):  # PMS_BodyControlInfo (P-CAN)
        self.data[4] = 0x00

        self.parent.send_message(self.parent.p_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class PMS_VRI(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.send_id = 0x18fab327

    def thread_func(self):  # PMS_VRI
        self.data[0] = 0x00
        self.data[1] = 0x00
        self.data[2] = 0x00
        self.data[3] = 0x00

        self.parent.send_message(self.parent.p_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class FCS_AEB(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.single_tx = None
        self.send_id = 0x0cf02fa0

    def thread_func(self):  # FCS_AEBS1
        if self.single_tx:
            if self.single_tx == 0xfd:
                self.data[0] = 0xF1
            elif self.single_tx == 0xfc:
                self.data[0] = 0xF2

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class FCS_LDW(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.single_tx = None
        self.send_id = 0x18fe5be8

    def thread_func(self):  # FCS_FLI2
        self.data[1] = 0xF0

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class IC_TachoSpeed(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.050
        self.value = '0000'
        self.send_id = 0x0cfe6c17

    def thread_func(self):
        self.data[6] = int(self.value[2:4], 16)
        self.data[7] = int(self.value[0:2], 16)

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class IC_Distance(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 1.000
        self.send_id = 0x18fec117

    def thread_func(self):
        self.data[0] = 0x00
        self.data[1] = 0x00
        self.data[2] = 0x00
        self.data[3] = 0x00

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class ESC_TPMS(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.010
        self.send_id = 0x18f0120B

    def thread_func(self):
        self.data[7] = 0xCF
        if self.sender():
            btn_text = self.sender().objectName()
            if btn_text == "btn_tpms_success":
                self.data[7] = 0xDF
            elif btn_text == "btn_tpms_fail":
                self.data[7] = 0xEF

        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class ACU_SeatBelt(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 0.200
        self.send_id = 0x18fac490

    def thread_func(self):
        self.parent.send_message(self.parent.c_can_bus, self.send_id, self.data)
        time.sleep(self.period)

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
    def __init__(self, parent):
        super().__init__(parent)
        self.value = '7D'
        self.send_id = 0x18fa40f4

    def thread_func(self):
        self.data[2] = 0x00
        self.data[3] = 0x7D
        self.data[4] = int(self.value, 16)
        self.data[5] = 0x7D

        self.parent.send_message(self.parent.p_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class BMS_Charge(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x18fa3ef4

    def thread_func(self):
        self.data[0] = 0x0F
        self.data[1] = 0xFC
        if self.parent.chkbox_charge.isChecked():
            self.data[0] = 0x1F

        self.parent.send_message(self.parent.p_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class MCU_Motor(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.send_id = 0x0cfa01ef

    def thread_func(self):
        self.data[4] = 0x00
        self.data[5] = 0x00

        self.parent.send_message(self.parent.p_can_bus, self.send_id, self.data)
        time.sleep(self.period)


class TesterPresent(NodeThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.period = 4.0
        self.send_id = 0x18da41f1

    def thread_func(self):
        if self.parent.chkbox_tester_present.isChecked():
            self.data[0] = 0x02
            self.data[1] = 0x3E
            self.data[2] = 0x00
            message = can.Message(arbitration_id=0x18da41f1, data=self.data)
            self.parent.c_can_bus.send(message)
            time.sleep(self.period)

        # pixmap = QPixmap(':/icon/OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # self.sig_side_mirrorb = QPixmap(':/icon/OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # pixmap.save("aaa.jpg")
        # pixmap2 = QPixmap()
        # pixmap2.load('./OneDrive_2023-05-17/2x/btn_navi_heatedsteeringwheel_02_on.png')
        # print(pixmap)
        # self.parent.test_label.setPixmap(pixmap)
        # self.parent.test_label.setPixmap(pixmap2)
        # self.parent.test_label.setPixmap(self.sig_side_mirrorb)