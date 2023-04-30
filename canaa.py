import pywinusb.hid as hid
import usb.core
import asyncio
import serial
import serial.tools.list_ports as sp


def good():
    print('sss')
    list = sp.comports()
    connected = []
    print(list)

    for i in list:
        print(i)

async def usb_test():
    vid = 0x1FB7
    pid = 0x0313

    device = usb.core.find(idVendor=vid, idProduct=pid)
    endpoint = device[0][(0, 0)][0]
    interface = device[0][(0, 0)].bInterfaceNumber
    device.set_interface_altsetting(interface, 0)

    print (device)

#
#     while True:
#         try:
#             data = await asyncio.wait_for(
#                 asyncio.get_running_loop().run_in_executor(None, device.read, endpoint.bEndpointAddress, endpoint.wMaxPacketSize), timeout=5.0
#             )
#             print(f'Received Data: {data}')
#         except asyncio.TimeoutError:
#             print('Timeout error occurred')
#         except usb.core.USBError as e:
#             if e.errno == 60:
#                 continue
#             else:
#                 raise
#
#     # data = device.read(endpoint, 16, timeout=10000)
#
#     print(interface)
#     #
#     # [(0, 0)].bEndpointAddress
#     #
#     # data = device.read(endpoint, 64, timeout=5000)
#     #
#     # print(data)
#
#
# #

if __name__ == "__main__":
    # asyncio.run(usb_test())
    good()