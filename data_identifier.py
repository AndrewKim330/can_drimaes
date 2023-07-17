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


def message_info_by_can_id(can_id):
    info_set = []
    if can_id == 0x0CFE6C17:
        info_set.append("IC_TC01")
        info_set.append({"name": "IC_TachographVehicleSpeed", "bit_st_pos": 48, "bit_len": 16})
        return info_set
    elif can_id == 0x18FEC117:
        info_set.append("IC_VDHR")
        return info_set
    elif can_id == 0x18F0120B:
        info_set.append("ESC_ABS_BrakeSysSts")
        return info_set
    elif can_id == 0x0CFFB291:
        info_set.append("SasChas1Fr01")
        return info_set
    elif can_id == 0x18FFA57F:
        info_set.append("HVSM_MMIFBSts")
        return info_set
    elif can_id == 0x0CF02FA0:
        info_set.append("FCS_AEBS1")
        return info_set
    elif can_id == 0x18FE5BE8:
        info_set.append("FCS_FLI2")
        return info_set
    elif can_id == 0x18FFD741:
        info_set.append("MMI_ShowApp")
        info_set.append({"name": "MMI_SteerWhlHeatgOnCmd", 0: "Off", 1: "Lo", 2: "Med", 3: "Hi", "bit_st_pos": 0, "bit_len": 2})
        info_set.append({"name": "MMI_SteerWhlTTun", "bit_st_pos": 2, "bit_len": 4})
        info_set.append({"name": "MMI_DrvSeatHeatgLvlSet", 0: "OFF", 1: "Level 1_Low", 2: "Level 2_Middle", 3: "Level 3_High", "bit_st_pos": 8, "bit_len": 2})
        info_set.append({"name": "MMI_PassSeatHeatgLvlSet", 0: "OFF", 1: "Level 1_Low", 2: "Level 2_Middle", 3: "Level 3_High", "bit_st_pos": 10, "bit_len": 2})
        info_set.append({"name": "MMI_DrvSeatVentnLvlSet", 0: "OFF", 1: "Level 1_Low", 2: "Level 2_Middle", 3: "Level 3_High", "bit_st_pos": 12, "bit_len": 2})
        info_set.append({"name": "MMI_PassSeatVentnLvlSet", 0: "OFF", 1: "Level 1_Low", 2: "Level 2_Middle", 3: "Level 3_High", "bit_st_pos": 14, "bit_len": 2})
        info_set.append({"name": "MMI_TPMS_Reset_Set", 0: "No request", 1: "Request reset", 2: "Reserved", 3: "Invalid", "bit_st_pos": 16, "bit_len": 2})
        info_set.append({"name": "MMI_RearJustRequest", 0: "No request", 1: "Off", 2: "On", 3: "Reserved", "bit_st_pos": 18, "bit_len": 2})
        return info_set
    elif can_id == 0x18FFD841:
        info_set.append("MMI_SoftSwSet")
        return info_set
    elif can_id == 0x0C0BA021:
        info_set.append("MMI_AEBS2")
        return info_set
    elif can_id == 0x18A9E821:
        info_set.append("MMI_FLIC")
        return info_set
    elif can_id == 0x18FF6341:
        info_set.append("MMI_OTAStatus")
        return info_set
    elif can_id == 0x18FF4B41:
        info_set.append("MMI_Safety_Command")
        return info_set
    elif can_id == 0x18FAC490:
        info_set.append("ACU_Status")
        return info_set
    elif can_id == 0x0CFAB127:
        info_set.append("PMS_BodyControlInfo")
        return info_set
    elif can_id == 0x18FAB027:
        info_set.append("PMS_PTInfoIndicate")
        return info_set
    elif can_id == 0x18FF8621:
        info_set.append("BCM_StateUpdate")
        return info_set
    elif can_id == 0x18FF8721:
        info_set.append("BCM_LightChimeReq")
        return info_set
    elif can_id == 0x18FFD521:
        info_set.append("BCM_MMIFBSts")
        return info_set
    elif can_id == 0x18FA7F21:
        info_set.append("SWS-LIN")
        return info_set
    elif can_id == 0x18FF0721:
        info_set.append("SwmCem_Lin4Fr02")
        return info_set
    elif can_id == 0x18DA41F1:
        info_set.append("MMI_DiagReq")
        return info_set
    elif can_id == 0x18DAF141:
        info_set.append("MMI_DiagResp")
        return info_set
    elif can_id == 0x18DB33F1:
        info_set.append("Func_DiagReq")
        return info_set
    elif can_id == 0x0CFA01EF:
        info_set.append("MCU_MotorElePara")
        return info_set
    elif can_id == 0x18FA40F4:
        info_set.append("BMS_BatteryInfo")
        return info_set
    elif can_id == 0x18FA3EF4:
        info_set.append("BMS_ChgInfo")
        return info_set
    elif can_id == 0x18FAB327:
        info_set.append("PMS_VRI")
        return info_set
    else:
        info_set.append("No matching id")
        return info_set


def data_matcher(tx, sub_mess):
    byte_pos = int(sub_mess["bit_st_pos"] / 8)

    try:
        bin_data = bin(tx.data[byte_pos])[2:].zfill(8)
        if sub_mess["name"] == "IC_TachographVehicleSpeed":
            print(bin_data)
        bin_st_pos = 8 - sub_mess["bit_st_pos"] % 8 - sub_mess["bit_len"]
        sig = int(bin_data[bin_st_pos:bin_st_pos + sub_mess["bit_len"]], 2)
        return sub_mess[sig]
    except KeyError:
        return str(sig)
        # if sub_mess["name"] == "MMI_SteerWhlHeatgOnCmd":
        #     sig = str_whl_heat
        # elif sub_mess["name"] == "MMI_PassSeatVentnLvlSet":
        #     sig = sig_pass_vent
        # elif sub_mess["name"] == "MMI_PassSeatVentnLvlSet":
        #     sig = sig_drv_vent
        # elif sub_mess["name"] == "MMI_PassSeatHeatgLvlSet":
        #     sig = sig_pass_heat
        # elif sub_mess["name"] == "MMI_PassSeatHeatgLvlSet":
        #     sig = sig_pass_heat
        # elif sub_mess["name"] == "MMI_DrvSeatHeatgLvlSet":
        #     sig = sig_drv_heat
        # return sub_mess[sig]
        # else:

