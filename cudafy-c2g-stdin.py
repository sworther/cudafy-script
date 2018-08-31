#!/usr/bin/env python3
import fire
# from pprint import pprint
import collections
import re
import sys


class Cudafy():
    """
    convert array subscript in a  cpp file to a cuda  version
    require array stored as "cuda-array.cpp" in current directory
    """

    def __init__(self):
        """
        store array of separate dimension in separate dict
        array has three different dimension
        for 4D: there are four different type
            s1xn[ng_e + 1][nz_e + 2][ny_e + 1][nx_e + 1],
            q11[nt_e + 1][nz_e + 2][ny_e + 2][nx_e + 2],
            gradfi[16][nz_e + 2][ny_e + 2][nx_e + 2],
            betaxn[nt_e + 1][ng_e + 1][nz_e + 1][ny_e + 1],

            betaxn[nt_e + 1][ng_e + 1][nz_e + 1][ny_e + 1],
        for 3D: one type just different offset
            av1[nz_e + 2][ny_e + 2][nx_e + 2],
        for 2D:

            betax[nz_e + 1][ny_e + 1],
            double dm[nt_e + 1][nt_e + 1]; (only this one case)
        """
        # _fourdict_di : di stands for digit
        self._fourdict_di = collections.defaultdict(list)
        self._fourdict_ng = collections.defaultdict(list)
        self._fourdict_nt = collections.defaultdict(list)
        self._fourdict_tg = collections.defaultdict(list)
        self._threedict = collections.defaultdict(list)
        self._twodict_nz = collections.defaultdict(list)
        self._twodict_nt = collections.defaultdict(list)

        with open("./auxiliary/cuda-array.cpp", "r") as f:
            strlist = f.readlines()

            for line in strlist:
                # match for dimension
                m4 = re.match(r"""
                (?:[ ]*)
                \b(\w+)
                \[  .+?    \]
                \[  .+?    \]
                \[  .+?    \]
                \[  .+?    \]
                    """, line, re.M | re.X)

                if m4:
                    m4_nt = re.match(r"""
                    (?:[ ]*)
                    \b(\w+)
                    \[  nt_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  nz_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  nx_e  [ ]  \+  [ ] ([0-9])   \]
                        """, line, re.M | re.X)

                    m4_ng = re.match(r"""
                    (?:[ ]*)
                    \b(\w+)
                    \[  ng_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  nz_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  nx_e  [ ]  \+  [ ] ([0-9])   \]
                        """, line, re.M | re.X)

                    m4_di = re.match(r"""
                    (?:[ ]*)
                    \b(\w+)
                    \[  (\d+)   \]
                    \[  nz_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  nx_e  [ ]  \+  [ ] ([0-9])   \]
                        """, line, re.M | re.X)

                    m4_tg = re.match(r"""
                    (?:[ ]*)
                    \b(\w+)
                    \[  nt_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  ng_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  nz_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                        """, line, re.M | re.X)

                    if m4_nt:
                        key = m4_nt.group(2) + m4_nt.group(3) + m4_nt.group(
                            4) + m4_nt.group(5)
                        self._fourdict_nt[key].append(m4_nt.group(1))

                    elif m4_ng:
                        key = m4_ng.group(2) + m4_ng.group(3) + m4_ng.group(
                            4) + m4_ng.group(5)
                        self._fourdict_ng[key].append(m4_ng.group(1))

                    elif m4_di:
                        key = m4_di.group(2) + '-' + m4_di.group(
                            3) + m4_di.group(4) + m4_di.group(5)
                        self._fourdict_di[key].append(m4_di.group(1))

                    elif m4_tg:
                        key = m4_tg.group(2) + m4_tg.group(3) + m4_tg.group(
                            4) + m4_tg.group(5)
                        self._fourdict_tg[key].append(m4_tg.group(1))

                else:
                    m3 = re.match(r"""
                    (?:[ ]*)
                    \b(\w+)
                    \[  nz_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  nx_e  [ ]  \+  [ ] ([0-9])   \]
                        """, line, re.M | re.X)
                    if m3:
                        key = m3.group(2) + m3.group(3) + m3.group(4)
                        self._threedict[key].append(m3.group(1))

                    else:
                        m2 = re.match(r"""
                        (?:[ ]*)
                        \b(\w+)
                        \[  .+?    \]
                        \[  .+?    \]
                        """, line, re.M | re.X)

                        if m2:
                            m2_nz = re.match(r"""
                            (?:[ ]*)
                            \b(\w+)
                            \[  nz_e  [ ]  \+  [ ] ([0-9])   \]
                            \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                            """, line, re.M | re.X)

                            m2_nt = re.match(r"""
                            (?:[ ]*)
                            \b(\w+)
                            \[  nt_e  [ ]  \+  [ ] ([0-9])   \]
                            \[  nt_e  [ ]  \+  [ ] ([0-9])   \]
                                """, line, re.M | re.X)

                            if m2_nz:
                                key = m2_nz.group(2) + m2_nz.group(3)
                                self._twodict_nz[key].append(m2_nz.group(1))

                            elif m2_nt:
                                key = m2_nt.group(2) + m2_nt.group(3)
                                self._twodict_nt[key].append(m2_nt.group(1))

    def display(self):
        for name, elem in self.__dict__.items():
            for key, value in elem.items():
                print(name, ": ", key, "--", value)
            print()

    def find_arrs_in_func(self):
        """
        find referenced global cpu arrs in func
        :rtype: list
        """
        text = sys.stdin.read()
        arrs_in_func = re.findall(r"\b(\w+)(?=\[)", text)
        arrs_in_func = sorted(set(arrs_in_func))
        glo_fun_arrs = self.find_cpu_arrs()
        glo_fun_arrs = sorted(set(glo_fun_arrs) & set(arrs_in_func))
        return glo_fun_arrs

    def find_cpu_arrs(self):
        """
        find the cpu arrs in cuda-array.cpp file
        """
        with open("./auxiliary/cuda-array.cpp", "r") as f:
            text = f.read()
        arrs = re.findall(r"^(?:[ ]*)\b(\w+)(?=\[)", text, re.M)
        arrs_set = set(arrs)
        if len(arrs_set) != len(arrs):
            raise ValueError("duplicate arrs exist")
        return arrs

    def alloc(self):
        text = ""
        cpu_arrs = self.find_cpu_arrs()
        for arr in cpu_arrs:
            for dim, dic in self.__dict__.items():
                if dim.startswith("_fourdict_di"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("d_{arr} = alloc_pitch<double>"
                                    "((nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * {off4});\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[:2])
                            text += temp

                elif dim.startswith("_fourdict_tg"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("d_{arr} = alloc_pitch<double>"
                                    "((ny_e + {off1}), (nz_e + {off2} ),"
                                    " (ng_e + {off3}) * (nt_e  + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4])
                            text += temp

                elif dim.startswith("_fourdict_"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("d_{arr} = alloc_pitch<double>"
                                    "((nx_e + {off1}), (ny_e + {off2} ),"
                                    " (nz_e + {off3}) * ({dimends} + '_e' + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        dimends=dim[-2:],
                                        off4=offset[-4])
                            text += temp

                elif dim.startswith("_threedict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("d_{arr} = alloc_pitch<double>"
                                    "((nx_e + {off1}), (ny_e + {off2} ),"
                                    " (nz_e + {off3}));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3])
                            text += temp

                elif dim.startswith("_twodict_nz"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("d_{arr} = alloc_pitch<double>"
                                    "((ny_e + {off1}), (nz_e + {off2} ), 1);\n"
                                    ).format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp

                elif dim.startswith("_twodict_nt"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("d_{arr} = alloc_pitch<double>"
                                    "((nt_e + {off1}), (nt_e + {off2} ),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp
        sys.stdout.write(text)

    def dealloc(self):
        text = ""
        cpu_arrs = self.find_cpu_arrs()
        for arr in cpu_arrs:
            temp = "dealloc_pitch<double>(d_{arr}.ptr);\n".format(
                arr=arr)
            text += temp
        sys.stdout.write(text)

    def upload(self):
        text = ""
        cpu_arrs = self.find_cpu_arrs()
        for arr in cpu_arrs:
            for dim, dic in self.__dict__.items():
                if dim.startswith("_fourdict_di"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0][0][0],"
                                    " (nx_e + {off1}),"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * {off4});\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[:2])
                            text += temp

                elif dim.startswith("_fourdict_tg"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0][0][0],"
                                    " (ny_e + {off1}),"
                                    " (ny_e + {off1}), (nz_e + {off2}),"
                                    " (ng_e + {off3}) * (nt_e + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4])
                            text += temp

                elif dim.startswith("_fourdict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0][0][0],"
                                    " (nx_e + {off1}),"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * ({dimends} + '_e' + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4],
                                        dimends=dim[-2:])
                            text += temp

                elif dim.startswith("_threedict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0][0],"
                                    " (nx_e + {off1}),"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3])
                            text += temp

                elif dim.startswith("_twodict_nz"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0],"
                                    " (ny_e + {off1}),"
                                    " (ny_e + {off1}), (nz_e + {off2}),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp

                elif dim.startswith("_twodict_nt"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0],"
                                    " (nt_e + {off1}),"
                                    " (nt_e + {off1}), (nt_e + {off2}),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp
        sys.stdout.write(text)

    def download(self):
        text = ""
        cpu_arrs = self.find_cpu_arrs()
        for arr in cpu_arrs:
            for dim, dic in self.__dict__.items():
                if dim.startswith("_fourdict_di"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0][0][0],"
                                    " (nx_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * {off4});\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[:2])
                            text += temp

                elif dim.startswith("_fourdict_tg"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0][0][0],"
                                    " (ny_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (ny_e + {off1}), (nz_e + {off2}),"
                                    " (ng_e + {off3}) * (nt_e + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4])
                            text += temp

                elif dim.startswith("_fourdict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0][0][0],"
                                    " (nx_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * ({dimends} + '_e' + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4],
                                        dimends=dim[-2:])
                            text += temp

                elif dim.startswith("_threedict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0][0],"
                                    " (nx_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3])
                            text += temp

                elif dim.startswith("_twodict_nz"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0],"
                                    " (ny_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (ny_e + {off1}), (nz_e + {off2}),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp

                elif dim.startswith("_twodict_nt"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0],"
                                    " (nt_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (nt_e + {off1}), (nt_e + {off2}),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp
        sys.stdout.write(text)


    def upload_func(self):
        arrs_in_func = self.find_arrs_in_func()
        text = ""
        for arr in arrs_in_func:
            for dim, dic in self.__dict__.items():
                if dim.startswith("_fourdict_di"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0][0][0],"
                                    " (nx_e + {off1}),"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * {off4});\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[:2])
                            text += temp

                elif dim.startswith("_fourdict_tg"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0][0][0],"
                                    " (ny_e + {off1}),"
                                    " (ny_e + {off1}), (nz_e + {off2}),"
                                    " (ng_e + {off3}) * (nt_e + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4])
                            text += temp

                elif dim.startswith("_fourdict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0][0][0],"
                                    " (nx_e + {off1}),"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * ({dimends}_e + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4],
                                        dimends=dim[-2:])
                            text += temp

                elif dim.startswith("_threedict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0][0],"
                                    " (nx_e + {off1}),"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3])
                            text += temp

                elif dim.startswith("_twodict_nz"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0],"
                                    " (ny_e + {off1}),"
                                    " (ny_e + {off1}), (nz_e + {off2}),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp

                elif dim.startswith("_twodict_nt"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("upload_pitch<double>(d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " &{arr}[0][0],"
                                    " (nt_e + {off1}),"
                                    " (nt_e + {off1}), (nt_e + {off2}),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp
        sys.stdout.write(text)

    def download_func(self):
        arrs_in_func = self.find_arrs_in_func()
        text = ""
        for arr in arrs_in_func:
            for dim, dic in self.__dict__.items():
                if dim.startswith("_fourdict_di"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0][0][0],"
                                    " (nx_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * {off4});\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[:2])
                            text += temp

                elif dim.startswith("_fourdict_tg"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0][0][0],"
                                    " (ny_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (ny_e + {off1}), (nz_e + {off2}),"
                                    " (ng_e + {off3}) * (nt_e + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4])
                            text += temp

                elif dim.startswith("_fourdict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0][0][0],"
                                    " (nx_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}) * ({dimends}_e + {off4}));\n"
                                    ).format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4],
                                        dimends=dim[-2:])
                            text += temp

                elif dim.startswith("_threedict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0][0],"
                                    " (nx_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (nx_e + {off1}), (ny_e + {off2}),"
                                    " (nz_e + {off3}));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3])
                            text += temp

                elif dim.startswith("_twodict_nz"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0],"
                                    " (ny_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (ny_e + {off1}), (nz_e + {off2}),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp

                elif dim.startswith("_twodict_nt"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("download_pitch<double>(&{arr}[0][0],"
                                    " (nt_e + {off1}),"
                                    " d_{arr}.ptr,"
                                    " d_{arr}.width_pitch,"
                                    " (nt_e + {off1}), (nt_e + {off2}),"
                                    " 1);\n").format(
                                        arr=arr, off1=offset[-1], off2=offset[-2])
                            text += temp
        sys.stdout.write(text)

    def register_cpu_arrs(self):
        arrs_in_func = self.find_arrs_in_func()
        text = ""
        for arr in arrs_in_func:
            for dim, dic in self.__dict__.items():
                if dim.startswith("_fourdict_di"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("checkCudaErrors(cudaHostRegister((void *)&{arr}[0][0][0][0],"
                                    " (nx_e + {off1}) * (ny_e + {off2}) * (nz_e + {off3}) * {off4}"
                                    " * sizeof(double), cudaHostRegisterPortable));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[:2])
                            text += temp

                elif dim.startswith("_fourdict_tg"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("checkCudaErrors(cudaHostRegister((void *)&{arr}[0][0][0][0],"
                                    " (ny_e + {off1}) * (nz_e + {off2}) * (ng_e + {off3}) * (nt_e + {off4})"
                                    " * sizeof(double), cudaHostRegisterPortable));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4])
                            text += temp

                elif dim.startswith("_fourdict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("checkCudaErrors(cudaHostRegister((void *)&{arr}[0][0][0][0],"
                                    " (nx_e + {off1}) * (ny_e + {off2}) * (nz_e + {off3}) * ({dimends} + '_e' + {off4})"
                                    " * sizeof(double), cudaHostRegisterPortable));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3],
                                        off4=offset[-4],
                                        dimends=dim[-2:])
                            text += temp

                elif dim.startswith("_threedict"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("checkCudaErrors(cudaHostRegister((void *)&{arr}[0][0][0],"
                                    " (nx_e + {off1}) * (ny_e + {off2}) * (nz_e + {off3})"
                                    " * sizeof(double), cudaHostRegisterPortable));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2],
                                        off3=offset[-3])
                            text += temp

                elif dim.startswith("_twodict_nz"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("checkCudaErrors(cudaHostRegister((void *)&{arr}[0][0],"
                                    " (ny_e + {off1}) * (nz_e + {off2})"
                                    " * sizeof(double), cudaHostRegisterPortable));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2])
                            text += temp

                elif dim.startswith("_twodict_nt"):
                    for offset, arrs in dic.items():
                        if arr in arrs:
                            temp = ("checkCudaErrors(cudaHostRegister((void *)&{arr}[0][0],"
                                    " (nt_e + {off1}) * (nt_e + {off2})"
                                    " * sizeof(double), cudaHostRegisterPortable));\n").format(
                                        arr=arr,
                                        off1=offset[-1],
                                        off2=offset[-2])
                            text += temp
        sys.stdout.write(text)


if __name__ == '__main__':
    cudafy = Cudafy()
    fire.Fire(cudafy)
