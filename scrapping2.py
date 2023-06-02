# from bs4 import BeautifulSoup
# import pandas as pd
import pprint as pp
import binascii
from copy import copy


def dtc_identifier(dtc_li):
    if dtc_li[0] == '0x93':
        if dtc_li[1] == '0x81':
            if dtc_li[2] == '0x11':
                return 'MIC short to GND'
            elif dtc_li[2] == '0x12':
                return 'MIC short to Battery'
            elif dtc_li[2] == '0x13':
                return 'MIC open'
        elif dtc_li[1] == '0x82':
            if dtc_li[2] == '0x11':
                return 'Camera video signal short to GND'
        elif dtc_li[1] == '0x89':
            if dtc_li[2] == '0x11':
                return 'Tuner Antenna short to GND'
            elif dtc_li[2] == '0x13':
                return 'Tuner Antenna Open'
        elif dtc_li[1] == '0xa9':
            if dtc_li[2] == '0x4b':
                return 'Over temperature'
        elif dtc_li[1] == '0xaa':
            if dtc_li[2] == '0x16':
                return 'Display Voltage low'
            elif dtc_li[2] == '0x17':
                return 'Display Voltage high'
            elif dtc_li[2] == '0x1c':
                return 'Display Voltage Error'
        elif dtc_li[1] == '0xb7':
            if dtc_li[2] == '0x19':
                return 'Host USB 1 Current-Over Occur'
        elif dtc_li[1] == '0x90':
            if dtc_li[2] == '0x16':
                return 'Main Power DCDC 11V-Buck-Boost output Voltage low'
            elif dtc_li[2] == '0x17':
                return 'Main Power DCDC 11V-Buck-Boost output Voltage high'
        elif dtc_li[1] == '0x91':
            if dtc_li[2] == '0x16':
                return 'Main Power DCDC 3.3V-Buck-Boost output Voltage low'
            elif dtc_li[2] == '0x17':
                return 'Main Power DCDC 3.3V-Buck-Boost output Voltage high'
        elif dtc_li[1] == '0x92':
            if dtc_li[2] == '0x16':
                return 'Main Power DCDC 1.8V-Buck-Boost output Voltage low'
            elif dtc_li[2] == '0x17':
                return 'Main Power DCDC 1.8V-Buck-Boost output Voltage high'
            elif dtc_li[2] == '0x1c':
                return 'Main Power DCDC 1.8V-Buck-Boost output Voltage Error'
        elif dtc_li[1] == '0x93':
            if dtc_li[2] == '0x16':
                return 'Main Batt+ Voltage low'
            elif dtc_li[2] == '0x17':
                return 'Main Batt+ Voltage high'
        elif dtc_li[1] == '0x94':
            if dtc_li[2] == '0x11':
                return 'GPS Antenna short to GND'
            elif dtc_li[2] == '0x13':
                return 'GPS Antenna open'
        elif dtc_li[1] == '0x95':
            if dtc_li[2] == '0x16':
                return 'BT/WiFi Power output Voltage low'
            elif dtc_li[2] == '0x17':
                return 'BT/WiFi Power output Voltage high'
            elif dtc_li[2] == '0x1c':
                return 'BT/WiFi Power output Voltage Error'
        elif dtc_li[1] == '0x96':
            if dtc_li[2] == '0x16':
                return 'LTE Power output Voltage low'
            elif dtc_li[2] == '0x17':
                return 'LTE Power output Voltage high'
            elif dtc_li[2] == '0x1':
                return 'LTE Reject'
            elif dtc_li[2] == '0x1c':
                return 'LTE Power output Voltage Error'
        elif dtc_li[1] == '0x97':
            if dtc_li[2] == '0x11':
                return 'LTE Antenna short to GND'
            elif dtc_li[2] == '0x13':
                return 'LTE Antenna open'
            elif dtc_li[2] == '0x1c':
                return 'LTE Antenna Error'
        elif dtc_li[1] == '0x98':
            if dtc_li[2] == '0x11':
                return 'LCD BLU power short to GND'
            elif dtc_li[2] == '0x13':
                return 'LCD BLU power open'
            elif dtc_li[2] == '0x1c':
                return 'LTE BLU power error'
        elif dtc_li[1] == '0x99':
            if dtc_li[2] == '0x11':
                return 'Camera power output short to GND'
        elif dtc_li[1] == '0x9a':
            if dtc_li[2] == '0x5':
                return 'IVI Software Failed'
        elif dtc_li[1] == '0x9b':
            if dtc_li[2] == '0x1':
                return 'Left Speaker Error'
        elif dtc_li[1] == '0x9c':
            if dtc_li[2] == '0x1':
                return 'Right Speaker Error'
        elif dtc_li[1] == '0x0':
            if dtc_li[2] == '0x0':
                return 'ACU Timeout Error'
            elif dtc_li[2] == '0x1':
                return 'BCM Timeout Error'
            elif dtc_li[2] == '0x2':
                return 'ESC Timeout Error'
            elif dtc_li[2] == '0x3':
                return 'FCS Timeout Error'
            elif dtc_li[2] == '0x4':
                return 'IC Timeout Error'
            elif dtc_li[2] == '0x5':
                return 'PMS Timeout Error'
            elif dtc_li[2] == '0x6':
                return 'PMS_S Timeout Error'
            elif dtc_li[2] == '0x7':
                return 'PMS_C Timeout Error'
            elif dtc_li[2] == '0x8':
                return 'PMS Timeout Error'
            elif dtc_li[2] == '0x9':
                return 'BMS Timeout Error'
            elif dtc_li[2] == '0x10':
                return 'MCU Timeout Error'

    elif dtc_li[0] == '0xc0':
        if dtc_li[1] == '0x73':
            if dtc_li[2] == '0x0':
                return 'Control Module CAN bus Off (C-CAN)'
            elif dtc_li[2] == '0x1':
                return 'Control Module CAN bus Off (P-CAN)'
    else:
        return 'No Code'


def scr():
    with open('wefab.asc', 'r') as f:
        temp_a = f.read()

    temp = temp_a.split()

    li_origin = []
    li_mani = []
    res = []
    dtc_num = 0
    dtc_flag = False
    multi_flag = False
    i = 0
    while i < len(temp):
        temp_li = []
        if temp[i] == '18DA41F1x':
            temp_li.append('GST_MMI')
            temp_li.append(temp[i])
            for j in range(8):
                temp_li.append(temp[i + 4 + j])
            i += j
            li_origin.append(copy(temp_li))
            li_mani.append(temp_li[2:])
        elif temp[i] == '18DAF141x':
            temp_li.append('MMI_GST')
            temp_li.append(temp[i])
            for j in range(8):
                temp_li.append(temp[i + 4 + j])
            i += j
            li_origin.append(copy(temp_li))
            li_mani.append(temp_li[2:])
        else:
            i += 1

    pp.pprint(li_origin)
    print("----")
    pp.pprint(li_mani)

    j = 0
    dtc = []
    while j < len(li_mani):
        dtc_flag = False
        if multi_flag:
            li_new = li_mani[j][1:]
            k = 0
            dtc_num = 0
            while k < len(li_new):
                if len(dtc) == 3:
                    k += dtc_num
                    dtc_flag = False
                    dtc.append(dtc_identifier(dtc))
                    res.append(dtc[:])
                    dtc = []
                    dtc_num = 0
                else:
                    if dtc_flag:
                        try:
                            dtc.append(hex(int(li_new[k+dtc_num], 16)))
                            dtc_num += 1
                        except IndexError:
                            break
                    else:
                        if li_new[k] == status_mask:
                            k += 1
                        dtc_flag = True
            # res.append(dtc)
        else:
            if li_mani[j][0] == "03":
                status_mask = li_mani[j][3]
            elif li_mani[j][0] == '10':
                multi_flag = True
        j += 1

    pp.pprint(res)


if __name__ == "__main__":
    scr()
    # test()