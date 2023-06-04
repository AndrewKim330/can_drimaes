
import scrapping3 as scr

import sys
import can
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from can import interfaces
import can_thread as worker

form_class = uic.loadUiType("untitled.ui")[0]

# bus1 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')

# try:
#     # bus2 = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS2', bitrate='500000')
# except:
#     # bus1 = can.interface.Bus(bustype='vector', channel=0, bitrate='500000')
#     # bus2 = can.interface.Bus(bustype='vector', channel=1, bitrate='500000')
#     print("No good")


class Main(QMainWindow, form_class):
    custom_signal = pyqtSignal("PyQt_PyObject")

    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.bus = None
        self.bus_flag = False

        self.btn_drv_state.clicked.connect(self.set_drv_state)

        self.power_train_worker = worker.PowerTrain(parent=self)

        # Default value of Gear radio button
        self.btn_gear_n.setChecked(True)
        self.btn_gear_n.clicked.connect(self.power_train_worker.thread_func)
        self.btn_gear_r.clicked.connect(self.power_train_worker.thread_func)
        self.btn_gear_d.clicked.connect(self.power_train_worker.thread_func)

        self.power_worker = worker.PowerMode(parent=self)

        # Default value of Power mode radio button
        self.btn_acc.setChecked(True)
        self.btn_acc_off.clicked.connect(self.power_worker.thread_func)
        self.btn_acc.clicked.connect(self.power_worker.thread_func)
        self.btn_ign.clicked.connect(self.power_worker.thread_func)
        self.btn_start.clicked.connect(self.power_worker.thread_func)

        self.chkbox_pt_ready.clicked.connect(self.power_worker.thread_func)

        self.swrc_worker = worker.Swrc(parent=self)

        self.btn_ok.clicked.connect(self.swrc_worker.thread_func)
        self.btn_left.clicked.connect(self.swrc_worker.thread_func)
        self.btn_left_long.clicked.connect(self.swrc_worker.thread_func)
        self.btn_right.clicked.connect(self.swrc_worker.thread_func)
        self.btn_right_long.clicked.connect(self.swrc_worker.thread_func)
        self.btn_undo.clicked.connect(self.swrc_worker.thread_func)
        self.btn_mode.clicked.connect(self.swrc_worker.thread_func)
        self.btn_mute.clicked.connect(self.swrc_worker.thread_func)

        self.btn_call.clicked.connect(self.swrc_worker.thread_func)
        self.btn_call_long.clicked.connect(self.swrc_worker.thread_func)
        self.btn_vol_up.clicked.connect(self.swrc_worker.thread_func)
        self.btn_vol_up_long.clicked.connect(self.swrc_worker.thread_func)
        self.btn_vol_down.clicked.connect(self.swrc_worker.thread_func)
        self.btn_vol_down_long.clicked.connect(self.swrc_worker.thread_func)

        # self.nrc_sess_12.clicked.connect(self.session_cont)
        # self.nrc_sess_13.clicked.connect(self.session_cont)

        # self.hw_reset.clicked.connect(self.reset_cont)
        # self.sw_reset.clicked.connect(self.reset_cont)
        # self.nrc_reset_12.clicked.connect(self.reset_cont)
        # self.nrc_reset_13.clicked.connect(self.reset_cont)
        # self.nrc_reset_7f_hw.clicked.connect(self.reset_cont)
        # self.nrc_reset_7f_sw.clicked.connect(self.reset_cont)
        #
        # self.clear_console.clicked.connect(self.diag_text_clear)

        self.thread_worker = worker.ThreadWorker(parent=self)

        self.slider_speed.sliderMoved.connect(self.thread_worker.slider_speed_func)
        self.slider_speed.valueChanged.connect(self.thread_worker.slider_speed_func)

        self.speed_worker = worker.TachoSpeed(parent=self)

        self.btn_ota_cond.clicked.connect(self.set_ota_cond)

        self.tx_worker = worker.TxOnlyWorker(parent=self)
        self.hvac_worker = worker.Hvac(parent=self)

        self.tx_worker.sig2.connect(self.sig2)
        # self.custom_signal.connect(self.tx_worker.good2)

        # self.thread_worker.sig1.connect(self.sig1)
        # self.custom_signal.connect(self.thread_worker.)

        self.btn_bus_connect.clicked.connect(self.bus_connect)

        self.btn_bus_start.clicked.connect(self.thread_start)
        self.btn_bus_stop.clicked.connect(self.thread_stop)

        self.set_entire_basic_btns_enable(False)

    def bus_connect(self):
        if not self.bus_flag:
            try:
                self.bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate='500000')
                self.bus_flag = True
                self.bus_console.appendPlainText("PCAN bus is connected")
            except interfaces.pcan.pcan.PcanCanInitializationError as e1:
                print(e1)
                self.bus_console.appendPlainText("PCAN bus is not connected")
                try:
                    self.bus = can.interface.Bus(bustype='vector', channel=0, bitrate='500000')
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
            self.thread_worker.start()
            self.tx_worker.start()
            self.hvac_worker.start()
            self.swrc_worker.start()
            self.power_train_worker.start()
            self.power_worker.start()
            self.speed_worker.start()

            self.thread_worker._isRunning = True
            self.tx_worker._isRunning = True
            self.hvac_worker._isRunning = True
            self.swrc_worker._isRunning = True
            self.power_train_worker._isRunning = True
            self.power_worker._isRunning = True
            self.speed_worker._isRunning = True

            self.set_entire_basic_btns_enable(True)
        else:
            self.bus_console.appendPlainText("Can bus is not connected")

    def thread_stop(self):
        self.thread_worker.stop()
        self.tx_worker.stop()
        self.hvac_worker.stop()
        self.swrc_worker.stop()
        self.power_train_worker.stop()
        self.power_worker.stop()
        self.speed_worker.stop()

        self.thread_worker.quit()
        self.tx_worker.quit()
        self.hvac_worker.quit()
        self.swrc_worker.quit()
        self.power_train_worker.quit()
        self.power_worker.quit()
        self.speed_worker.quit()

        self.set_entire_basic_btns_enable(False)

    # def btn_clicked_dtc_num(self):
    #     print("19 01 service")
    #     message = can.Message(arbitration_id=0x18da41f1, data=[0x03, 0x19, 0x01, 0x09, 0xFF, 0xFF, 0xFF, 0xFF])
    #     bus1.send(message)
    #
    # def btn_clicked_dtc_list(self):
    #     print("19 02 service")
    #     message = can.Message(arbitration_id=0x18da41f1, data=[0x03, 0x19, 0x02, 0x09, 0xFF, 0xFF, 0xFF, 0xFF])
    #     bus1.send(message)

    def set_drv_state(self):
        if self.btn_drv_state.text() == 'On Driving State':
            self.btn_gear_n.setChecked(True)
            self.btn_ign.setChecked(True)
            self.chkbox_pt_ready.setChecked(False)
        else:
            self.btn_gear_d.setChecked(True)
            self.btn_start.setChecked(True)
            self.chkbox_pt_ready.setChecked(True)

    def set_ota_cond(self):
        # **need to add battery condition**
        if self.btn_ota_cond.text() == 'On OTA Condition':
            self.chkbox_h_brake.setChecked(False)
        else:
            self.btn_gear_n.setChecked(True)
            self.chkbox_h_brake.setChecked(True)

    def set_entire_basic_btns_enable(self, flag):
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

    def btn_clicked_security(self):
        self.custom_signal.emit("security")

    def btn_clicked_write(self):
        self.custom_signal.emit("write")

    # def btn_clicked5(self):
    #     print("2E - ECU date")
    #     message = can.Message(arbitration_id=0x18da41f1, data=[0x02, 0x27, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #     bus1.send(message)
    #
    # def btn_clicked6(self):
    #     print("27 02 service")
    #     message = can.Message(arbitration_id=0x18da41f1, data=[0x06, 0x27, 0x02, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #     bus1.send(message)

    def diag_text_clear(self):
        self.diag_console.clear()

    def mmi_text_clear(self):
        self.mmi_console.clear()

    @pyqtSlot(list)
    def sig1(self, li):
        # print("good1", li)
        # print('emit success')
        # scr.scr(li)
        # print("good1", li)
        # self.mmi_hvac.appendPlainText(li[5])
        if li[3] == "18daf141":
            self.diag_console.appendPlainText(li[5])
        #     print("diag", li)
        #     self.session_cont(li)
        # if li[3] == '18ffd741':
        #     print("Seat_HAVC", li)
        #     self.mmi_console.appendPlainText(str(li))
        # for i in li:
        #     self.mmi_hvac.append(str(i))
        #     # self.text_box.appendPlainText(str(i))
        # if li[3] == '18ff8621':
            # print("good", li)
            # self.mmi_console.appendPlainText(str(li))

    @pyqtSlot(list)
    def sig2(self, li):
        self.mmi_console.appendPlainText(str(li))
        if li[3] == '18ffd741':
            seat_hvac_bin = bin(int(li[9], 16))[2:].zfill(8)
            drv_heat = seat_hvac_bin[6:8]
            self.txt_res_drv_heat.setText(str(int(drv_heat, 2)))
            pass_heat = seat_hvac_bin[4:6]
            self.txt_res_pass_heat.setText(str(int(pass_heat, 2)))
            drv_vent = seat_hvac_bin[2:4]
            self.txt_res_drv_vent.setText(str(int(drv_vent, 2)))
            pass_vent = seat_hvac_bin[0:2]
            self.txt_res_pass_vent.setText(str(int(pass_vent, 2)))

            st_whl_heat_bin = bin(int(li[8], 16))[2:].zfill(8)
            st_whl_heat = st_whl_heat_bin[6:8]
            self.txt_res_st_whl_heat.setText(str(int(st_whl_heat, 2)))

            tpms_and_sidemirror_mani_bin = bin(int(li[10], 16))[2:].zfill(8)
            sidemirror = tpms_and_sidemirror_mani_bin[4:6]
            self.txt_res_side_mani.setText(str(int(sidemirror, 2)))

        if li[3] == '0c0ba021':
            aeb_bin = bin(int(li[8], 16))[2:].zfill(8)
            aeb = aeb_bin[6:8]
            self.txt_res_aeb.setText(str(int(aeb, 2)))

        if li[3] == '18ffd841':
            sidemirror_heat_bin = bin(int(li[15], 16))[2:].zfill(8)
            sidemirror_heat = sidemirror_heat_bin[0:2]
            self.txt_res_side_heat.setText(str(int(sidemirror_heat, 2)))

            home_safety_light_bin = bin(int(li[11], 16))[2:].zfill(8)
            home_safety_light = home_safety_light_bin[3:5]
            self.txt_res_light.setText(str(int(home_safety_light, 2)))

        # self.mmi_console.appendPlainText(str(li))
        # self.mmi_hvac.appendPlainText(li[5])
        if li[3] == "18daf141":
            print("diag", li)
            self.diag_console.appendPlainText(li[5])
        # if li[3] == '18ffd741':
        #     print("Seat_HAVC", li)
        #     self.mmi_console.appendPlainText(str(li))
        # for i in li:
        #     self.mmi_hvac.append(str(i))
        #     # self.text_box.appendPlainText(str(i))
        # if li[3] == '18ff8621':
        #     print("good", li)
        #     self.mmi_console.appendPlainText(str(li))

    # def reset_cont(self, l):
    #     try:
    #         btn_text = self.sender().objectName()
    #         if len(btn_text) > 0:
    #             message = can.Message(arbitration_id=0x18da41f1,
    #                                   data=[0x02, 0x10, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #             bus1.send(message)
    #             time.sleep(0.5)
    #             if btn_text == "hw_reset":
    #                 message = can.Message(arbitration_id=0x18da41f1,
    #                                       data=[0x02, 0x11, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #             elif btn_text == "sw_reset":
    #                 message = can.Message(arbitration_id=0x18da41f1,
    #                                       data=[0x02, 0x11, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #             elif btn_text == "nrc_reset_12":
    #                 message = can.Message(arbitration_id=0x18da41f1,
    #                                       data=[0x02, 0x11, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #             elif btn_text == "nrc_reset_13":
    #                 message = can.Message(arbitration_id=0x18da41f1,
    #                                       data=[0x03, 0x11, 0x01, 0x01, 0xFF, 0xFF, 0xFF, 0xFF])
    #             elif btn_text == "nrc_reset_7f_hw":
    #                 self.custom_signal.emit("security")
    #                 #
    #                 # message = can.Message(arbitration_id=0x18da41f1,
    #                 #                       data=[0x02, 0x10, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #                 # bus1.send(message)
    #                 # time.sleep(0.5)
    #                 # message = can.Message(arbitration_id=0x18da41f1,
    #                 #                       data=[0x02, 0x11, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #             elif btn_text == "nrc_reset_7f_sw":
    #                 message = can.Message(arbitration_id=0x18da41f1,
    #                                       data=[0x02, 0x10, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #                 bus1.send(message)
    #                 time.sleep(0.5)
    #                 message = can.Message(arbitration_id=0x18da41f1,
    #                                       data=[0x02, 0x11, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    #
    #             bus1.send(message)
    #         time.sleep(0.5)
    #         if l:
    #             data_str = str([l[8], l[9], l[10], l[11], l[12], l[13], l[14], l[15]])
    #             if l[9] == "51":
    #                 print("51")
    #                 pf_flag = "Success"
    #                 if l[10] == "01":
    #                     reset_name = "H/W"
    #                     self.hw_reset_label.setText("Tested Success")
    #                 elif l[10] == "03":
    #                     reset_name = "S/W"
    #                     self.sw_reset_label.setText("Tested Success")
    #                 console_str = f'{reset_name} reset {pf_flag}'
    #                 self.diag_console.appendPlainText(console_str)
    #                 self.diag_console.appendPlainText(data_str)
    #             elif l[9] == "7f":
    #                 if l[11] == "12":
    #                     reason = "Not Supported Subfunction"
    #                     self.nrc_reset_12_label.setText("Tested Success")
    #                 elif l[11] == "13":
    #                     reason = "Data Length Error"
    #                     self.nrc_reset_13_label.setText("Tested Success")
    #                 elif l[11] == "7f":
    #                     if l[10] == "01":
    #                         reason = "Not Supported Session (for H/W reset)"
    #                         self.nrc_reset_7f_hw_label.setText("Tested Success")
    #                     elif l[10] == "03":
    #                         reason = "Not Supported Session (for S/W reset)"
    #                         self.nrc_reset_7f_sw_label.setText("Tested Success")
    #                 console_str = f'Diagnosis Error - {reason} (NRC Code : {l[11]})'
    #                 self.diag_console.appendPlainText(console_str)
    #                 self.diag_console.appendPlainText(data_str)
    #     except AttributeError:
    #         pass
    #
    # # def btn_reset(self):


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Main()
    mywindow.show()
    sys.exit(app.exec_())
    # app.exec_()
