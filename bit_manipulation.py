def bit_mani(use_bit_li):
    # a = ''
    # b = a.rjust(use_bit_li[0][0], '1')

    a = []
    for signal_bit in use_bit_li:
        for j in range(signal_bit[1]):
            # b += '0'
            a.append(signal_bit[0] + j)
    print(a)


if __name__ == '__main__':
    showApp = [[0, 2], [2, 4], [8, 2], [10, 2], [12, 2], [14, 2], [16, 2], [18, 2]]
    bit_mani(showApp)