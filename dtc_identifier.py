def dtc_identifier(dtc_li):
    if dtc_li[0] == 0x93:
        if dtc_li[1] == 0x81:
            if dtc_li[2] == 0x11:
                return 'MIC short to GND'
            elif dtc_li[2] == 0x12:
                return 'MIC short to Battery'
            elif dtc_li[2] == 0x14:
                return 'MIC open'
        elif dtc_li[1] == 0x82:
            if dtc_li[2] == 0x11:
                return 'Camera video signal short to GND'
        elif dtc_li[1] == 0x89:
            if dtc_li[2] == 0x11:
                return 'Tuner Antenna short to GND'
            elif dtc_li[2] == 0x13:
                return 'Tuner Antenna Open'
        elif dtc_li[1] == 0xa9:
            if dtc_li[2] == 0x4b:
                return 'Over temperature'
        elif dtc_li[1] == 0xaa:
            if dtc_li[2] == 0x16:
                return 'Display Voltage low'
            elif dtc_li[2] == 0x17:
                return 'Display Voltage high'
            elif dtc_li[2] == 0x1c:
                return 'Display Voltage Error'
        elif dtc_li[1] == 0xb7:
            if dtc_li[2] == 0x19:
                return 'Host USB 1 Current-Over Occur'
        elif dtc_li[1] == 0x90:
            if dtc_li[2] == 0x16:
                return 'Main Power DCDC 11V-Buck-Boost output Voltage low'
            elif dtc_li[2] == 0x17:
                return 'Main Power DCDC 11V-Buck-Boost output Voltage high'
        elif dtc_li[1] == 0x91:
            if dtc_li[2] == 0x16:
                return 'Main Power DCDC 3.3V-Buck-Boost output Voltage low'
            elif dtc_li[2] == 0x17:
                return 'Main Power DCDC 3.3V-Buck-Boost output Voltage high'
        elif dtc_li[1] == 0x92:
            if dtc_li[2] == 0x16:
                return 'Main Power DCDC 1.8V-Buck-Boost output Voltage low'
            elif dtc_li[2] == 0x17:
                return 'Main Power DCDC 1.8V-Buck-Boost output Voltage high'
            elif dtc_li[2] == 0x1c:
                return 'Main Power DCDC 1.8V-Buck-Boost output Voltage Error'
        elif dtc_li[1] == 0x93:
            if dtc_li[2] == 0x16:
                return 'Main Batt+ Voltage low'
            elif dtc_li[2] == 0x17:
                return 'Main Batt+ Voltage high'
        elif dtc_li[1] == 0x94:
            if dtc_li[2] == 0x11:
                return 'GPS Antenna short to GND'
            elif dtc_li[2] == 0x13:
                return 'GPS Antenna open'
        elif dtc_li[1] == 0x95:
            if dtc_li[2] == 0x16:
                return 'BT/WiFi Power output Voltage low'
            elif dtc_li[2] == 0x17:
                return 'BT/WiFi Power output Voltage high'
            elif dtc_li[2] == 0x1c:
                return 'BT/WiFi Power output Voltage Error'
        elif dtc_li[1] == 0x96:
            if dtc_li[2] == 0x16:
                return 'LTE Power output Voltage low'
            elif dtc_li[2] == 0x17:
                return 'LTE Power output Voltage high'
            elif dtc_li[2] == 0x01:
                return 'LTE Reject'
            elif dtc_li[2] == 0x1c:
                return 'LTE Power output Voltage Error'
        elif dtc_li[1] == 0x97:
            if dtc_li[2] == 0x11:
                return 'LTE Antenna short to GND'
            elif dtc_li[2] == 0x13:
                return 'LTE Antenna open'
            elif dtc_li[2] == 0x1c:
                return 'LTE Antenna Error'
        elif dtc_li[1] == 0x98:
            if dtc_li[2] == 0x11:
                return 'LCD BLU power short to GND'
            elif dtc_li[2] == 0x13:
                return 'LCD BLU power open'
            elif dtc_li[2] == 0x1c:
                return 'LTE BLU power error'
        elif dtc_li[1] == 0x99:
            if dtc_li[2] == 0x11:
                return 'Camera power output short to GND'
        elif dtc_li[1] == 0x9a:
            if dtc_li[2] == 0x05:
                return 'IVI Software Failed'
        elif dtc_li[1] == 0x09:
            if dtc_li[2] == 0x01:
                return 'Left Speaker Error'
        elif dtc_li[1] == 0x9c:
            if dtc_li[2] == 0x01:
                return 'Right Speaker Error'
        elif dtc_li[1] == 0x00:
            if dtc_li[2] == 0x00:
                return 'ACU Timeout Error'
            elif dtc_li[2] == 0x01:
                return 'BCM Timeout Error'
            elif dtc_li[2] == 0x02:
                return 'ESC Timeout Error'
            elif dtc_li[2] == 0x03:
                return 'FCS Timeout Error'
            elif dtc_li[2] == 0x04:
                return 'IC Timeout Error'
            elif dtc_li[2] == 0x05:
                return 'PMS Timeout Error'
            elif dtc_li[2] == 0x06:
                return 'PMS_S Timeout Error'
            elif dtc_li[2] == 0x07:
                return 'PMS_C Timeout Error'
            elif dtc_li[2] == 0x08:
                return 'PMS Timeout Error'
            elif dtc_li[2] == 0x09:
                return 'BMS Timeout Error'
            elif dtc_li[2] == 0x10:
                return 'MCU Timeout Error'

    elif dtc_li[0] == 0xc0:
        if dtc_li[1] == 0x73:
            if dtc_li[2] == 0x00:
                return 'Control Module CAN bus Off (C-CAN)'
    else:
        return 'No Code'
