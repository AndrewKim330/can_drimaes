from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import serial.tools.list_ports


class SerialPortSelection(QDialog):

    def __init__(self, base_dir, main_obj):
        super().__init__()
        self.ui = uic.loadUi(base_dir + r"./src/can_serial_bus_selection_ui.ui", self)
        self.setWindowIcon(QIcon(base_dir + r"./src/drimaes_icon.ico"))
        self.setWindowTitle("Serial Port Selection for E-51 IVI CAN Simulator")
        self.ui_open()

        self.main_obj = main_obj

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

    def search_serial(self):
        ports = serial.tools.list_ports.comports()
        if len(ports) == 0:
            serial_devices = []
        else:
            serial_devices = ports
        self.port_setting(serial_devices)

    def selected_port_handler(self):
        selected_list = []
        for port in self.port_chkboxes:
            if port.isChecked():
                selected_list.append(port.text())
        self.main_obj.selected_ports = selected_list
        self.main_obj.bus_console.appendPlainText("Serial port is selected")
        self.ui_close()

    def ui_open(self):
        self.show()

    def ui_close(self):
        self.close()
