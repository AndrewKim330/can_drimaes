# from bs4 import BeautifulSoup
# import pandas as pd
import pprint as pp
import binascii

# def getd():

def test():
    a = 'ggg'
    print(int(a))

def scr():
    with open('wefab.asc', 'r') as f:
        temp_a = f.read()

    # print(temp_a)

    temp = temp_a.split()

    li = []
    dtc = []
    dtc_num = 0
    dtc_flag = False
    multi_flag = False
    i = 0
    while i < len(temp):
        temp_li = []
        if temp[i] == '18DA41F1x':
            temp_li.append('GST_MMI')
            temp_li.append(temp[i])
            for j in range(8):

                temp_li.append(temp[i + 4 + j])
            i += j
            li.append(temp_li)
        elif temp[i] == '18DAF141x':
            temp_li.append('MMI_GST')
            temp_li.append(temp[i])
            for j in range(8):
                temp_li.append(temp[i + 4 + j])
            i += j
            li.append(temp_li)
        else:
            i += 1
        j = 0
        while j < len(temp_li):
            dtc_num = 0
            if multi_flag:
                while dtc_num < 3:
                    if dtc_flag:
                        try:
                            dtc.append(hex(int(temp_li[j + dtc_num], 16)))
                            dtc_num += 1
                        except ValueError:
                            break
                        except IndexError:
                            break
                    else:
                        if temp_li[j] == '09':
                            dtc_flag = True
                        break
            else:
                if temp_li[2] == "03":
                    status_mask = temp_li[5]
                elif temp_li[2] == '30':
                    multi_flag = True
                break

            if dtc_num > 0:
                j += dtc_num
            else:
                j += 1
        print(dtc)

    # pp(li)
    #
    # for i in range(len(temp)):
    #     temp_li = []
    #     if temp[i] == '18DA41F1x':
    #         temp_li.append('GST_MMI')
    #         temp_li.append(temp[i])
    #         for j in range(8):
    #             temp_li.append(temp[i + 4 + j])
    #         li.append(temp_li)
    #     elif temp[i] == '18DAF141x':
    #         temp_li.append('MMI_GST')
    #         temp_li.append(temp[i])
    #         for j in range(8):
    #             temp_li.append(temp[i + 4 + j])
    #         li.append(temp_li)
    #     if len(temp_li) != 0:
    #         if multi_flag:
    #             while dtc_num < 4:
    #                 if temp[i] == '09':
    #                     dtc_num = 1
    #                     break
    #                 try:
    #                     dtc.append(int(temp[i+dtc_num]))
    #                     dtc_num += 1
    #                 except ValueError:
    #                     break
    #                 except IndexError:
    #                     break
    #             print(dtc)
    #
    #         else:
    #             if temp_li[2] == '03':
    #                 status_mask = temp_li[5]
    #             elif temp_li[2] == '30':
    #                 multi_flag = True
    #                 line = int(temp_li[4], 16)
        #
        # if dtc_flag:
        #     while dtc_num < 3:
        #         if temp[i] == '09':
        #             dtc_num = 1
        #         try:
        #             b = int(temp[i + dtc_num])
        #             dtc.append(b)
        #             dtc_num += 1
        #         except ValueError:
        #             pass
        # else:

    pp.pprint(li)


if __name__ == "__main__":
    scr()
    # test()