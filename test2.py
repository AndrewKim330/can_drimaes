import time

from gs_usb.gs_usb import GsUsb
# from gs_usb.gs_usb_frame import GsUsbFrame
# from gs_usb.constants import (
#     CAN_EFF_FLAG,
#     CAN_ERR_FLAG,
#     CAN_RTR_FLAG,
# )

devs = GsUsb.scan()
if len(devs) == 0:
    print("Can not find gs_usb device")
dev = devs[0]
#
# # Configuration
# if not dev.set_bitrate(250000):
#     print("Can not set bitrate for gs_usb")
#     return
#
# # Start device
# dev.start()