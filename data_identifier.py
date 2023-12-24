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


def message_info_by_can_id(can_id, bus):
    info_set = []
    if can_id == 0x0CFE6C17:
        info_set.append("IC_TC01")
        data_set = [{"name": "IC_TachographVehicleSpeed", "bit_st_pos": 48, "bit_len": 16}]
    elif can_id == 0x18FEC117:
        info_set.append("IC_VDHR")
        data_set = [{"name": "IC_TotalVehicleDistance", "bit_st_pos": 0, "bit_len": 32}]
    elif can_id == 0x18F0120B:
        info_set.append("ESC_ABS_BrakeSysSts")
        data_set = [{"name": "ECS_Reset_Progress", 0x0: "Reset Ongoing", 0x1: "Reset Ended Successfully",
                         0x2: "Reset Ended Failed", 0x3: "Reserved", "bit_st_pos": 60, "bit_len": 2}]
    elif can_id == 0x0CFFB291:
        info_set.append("SasChas1Fr01")
        data_set = [{"name": "SteerWhlSnsrAg", "bit_st_pos": 0, "bit_len": 15}]
    elif can_id == 0x18FFA57F:
        info_set.append("HVSM_MMIFBSts")
        data_set = [{"name": "HVSM_DrvSeatHeatSts", 0x0: "OFF", 0x1: "Level 1_Low", 0x2: "Level 2_Middle",
                     0x3: "Level 3_High", "bit_st_pos": 0, "bit_len": 2},
                    {"name": "HVSM_PassSeatHeatSts", 0x0: "OFF", 0x1: "Level 1_Low", 0x2: "Level 2_Middle",
                     0x3: "Level 3_High", "bit_st_pos": 2, "bit_len": 2},
                    {"name": "HVSM_DrvSeatVentnSts", 0x0: "OFF", 0x1: "Level 1_Low", 0x2: "Level 2_Middle",
                     0x3: "Level 3_High", "bit_st_pos": 4, "bit_len": 2},
                    {"name": "HVSM_PassSeatVentnSts", 0x0: "OFF", 0x1: "Level 1_Low", 0x2: "Level 2_Middle",
                     0x3: "Level 3_High", "bit_st_pos": 6, "bit_len": 2}]
    elif can_id == 0x0CF02FA0:
        info_set.append("FCS_AEBS1")
        data_set = [{"name": "FCS_AEBState", 0x0: "System is not ready (initialization not finished)",
                     0x1: "System is temporarily not available", 0x2: "System is deactivated by driver",
                     0x3: "System is ready and activated", 0x4: "Driver overrides system",
                     0x5: "Collision warning active", 0x6: "Collision warning with braking",
                     0x7: "Emergency braking active", 0x8: "Reserved for future use", 0x9: "Reserved for future use",
                     0xA: "Reserved for future use", 0xB: "Reserved for future use", 0xC: "Reserved for future use",
                     0xD: "Reserved for future use", 0xE: "Error indication", 0xF: "Not available / not installed",
                     "bit_st_pos": 0, "bit_len": 4}]
    elif can_id == 0x18FE5BE8:
        info_set.append("FCS_FLI2")
        data_set = [{"name": "FCS_LDWSystemState", 0x0: "system is not ready(initialization not finished)",
                     0x1: "System not available(not all conditions fulfilled)", 0x2: "System deactivated by driver",
                     0x3: "System is ready(no warning active)", 0x4: "driver overrides system",
                     0x5: "system is warning", 0x6: "Reserved", 0x7: "Reserved", 0x8: "Reserved", 0x9: "Reserved",
                     0xA: "Reserved", 0xB: "Reserved", 0xC: "Reserved", 0xD: "Reserved", 0xE: "error indication",
                     0xF: "not available / not installed", "bit_st_pos": 8, "bit_len": 4}]
    elif can_id == 0x18FFD741:
        info_set.append("MMI_ShowApp")
        data_set = [{"name": "MMI_SteerWhlHeatgOnCmd", 0x0: "Off", 0x1: "Lo", 0x2: "Med", 0x3: "Hi", "bit_st_pos": 0,
                     "bit_len": 2}, {"name": "MMI_SteerWhlTTun", "bit_st_pos": 2, "bit_len": 4},
                    {"name": "MMI_DrvSeatHeatgLvlSet", 0x0: "OFF", 0x1: "Level 1_Low", 0x2: "Level 2_Middle",
                     0x3: "Level 3_High", "bit_st_pos": 8, "bit_len": 2},
                    {"name": "MMI_PassSeatHeatgLvlSet", 0x0: "OFF", 0x1: "Level 1_Low", 0x2: "Level 2_Middle",
                     0x3: "Level 3_High", "bit_st_pos": 10, "bit_len": 2},
                    {"name": "MMI_DrvSeatVentnLvlSet", 0x0: "OFF", 0x1: "Level 1_Low", 0x2: "Level 2_Middle",
                     0x3: "Level 3_High", "bit_st_pos": 12, "bit_len": 2},
                    {"name": "MMI_PassSeatVentnLvlSet", 0x0: "OFF", 0x1: "Level 1_Low", 0x2: "Level 2_Middle",
                     0x3: "Level 3_High", "bit_st_pos": 14, "bit_len": 2},
                    {"name": "MMI_TPMS_Reset_Set", 0x0: "No request", 0x1: "Request reset", 0x2: "Reserved",
                     0x3: "Invalid", "bit_st_pos": 16, "bit_len": 2},
                    {"name": "MMI_RearJustRequest", 0x0: "No request", 0x1: "Off", 0x2: "On", 0x3: "Reserved",
                     "bit_st_pos": 18, "bit_len": 2}]
    elif can_id == 0x18FFD841:
        info_set.append("MMI_SoftSwSet")
        data_set = [{"name": "MMI_HomeSafetyLightsTimeSet", 0x0: "No request", 0x1: "Request reset", 0x2: "Reserved",
                     0x3: "Invalid", "bit_st_pos": 27, "bit_len": 3},
                    {"name": "MMI_RearDefrostKeyRequest", 0x0: "No request", 0x1: "Off", 0x2: "On", 0x3: "Reserved",
                     "bit_st_pos": 62, "bit_len": 2}]
    elif can_id == 0x0C0BA021:
        info_set.append("MMI_AEBS2")
        data_set = [
            {"name": "MMI_AEBS_DriveActiveDemand", 0x0: "Deactivation of system", 0x1: "No Deactivation of system)",
             0x2: "reserved", 0x3: "don’t' care / take no action", "bit_st_pos": 0, "bit_len": 2},
            {"name": "MMI_AEBS2_MessageCounter", "bit_st_pos": 56, "bit_len": 4},
            {"name": "MMI_AEBS2_MessageChecksum", "bit_st_pos": 60, "bit_len": 4}]
    elif can_id == 0x18A9E821:
        info_set.append("MMI_FLIC")
        data_set = [{"name": "MMI_LDWEnableCommand", 0x0: "Disable Lane Departure Warning",
                     0x1: "Enable Lane Departure Warning", 0x2: "Reserved", 0x3: "Don´t care", "bit_st_pos": 0,
                     "bit_len": 2}]
    elif can_id == 0x18FF6341:
        info_set.append("MMI_OTAStatus")
        data_set = [
            {"name": "MMI_OTA_DownloadRequest", 0x0: "Not Request", 0x1: "Request", "bit_st_pos": 0, "bit_len": 1},
            {"name": "MMI_OTA_DownloadState", 0: "Default", 0x1: "OTA Download Software in progress",
             0x2: "OTA Download Software success (Reserved)", 0x3: "OTA Download Software failure", "bit_st_pos": 1,
             "bit_len": 2},
            {"name": "MMI_OTA_UpdateRequest", 0x0: "Not Request", 0x1: "Request", "bit_st_pos": 3, "bit_len": 1},
            {"name": "MMI_OTA_UpdateState", 0x0: "Default", 0x1: "OTA Update in progress", 0x2: "OTA Update success",
             0x3: "OTA Update failure（Reserved）", 0x4: "OTA Update continue from restart（Reserved）",
             0x5: "OTA Update roll back failure", 0x6: "OTA Update roll back success", 0x7: "Reserved", "bit_st_pos": 4,
             "bit_len": 3},
            {"name": "MMI_OTA_Mode", 0x0: "Exit OTA Mode", 0x1: "Enter OTA Mode", "bit_st_pos": 7, "bit_len": 1},
            {"name": "MMI_OTA_DownloadProgress", "bit_st_pos": 8, "bit_len": 8},
            {"name": "MMI_OTA_FailedReason_PowerMode", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 16, "bit_len": 1},
            {"name": "MMI_OTA_FailedReason_GearPos", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 17, "bit_len": 1},
            {"name": "MMI_OTA_FailedReason_VehicleSpd", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 18, "bit_len": 1},
            {"name": "MMI_OTA_FailedReason_BattVol", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 19, "bit_len": 1},
            {"name": "MMI_OTA_FailedReason_HandBrake", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 20, "bit_len": 1},
            {"name": "MMI_OTA_FailedReason_ChgStatus", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 21, "bit_len": 1},
            {"name": "MMI_OTA_FailedReason_HVStatus", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 22, "bit_len": 1},
            {"name": "MMI_OTA_PreConditionDetect", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 23, "bit_len": 1},
            {"name": "MMI_OTA_DisclaimerWarning", 0x1: "OK", 0x2: "NOK", "bit_st_pos": 24, "bit_len": 1}]
    elif can_id == 0x18FF4B41:
        info_set.append("MMI_Safety_Command")
        data_set = [{"name": "MMI_OTA_InfoShowStatus", 0x0: "Default", 0x1: "OTA information show successful",
                     0x2: "OTA information show failure", 0x3: "Reserved", "bit_st_pos": 20, "bit_len": 2},
                    {"name": "MMI_OTA_DownloadSelected", 0x0: "Default", 0x1: "OTA Download Cancelled",
                     0x2: "OTA Download Confirmed", 0x3: "Reserved", "bit_st_pos": 22, "bit_len": 2},
                    {"name": "MMI_OTA_UpdateSelected", 0x0: "Default", 0x1: "OTA Update Cancelled",
                     0x2: "OTA Update Confirmed", 0x3: "Reserved", "bit_st_pos": 24, "bit_len": 2},
                    {"name": "MMI_OTA_UpdateResultConfirm", 0x1: "No Confirm", 0x2: "Confirm", "bit_st_pos": 26,
                     "bit_len": 1},
                    {"name": "MMI_OTA_DeclimerSelected", 0x0: "Default", 0x1: "OTA Declimer Cancelled",
                     0x2: "OTA Declimer Confirmed", 0x3: "Reserved", "bit_st_pos": 27, "bit_len": 2}]
    elif can_id == 0x18FAC490:
        info_set.append("ACU_Status")
        data_set = [
            {"name": "ACU_DrvSeatbeltBucklestatus", 0x0: "Switch Off", 0x1: "Switch On", "bit_st_pos": 0, "bit_len": 1},
            {"name": "ACU_PassSeatbeltBucklestatus", 0x0: "Switch Off", 0x1: "Switch On", "bit_st_pos": 1,
             "bit_len": 1},
            {"name": "ACU_DrvSeatbeltBuckleInvalid", 0x0: "Valid", 0x1: "Invalid", "bit_st_pos": 8, "bit_len": 1},
            {"name": "ACU_PassSeatbeltBuckleInvalid", 0x0: "Valid", 0x1: "Invalid", "bit_st_pos": 9, "bit_len": 1}]
    elif can_id == 0x0CFAB127:
        info_set.append("PMS_BodyControlInfo")
        if bus == "C-CAN":
            data_set = [{"name": "PMS_Brake_State", "bit_st_pos": 6, "bit_len": 1},
                        {"name": "PMS_VehicleSpd", "bit_st_pos": 8, "bit_len": 16},
                        {"name": "PMS_VehicleSpd_flag", 0x0: "Valid", 0x1: "Invalid", "bit_st_pos": 51, "bit_len": 1}]
        elif bus == "P-CAN":
            data_set = [{"name": "PMS_AcceleratorPedalPosition", "bit_st_pos": 32, "bit_len": 8}]
    elif can_id == 0x18FAB027:
        info_set.append("PMS_PTInfoIndicate")
        data_set = [
            {"name": "PMS_PTReadyInd", 0x0: "No Ready", 0x1: "Ready", 0x2: "Error", 0x3: "Invalid", "bit_st_pos": 4,
             "bit_len": 2},
            {"name": "PMS_GearPositionInd", 0xFC: "Driving", 0xFB: "Parking (Reserved)", 0xFA: "Climbing (Reserved)",
             0xDF: "Reverse", 0x7D: "Neutral", "bit_st_pos": 32, "bit_len": 8},
            {"name": "PMS_HandbrakeSts", 0x0: "Handbrake not applied", 0x1: "Handbrake applied", 0x2: "Error",
             0x3: "Invalid", "bit_st_pos": 40, "bit_len": 2},
            {"name": "PMS_IgniteSts", 0x0: "ON Position Power Off", 0x1: "ON Position Power On", 0x2: "Reserve",
             0x3: "Invalid", "bit_st_pos": 50, "bit_len": 2},
            {"name": "PMS_HV_Status ", 0x0: "Inactive", 0x1: "Active", 0x2: "Error", 0x3: "Invalid", "bit_st_pos": 62,
             "bit_len": 2}]
    elif can_id == 0x18FF8621:
        info_set.append("BCM_StateUpdate")
        data_set = [{"name": "BCM_LowBeamSts", 0x0: "OFF", 0x1: "ON", "bit_st_pos": 3, "bit_len": 1},
                    {"name": "BCM_AutoLightSts", 0x0: "OFF", 0x1: "ON", "bit_st_pos": 5, "bit_len": 1},
                    {"name": "BCM_HighBeamSts", 0x0: "OFF", 0x1: "ON", "bit_st_pos": 6, "bit_len": 1},
                    {"name": "BCM_RearFogLightSts", 0x0: "OFF", 0x1: "ON", "bit_st_pos": 8, "bit_len": 1},
                    {"name": "BCM_Central_unLock_CMD", 0x0: "Inactive", 0x1: "Active", "bit_st_pos": 10, "bit_len": 1},
                    {"name": "BCM_HazardSts", 0x0: "Inactive", 0x1: "Active", "bit_st_pos": 15, "bit_len": 1},
                    {"name": "BCM_PositionLight", 0x0: "OFF", 0x1: "ON", "bit_st_pos": 21, "bit_len": 1},
                    {"name": "BCM_PowerMode", 0x0: "OFF", 0x1: "ACC", 0x2: "ON", 0x3: "Reserved", 0x4: "START",
                     0x5: "Reserved", 0x6: "Reserved", 0x7: "Reserved", "bit_st_pos": 32, "bit_len": 3}]
    elif can_id == 0x18FF8721:
        info_set.append("BCM_LightChimeReq")
        data_set = [
            {"name": "BCM_FrontLeftDoorAjarStatus", 0x0: "DoorClosed", 0x1: "DoorAjar", "bit_st_pos": 4, "bit_len": 1},
            {"name": "BCM_FrontRightDoorAjarStatus", 0x0: "DoorClosed", 0x1: "DoorAjar", "bit_st_pos": 5, "bit_len": 1},
            {"name": "BCM_AnyDoorAjar", 0x0: "Inactive", 0x1: "Active", "bit_st_pos": 11, "bit_len": 1}]
    elif can_id == 0x18FFD521:
        info_set.append("BCM_MMIFBSts")
        data_set = [{"name": "BCM_HomeSafetyLightsTimeResp", 0X0: "No Delay", 0x1: "30s", 0x2: "60s", 0x3: "90s",
                     0x4: "Set Resp Fail", "bit_st_pos": 10, "bit_len": 3},
                    {"name": "BCM_SWM_HeatdSteerWhlDiagc", 0x0: "OK", 0x1: "CmnFailr", 0x2: "NotEdgePres",
                     0x3: "EdgeSho", 0x4: "SnsrFltT", 0x5: "FltPwrSplyErr", 0x6: "FltSwtHiSide", 0x7: "SigFailr",
                     "bit_st_pos": 25, "bit_len": 3},
                    {"name": "BCM_RearDefrostKeyRequest", 0x0: "No Request", 0x1: "Off", 0x2: "On", 0x3: "Reserved",
                     "bit_st_pos": 28, "bit_len": 2},
                    {"name": "BCM_RearfoldRequest", 0x0: "No Request", 0x1: "Off", 0x2: "On", 0x3: "Reserved",
                     "bit_st_pos": 30, "bit_len": 2}]
    elif can_id == 0x18FA7F21:
        info_set.append("SWS-LIN")
        data_set = [{"name": "BtnR1Req", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_Psd", "bit_st_pos": 0, "bit_len": 1},
                    {"name": "BtnR2Req", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_SPsd", 0x2: "PsdNotPsd_LPsd",
                     0x3: "Reserved", "bit_st_pos": 1, "bit_len": 2},
                    {"name": "BtnR3Req", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_SPsd", 0x2: "PsdNotPsd_LPsd",
                     0x3: "Reserved", "bit_st_pos": 3, "bit_len": 2},
                    {"name": "BtnR4Req", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_Psd", "bit_st_pos": 5, "bit_len": 1},
                    {"name": "BtnR5Req", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_Psd", "bit_st_pos": 6, "bit_len": 1},
                    {"name": "BtnR7Req", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_Psd", "bit_st_pos": 7, "bit_len": 1},
                    {"name": "BtnR6Req", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_SPsd", 0x2: "PsdNotPsd_LPsd",
                     0x3: "Reserved", "bit_st_pos": 8, "bit_len": 2},
                    {"name": "DiagcFailrSWSM", 0x0: "DiagcFailrSWSM_NoFailr", 0x1: "DiagcFailrSWSM_CmnFailr",
                     0x2: "DiagcFailrSWSM_CoupldFailr", 0x3: "DiagcFailrSWSM_Spare", "bit_st_pos": 10, "bit_len": 2},
                    {"name": "RotyPosReq5", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_SPsd", 0x2: "PsdNotPsd_LPsd",
                     0x3: "Reserved", "bit_st_pos": 12, "bit_len": 2},
                    {"name": "RotyDirReq5", 0x0: "PsdNotPsd_NotPsd", 0x1: "PsdNotPsd_SPsd", 0x2: "PsdNotPsd_LPsd",
                     0x3: "Reserved", "bit_st_pos": 14, "bit_len": 2}]
    elif can_id == 0x18FF0721:
        info_set.append("SwmCem_Lin4Fr02")
        data_set = [{"name": "SWM_SteerWhlHeatgPwrOn", 0x0: "Off", 0x1: "On", "bit_st_pos": 2, "bit_len": 1}]
    elif can_id == 0x18DA41F1:
        info_set.append("MMI_DiagReq")
        data_set = []
    elif can_id == 0x18DAF141:
        info_set.append("MMI_DiagResp")
        data_set = []
    elif can_id == 0x18DB33F1:
        info_set.append("Func_DiagReq")
        data_set = []
    elif can_id == 0x0CFA01EF:
        info_set.append("MCU_MotorElePara")
        data_set = [{"name": "MCU_MotorDCPower", "bit_st_pos": 32, "bit_len": 16}]
    elif can_id == 0x18FA40F4:
        info_set.append("BMS_BatteryInfo")
        data_set = [{"name": "BMS_BattVolt", "bit_st_pos": 0, "bit_len": 16},
                    {"name": "BMS_BattCurr", "bit_st_pos": 16, "bit_len": 16},
                    {"name": "BMS_BattSOC", "bit_st_pos": 32, "bit_len": 8},
                    {"name": "BMS_BattSOH", "bit_st_pos": 40, "bit_len": 8}]
    elif can_id == 0x18FA3EF4:
        info_set.append("BMS_ChgInfo")
        data_set = [
            {"name": "BMS_ChgStatus", 0x0: "Default", 0x1: "Charging", 0x2: "Charge End", 0x3: "Error Charge Stop",
             0x4: "Heating", 0x5: "Cooling", 0x6: "Charge Pause", 0x7: "Other Charge Stop", 0x8: "Reserved",
             0x9: "Reserved", 0xA: "Reserved", 0xB: "Reserved", 0xC: "Reserved", 0xD: "Reserved", 0xE: "Reserved",
             0xF: "Reserved", "bit_st_pos": 4, "bit_len": 4},
            {"name": "BMS_DCChgPlugSts", 0x0: "Disconnected", 0x1: "Connected", 0x2: "Reserved", 0x3: "Invalid",
             "bit_st_pos": 8, "bit_len": 2}]
    elif can_id == 0x18FAB327:
        info_set.append("PMS_VRI")
        data_set = [{"name": "PMS_VehCruisingDistance", "bit_st_pos": 0, "bit_len": 32}]
    elif can_id == 0x1CFFD841:
        info_set.append("MMI_Debug")
        data_set = [{"name": "APSleepCheckTimer", "bit_st_pos": 0, "bit_len": 12},
                    {"name": "AP_Status1_PIN", "bit_st_pos": 12, "bit_len": 1},
                    {"name": "APSPIALiveCount", "bit_st_pos": 16, "bit_len": 8},
                    {"name": "C_CAN_BusOff", "bit_st_pos": 32, "bit_len": 2},
                    {"name": "BCM_RxStatus", "bit_st_pos": 40, "bit_len": 2},
                    {"name": "APSleepStatusPIN", "bit_st_pos": 56, "bit_len": 1},
                    {"name": "EEP_Init", "bit_st_pos": 57, "bit_len": 1},
                    {"name": "AP_Boot_Complete", "bit_st_pos": 58, "bit_len": 1},
                    {"name": "AP_Camera_Control", "bit_st_pos": 59, "bit_len": 1},
                    {"name": "AP_BT_WiFi_Menu_Status", "bit_st_pos": 60, "bit_len": 1},
                    {"name": "SPI_BCM_PowerMode", "bit_st_pos": 61, "bit_len": 3}]
    else:
        info_set.append("No matching id")
    info_set += data_set
    return info_set


def data_matcher(tx, sub_mess):
    sig = ''
    byte_len = int(sub_mess["bit_len"] / 8)
    if sub_mess["bit_len"] < 8:
        byte_len += 1
    for i in range(byte_len):
        byte_pos = int(sub_mess["bit_st_pos"] / 8) + i
        sig += str(signal_idendifier(tx, byte_pos, sub_mess))
    return sig


def signal_idendifier(tx, byte_pos, sub_mess):
    bin_data = bin(tx.data[byte_pos])[2:].zfill(8)
    bin_st_pos = 8 - sub_mess["bit_st_pos"] % 8 - sub_mess["bit_len"]
    sig = int(bin_data[bin_st_pos:bin_st_pos + sub_mess["bit_len"]], 2)
    return sig