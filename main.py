# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import canopen

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # # a = int("1C", 16)
    # # b = bin(a)[2:]
    # # print(b)
    # # print(b.zfill(8))
    # #
    # # a = '1'
    # # b = a.rjust(64, '1')
    # # print(b)
    # # print(a)
    # # print(hex(int(b, 2)))
    #
    # value = ["L", "M", "P", "A", "1", "K", "M", "B", "7", "N", "C", "0", "0", "1", "2", "3", "4"]
    # list = [hex(ord(ch)) for ch in value]
    # print(list)

    network = canopen.Network()

    network.connect(ustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
