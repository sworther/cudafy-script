#!/usr/bin/env python3

import numpy as np

loop_dic = {"nx": 192, "ny": 64, "nz": 32}



def tridiag(a, b, c, k1=-1, k2=0, k3=1):
    return np.diag(a, k1) + np.diag(b, k2) + np.diag(c, k3)


for ta in [1.0, 1.5]:
    for loop in loop_dic.items():
        for it in [1, 2, 4]:
            loop_cur = loop[1] // it
            ul_diag = [-ta] * (loop_cur - 1)
            mm_diag = [2*ta+1] * loop_cur

            mat = tridiag(ul_diag, mm_diag, ul_diag)
            mat_inver = np.linalg.inv(mat)

            filename = "tridiag_{}_{}_div{}.csv".format(ta, loop[0], it)
            np.savetxt(filename, mat_inver, delimiter=" ")

