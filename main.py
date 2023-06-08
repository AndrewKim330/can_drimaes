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
    value1 = [0x49, 0x56, 0x49, 0x30, 0x58, 0x30]
    list1 = [chr(asc) for asc in value1]
    value2 = ["L", "M", "P", "A", "1", "K", "M", "B", "7", "N", "C", "0", "0", "2", "0", "9", "0"]
    list2 = [hex(ord(ch)) for ch in value2]
    print(list2)
    #
    # network = canopen.Network()
    #
    # network.connect(ustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
