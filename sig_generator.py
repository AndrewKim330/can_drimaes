def binary_sig(hex_val, pos, bit_len, val):
    tt = bin(hex_val)[2:].zfill(8)
    val_bin = bin(val)[2:].zfill(bit_len)
    if pos > 0:
        temp = tt[:pos] + val_bin + tt[pos + len(val_bin):]
    else:
        temp = val_bin + tt[pos + len(val_bin):]
    return int(temp, 2)
