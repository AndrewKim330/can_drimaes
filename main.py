# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# import canopen

# ****need to fix to the bit length
def example(hex_val, pos, bit_len, val):
    a = bin(hex_val)[2:].zfill(8)
    val_bin = bin(val)[2:].zfill(bit_len)
    if pos > 0:
        temp = a[pos - 1] + val_bin + a[pos + len(val_bin):]
    else:
        temp = val_bin + a[pos + len(val_bin):]
    print(int(temp, 2))
    return hex(int(temp, 2))

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
    # value1 = [0x49, 0x56, 0x49, 0x30, 0x58, 0x30]
    # list1 = [chr(asc) for asc in value1]
    # value2 = ["L", "M", "P", "A", "1", "K", "M", "B", "7", "N", "C", "0", "0", "2", "0", "9", "0"]
    # list2 = [hex(ord(ch)) for ch in value2]
    # # temp = a[0]+'1'+a[2:]
    # # a[0] = '1'
    # # print(temp)
    # a = example(0x01, 0, 2, 1)
    # print(a)
    # b = example(int(a, 16), 2, 2, 2)
    # print(b, type(b))

    # def sig_generator(hex_val, pos, bit_len, val):
    #     tt = bin(hex_val)[2:].zfill(8)
    #     val_bin = bin(val)[2:].zfill(bit_len)
    #     if pos > 0:
    #         temp = tt[:pos] + val_bin + tt[pos + len(val_bin):]
    #     else:
    #         temp = val_bin + tt[pos + len(val_bin):]
    #     return int(temp, 2)
    #
    # print(sig_generator(0x81, 4, 3, 2))



    # color_str = f"\"color : {color}\""
    # print(color_str)

    # tpms_and_sidemirror_mani_bin = bin(int(sig, 16))[2:].zfill(8)
    # print(list2)
    #
    # network = canopen.Network()
    #
    # network.connect(ustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
