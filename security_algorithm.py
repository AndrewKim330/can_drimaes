def secu_algo(seed):
    xor = [0x69, 0x1d, 0xbe, 0x55]
    cal_data = []
    res = []

    for i in range(4):
        temp = int(seed[i], 16) ^ xor[i]
        cal_data.append(temp)

    res.append(((cal_data[3] & 0x0f) << 4) | (cal_data[3] & 0xf0))
    res.append(((cal_data[1] & 0x0f) << 4) | ((cal_data[0] & 0xf0) >> 4))
    res.append((cal_data[1] & 0xf0) | ((cal_data[2] & 0xf0) >> 4))
    res.append(((cal_data[0] & 0x0f) << 4) | (cal_data[2] & 0x0f))

    return res
