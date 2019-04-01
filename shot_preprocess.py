import os
import shutil
import subprocess
import numpy as np
import shotanalysis as sa


decode_path = "/home/gelijian/EAST/TOFED_DAQ/decode_and_coin/build/decode"
coin_path = "/home/gelijian/EAST/TOFED_DAQ/decode_and_coin/build/coin"
DGZ_type_list = ["751", "APV"]
dir_data = "/home/gelijian/EAST/shot_data/2017"
s1list = [0, 1, 2, 3, 4]
s2list = [5, 6, 8, 9, 10, 11, 12, 13, 14]
s2up = [5, 6, 8, 9]
s2bottom = [10, 11, 12, 13, 14]
reflist = [7, 15]

shotlist = np.arange(75030, 75080)
for shot in shotlist:
    dir_shot = os.path.join(dir_data, "%d" % shot)
    print(dir_shot)
    if not os.path.exists(dir_shot):
        print("%s does not exist"%dir_shot)
        continue

    # # decode data
    # print("Decoding data for V1751 boards and APV boards start")
    # command = "%s %s/" % (decode_path, dir_shot)
    # p1 = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    # p1.communicate()
    # print("Decoding data for V1751 boards and APV boards finished")

    # do coincidence for TOFED data
    # command = "%s %s/" % (coin_path, dir_shot)
    # print("Doing coincidence for TOFED data start")
    # p2 = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    # p2.communicate()
    # print("Doing coincidence for TOFED data finished")

    # Correct coincidence data
    print("Calculated board offset for TOFED start")
    # reflist = [0, 8, 16, 24]
    m = sa.TOFEDdata()
    m.set_dir_shot(dir_shot)
    m.set_up_ring(s2up)
    m.set_bottom_ring(s2bottom)
    data_shot = np.empty((0, 5))

    for DGZ_type in sa.Digitizer:
        file_div = os.path.join(dir_data, "%s_divergence_old" % sa.DGZ_cfg[DGZ_type]["name"])
        m.set_DGZ_type(DGZ_type)
        # m.cal_board_offset(reflist)
        m.load_board_offset()
        m.load_divergence(file_div)
        data = m.load_pairs(s1list, s2list, include_divergence=True)
        if data.shape[0] > 1:
            data_shot = np.vstack((data_shot, data))
    filename = os.path.join(dir_shot, "TOFED_data")
    np.savetxt(filename, data_shot, fmt="%g")
    print("Calculated board offset for TOFED finished")
    print("")
