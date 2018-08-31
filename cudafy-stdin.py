#!/usr/bin/env python3
import fire
import collections
import re
import sys


class Cudafy():
    """
    convert array subscript in a  cpp file to a cuda  version
    require array stored as "cuda-array.cpp" in current directory
    """

    def __init__(self):
        """store array of separate dimension in separate dict"""
        self._fourdict = collections.defaultdict(list)
        self._fourdict_nt = collections.defaultdict(list)
        self._threedict = collections.defaultdict(list)
        self._twodict = collections.defaultdict(list)

        with open("./auxiliary/cuda-array.cpp", "r") as f:
            strlist = f.readlines()

            for line in strlist:
                # search for dimension
                m4 = re.search(r"""
                \b(\w+)
                \[  .*    \]
                \[  nz_e  [ ]  \+  [ ] ([0-9])   \]
                \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                \[  nx_e  [ ]  \+  [ ] ([0-9])   \]
                    """, line, re.M | re.X)

                if m4:
                    self._fourdict[m4.group(2) + m4.group(3) +
                                   m4.group(4)].append(m4.group(1))
                else:
                    m4_nt = re.search(r"""
                    \b(\w+)
                    \[  .*    \]
                    \[  ng_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  nz_e  [ ]  \+  [ ] ([0-9])   \]
                    \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                        """, line, re.M | re.X)
                    if m4_nt:
                        self._fourdict_nt[m4_nt.group(2) + m4_nt.group(3) +
                                          m4_nt.group(4)].append(
                                              m4_nt.group(1))
                    else:
                        m3 = re.search(r"""
                        \b(\w+)
                        \[  nz_e  [ ]  \+  [ ] (?:[0-9])   \]
                        \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                        \[  nx_e  [ ]  \+  [ ] ([0-9])   \]
                            """, line, re.M | re.X)
                        if m3:
                            self._threedict[m3.group(2) + m3.group(3)].append(
                                m3.group(1))
                        else:
                            m2 = re.search(r"""
                            \b(\w+)
                            \[  nz_e  [ ]  \+  [ ] (?:[0-9])   \]
                            \[  ny_e  [ ]  \+  [ ] ([0-9])   \]
                                """, line, re.M | re.X)
                            if m2:
                                self._twodict[m2.group(2)].append(m2.group(1))

        # print(self._twodict)
        # print(self._threedict.keys())
        # print(self._fourdict.keys())
        # print(self._fourdict_nt)

    def kji_irregular(self):
        """
            change IRREGULAR index of  array
            for example :
            q11[n][k][j][1]  to
            d_q11.ptr[ indexFour222(1, j, k, n)
        """

        text = sys.stdin.read()

        for key in self._twodict:
            # substitute for av1[ index(width, height, depth) ] = 0 like
            regex = re.compile(r"""
            \b(%s)
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            """ % ("|".join(self._twodict[key])), re.M | re.X)
            text = regex.sub(r"d_\1.ptr[ indexTwo" + r"(\3, \2) ]", text)

        for key in self._threedict:
            # substitute for av1[ index(width, height, depth) ] = 0 like
            regex = re.compile(r"""
            \b(%s)
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            """ % ("|".join(self._threedict[key])), re.M | re.X)
            text = regex.sub(r"d_\1.ptr[ index" + key + r"(\4, \3, \2) ]",
                             text)

        for key in self._fourdict:
            # substitute for av1[ index(width, height, depth) ] = 0 like
            regex = re.compile(r"""
            \b(%s)
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            """ % ("|".join(self._fourdict[key])), re.M | re.X)
            text = regex.sub(
                r"d_\1.ptr[ indexFour" + key + r"(\5, \4, \3, \2) ]", text)

        for key in self._fourdict_nt:
            # substitute for av1[ index(width, height, depth) ] = 0 like
            regex = re.compile(r"""
            \b(%s)
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            \[   ([^\]]+)   \]
            """ % ("|".join(self._fourdict_nt[key])), re.M | re.X)
            text = regex.sub(r"d_\1.ptr[ indexFour_nt" + r"(\5, \4, \3, \2) ]",
                             text)

        sys.stdout.write(text)

    def kji_general_offset(self):
        """
        change index of 3D and 4D array with k,j,i like subscript
        for example :
        pvx[k][j][i - 1] -> d_pvx.ptr[ index22(width - 1, height , depth ) ]
        """

        text = sys.stdin.read()

        # substitute for [\w+][k][j][i+-]
        for key in self._fourdict:
            regex = re.compile(r"""
            \b(%s)
            \[  (\w+) [ ]*      \]
            \[ [ ]* k [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            \[ [ ]* j [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            \[ [ ]* i [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            """ % ("|".join(self._fourdict[key])), re.M | re.X)
            text = regex.sub(r"d_\1.ptr[ indexFour" + key +
                             r"(width \7, height \5, depth \3, \2 ) ]", text)

        for key in self._fourdict_nt:
            regex = re.compile(r"""
            \b(%s)
            \[  (\w+) [ ]*      \]
            \[ [ ]* k [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            \[ [ ]* j [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            \[ [ ]* i [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            """ % ("|".join(self._fourdict_nt[key])), re.M | re.X)
            text = regex.sub(r"d_\1.ptr[ indexFour_nt" +
                             r"(width \7, height \5, depth \3, \2 ) ]", text)

        # substitute for [k][j+-][i]
        for key in self._threedict:
            regex = re.compile(r"""
            \b(%s)
            \[ [ ]* k [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            \[ [ ]* j [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            \[ [ ]* i [ ]*  (([+-]  [ ]*  [0-9])?) [ ]*   \]
            """ % ("|".join(self._threedict[key])), re.M | re.X)
            text = regex.sub(r"d_\1.ptr[ index" + key +
                             r"(width \6, height \4, depth \2) ]", text)

        sys.stdout.write(text)

    def for2if(self):
        """
        change three/two layers of  for loop to cuda if version
        notice
        1. there shouldn't have blank line among for loops,
        2. at least a blank line precede the whole loop
        3. for loop variable is k,j,i  k,i  k,j j,i
        """
        text = sys.stdin.read()

        # change for 3D k-j-i
        pattern = (
            r"("
            r"^[\t ]*for \(int k = ([012]); k < nz \+ ([12]); k\+\+\)[ ]*$\n"
            r"^[\t ]*for \(int j = ([012]); j < ny \+ ([12]); j\+\+\)[ ]*$\n"
            r"^[\t ]*for \(int i = ([012]); i < nx \+ ([12]); i\+\+\)"
            r")")
        replace = (
            r"/*\n\1\n*/\n\n"
            r"  if(width < (nx + \7) && height < (ny + \5) && depth < (nz + \3) && width >=\6 && height >=\4 && depth >= \2)"
        )
        regex = re.compile(pattern, re.M)
        text = regex.sub(replace, text)

        # change for 2D k-j
        pattern = (
            r"("
            r"^[\t ]*for \(int k = ([012]); k < nz \+ ([12]); k\+\+\)[ ]*$\n"
            r"^[\t ]*for \(int j = ([012]); j < ny \+ ([12]); j\+\+\)"
            r")"
            r"(?![\t ]*\n^[\t ]*\bfor\b.*$\n)")
        replace = (
            r"/*\n\1\n*/\n\n"
            r"\1\n"
            r"  if(width < (ny + \5) && height < (nz + \3) && width >=\4 && height >=\2)"
        )
        regex = re.compile(pattern, re.M)
        text = regex.sub(replace, text)

        # change for 2D k-i
        pattern = (
            r"("
            r"^[\t ]*for \(int k = ([012]); k < nz \+ ([12]); k\+\+\)[ ]*$\n"
            r"^[\t ]*for \(int i = ([012]); i < nx \+ ([12]); i\+\+\)"
            r")")
        replace = (
            r"/*\n\1\n*/\n\n"
            r"\1\n"
            r"  if(width < (nx + \5) && height < (nz + \3) && width >=\4 && height >=\2)"
        )
        regex = re.compile(pattern, re.M)
        text = regex.sub(replace, text)

        # change for 2D j-i
        pattern = (
            r"^$\n"
            r"("
            r"^[\t ]*for \(int j = ([012]); j < ny \+ ([12]); j\+\+\)[ ]*$\n"
            r"^[\t ]*for \(int i = ([012]); i < nx \+ ([12]); i\+\+\)"
            r")")
        replace = (
            r"/*\n\1\n*/\n\n"
            r"\1\n"
            r"  if(width < (nx + \5) && height < (ny + \3) && width >=\4 && height >=\2)"
        )
        regex = re.compile(pattern, re.M)
        text = regex.sub(replace, text)

        sys.stdout.write(text)

    def find_variable(self):
        """find the global variable used in a region"""

        int_globle_set = {
            "nb", "nt", "ng", "nxm1", "nym1", "nzm1", "nng0", "nitt", "nng",
            "ign", "it00", "lbb", "nxm", "nym", "nzm", "ibm", "itm", "jbm",
            "jtm", "nx", "ny", "nz", "ib", "it", "jb", "jt", "n", "ci",
            "cycle_by"
        }

        double_global_set = {
            "vxx", "vrr", "vtt", "vee", "y1", "z1", "rr", "vx", "vy", "vz",
            "wx", "wy", "wz", "ama", "dim", "en", "pp", "rpm", "ma", "sir",
            "cor", "c2", "cfl", "a4", "a2", "beta1", "beta2", "time_begin",
            "time_end", "time_t", "pi", "ta", "timl", "pt", "ht", "rout",
            "pb0", "pb1", "period", "rmsm", "rmsm0", "rmsmmax", "cvl0", "t0",
            "ts", "cp", "prt", "prl", "rg", "cv1", "cv2", "kap", "sigmav",
            "cb1", "cb2", "cw1", "cw2", "cw3", "cr1", "cr2", "cr3"
        }

        text_list = sys.stdin.readlines()
        text = "".join(text_list)

        # remove the situation to treat // as /
        variable_list = re.findall(r"""
        (?:[+\-*=<>] | (?<!/)[/])  [ ]* \b(\w+ | \w+[.]\w+)\b
        """, text, re.M | re.X)

        variable_list.extend(
            re.findall(r"""
            \b(\w+ | \w+[.]\w+)\b  [ ]*  (?:[+\-*=<>/])
            """, text, re.M | re.X))

        # find the global var as lvalue
        lvalue_global_list = re.findall(r"""
        ^ [ \t]* \b(\w+ | \w+[.]\w+)\b  [ \t]*  [=]
        """, text, re.M | re.X)

        local_variable_list = []

        for line in text_list:
            match_res = re.match(r"^[ ]*int[ ][\w, ]+;[ ]*$", line)
            if match_res:
                local_variable_list.extend(re.findall(r"\b(\w+)[,;]", line))

            match_res = re.match(r"^[ ]*double[ ][\w, ]+;[ ]*$", line)
            if match_res:
                local_variable_list.extend(re.findall(r"\b(\w+)[,;]", line))

        variable_set = set(variable_list)
        # remove array and number literal and remove certain elements
        variable_set = {
            x
            for x in variable_set
            if not (
                re.match(r"d_[\w.]+", x) or re.match(r"[0-9]+([.][0-9]+)?", x)
                or re.match(r"thread[\w.]+", x) or re.match(r"block[\w.]+", x))
        }

        # enum other literal to remove
        remove_set = {
            "k", "j", "i", "width", "height", "depth", "threadIdx", "blockIdx",
            "abs", "pow", "sqrt", "max", "min", "blockDim"
        }

        variable_set = variable_set - remove_set
        local_variable_set = set(local_variable_list)

        # set the used set
        int_used_set = variable_set & int_globle_set
        double_used_set = variable_set & double_global_set

        lvalue_used_set = set(lvalue_global_list) & (int_globle_set
                                                     | double_global_set)
        lvalue_int_used_set = set(lvalue_used_set) & int_globle_set
        lvalue_double_used_set = set(lvalue_used_set) & double_global_set

        # remove the double used global lvalue in the double set
        double_used_set -= lvalue_double_used_set

        # if variable defined in global and local, use the local one
        int_used_set -= local_variable_set
        double_used_set -= local_variable_set
        lvalue_int_used_set -= local_variable_set
        lvalue_double_used_set -= local_variable_set

        not_found_set = variable_set - (int_globle_set | double_global_set
                                        | lvalue_double_used_set
                                        | local_variable_set)

        # modify the content
        int_used_set = {"int " + x for x in int_used_set}
        double_used_set = {"double " + x for x in double_used_set}

        int_used_string = ", ".join(sorted(int_used_set))
        double_used_string = ", ".join(sorted(double_used_set))
        local_variable_string = ", ".join(sorted(local_variable_set))
        not_found_string = ", ".join(sorted(not_found_set))
        lvalue_double_used_string = ", ".join(sorted(lvalue_double_used_set))
        lvalue_int_used_string = ", ".join(sorted(lvalue_int_used_set))

        # output sequence in the first two line shouldn't be change so careless
        sys.stdout.write("global lval double:" + lvalue_double_used_string + (";" if lvalue_double_used_string  else "") + "\n")
        sys.stdout.write(int_used_string + (
            ", " if double_used_string else ",") + double_used_string)
        if (double_used_string):
            sys.stdout.write(", ")
        sys.stdout.write("\n")
        sys.stdout.write("not found    : " + not_found_string + "\n")
        sys.stdout.write("local var    : " + local_variable_string + "\n")
        sys.stdout.write("global lval int: " + lvalue_int_used_string +  (";" if lvalue_int_used_string else "") +  "\n")

    def find_array(self):
        text = sys.stdin.read()
        array_list = re.findall(r"d_\w+", text)
        array_list = sorted(set(array_list))

        array_list = [("\n"
                       if index % 3 == 0 else "") + "pitch_ref<double> " + x
                      for index, x in enumerate(array_list)]
        array_string = ", ".join(array_list)
        # delete the whitespace in the line end
        array_string = array_string.replace(" \n", "\n")
        sys.stdout.write(array_string)

    def find_cpu_arrs(self):
        text = sys.stdin.read()
        array_list = re.findall(r"\b(\w+)(?=\[)", text)
        array_list = sorted(set(array_list))
        array_string = ", ".join(array_list)
        sys.stdout.write(array_string)

    def make_3D_wrapper(self):
        text = sys.stdin.read()
        kernels = re.findall(r"^[ ]*__global__.+?[)]", text, re.M | re.S)

        for i in range(len(kernels)):
            kernels[i] = kernels[i].replace("__global__ ", "")
            kernels[i] = kernels[i].replace("void ", "")
            kernels[i] = kernels[i].replace("(", "<<<dimGrid, dimBlock>>>(", 1)
            kernels[i] = kernels[i].replace("int ", "")
            kernels[i] = kernels[i].replace("double ", "")
            kernels[i] = kernels[i].replace("pitch_ref<double> ", "")
            # delete whitespace in the line end
            kernels[i] = kernels[i].replace(" \n", "\n")

            name = re.search(r"(?<=cuda_)(.+?)<", kernels[i])
            chk_error = 'getLastCudaError("cuda {} failed")'.format(
                name.group(1))

            kernels[i] = "  " + kernels[i] + ";\n" + "  " + chk_error + ";\n"

        for item in kernels:
            sys.stdout.write(item + "\n")

    def func_name_transform(self):
        cpu2gpunames = {
            "copr": "cuda_copr_wrapper",
            "dddc": "cuda_dddc_wrapper",
            "dddsa": "cuda_ddd_wrappersa",
            "dsdt": "cuda_dsdt_wrapper",
            "geon": "cuda_geon_wrapper",
            "gradscentre": "cuda_gradscentre_wrapper",
            "gradsface": "cuda_gradsface_wrapper",
            "gradsfaceI": "cuda_g_wrapperradsfaceI",
            "gradsfaceJ": "cuda_gradsfaceJ_wrapper",
            "gradsfaceK": "cuda_gradsfaceK_wrapper",
            "pred": "cuda_pred_wrapper",
            "predsa": "cuda_predsa_wrapper",
            "qqqsa": "cuda_qqqsa_wrapper",
            "qqq": "cuda_qqq_wrapper",
            "ddd": "cuda_ddd_wrapper",
            "ppp": "cuda_ppp_wrapper",
            "qqqv": "cuda_qqqv_wrapper",
            "qqqvsa": "cuda_qqqvsa_wrapper",
            "SAsource": "Cuda_SAsource_Wrapper",
            "step": "cuda_step_wrapper",
            "tsd": "cuda_tsd_wrapper",
            "tsdsa": "cuda_tsdsa_wrapper",
            "update2": "cuda_update2_wrapper",
            "update": "cuda_update_wrapper",
            "ye": "cuda_ye_wrapper",
            "yen": "cuda_yen_wrapper",
            "march1": "cuda_march1_wrapper",
            "march2": "cuda_march2_wrapper",
            "marchsa": "cuda_marchsa_wrapper"
        }

        cpu2cpunames = {
            "avesa": "cpu_avesa",
            "ave": "cpu_ave",
            "bc": "cpu_bc",
            "init": "cpu_init",
            "geo": "cpu_geo"
            }
        text = sys.stdin.read()

        for key, value in cpu2gpunames.items():
            text = text.replace( key + r"(",  value + r"(")
        for key, value in cpu2cpunames.items():
            text = text.replace( key + r"(",  value + r"(")

        sys.stdout.write(text)


if __name__ == '__main__':
    cudafy = Cudafy()
    fire.Fire(cudafy)
