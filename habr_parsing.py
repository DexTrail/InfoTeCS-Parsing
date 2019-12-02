#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


Version: 0.1
Created: 00/12/2019
Last modified: 00/12/2019
"""

import time


def main():
    pass


if __name__ == '__main__':
    __time_start = time.perf_counter()
    main()
    __time_delta = time.perf_counter() - __time_start
    __TIMES = (('d', 24 * 60 * 60), ('h', 60 * 60), ('m', 60), ('s', 1))
    __times = ''
    for __i in range(len(__TIMES) - 1):
        __t, __time_delta = divmod(__time_delta, __TIMES[__i][1])
        if __t > 0:
            __times += "{} {} ".format(int(__t), __TIMES[__i][0])
    __times += "{:.3} {}".format(__time_delta, __TIMES[~0][0])
    print("\n[Finished in {}]".format(__times))
