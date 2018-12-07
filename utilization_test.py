"""Utilization-based Schedulability Test for fixed priority scheduler.

A general taskset is schedulable, if and only if the total utilization is less than or equal 1:
U = sum(C_i / T_i) <= 1 (neccessary condition)
"""

import logging


def utilization_test(taskset):
    """Utilization-based schedulabilty test.

    Keyword arguments:
    taskset -- Taskset which should be tested, represented as a list of tuples:
                [(C0, T0), (C1, T2), ..., (Cn, Tn)]
                C0 = execution time of the first task
                T0 = period of the first task
    Return value:
    True/False -- schedulability result, True if taskset is schedulable, otherwise False
    """
    logging.debug("utilization_test(): utilization-test will be performed")
    utilization = 0
    for i in range(len(taskset)):
        utilization += taskset[i][0] / taskset[i][1]
    if utilization <= 1:
        logging.debug("utilization_test(): taskset is schedulable!")
        return True
    else:
        logging.debug("utilization_test(): taskset is NOT scheudlable!")
        return False


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    example_taskset = [(5000, 10000), (3000, 10000), (2000, 10000)]
    result = utilization_test(example_taskset)
    print(result)
