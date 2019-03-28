"""Utilization-based Schedulability Tests."""

import logging

from database_interface import Taskset


def basic_utilization_test(taskset):
    """Utilization-based schedulability test.

    A task-set is schedulable, if the total utilization of a processor is less than or equal to 1:
    U <= 1. The utilization of a task is the fraction of processing time and deadline or period:
    U_i = C_i / min(D_i, T_i).

    Return value:
    True/False -- schedulabilty of task-set
    -1 -- error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.utilization.basic_utilization_test')

    # Check input argument
    if taskset is None or not isinstance(taskset, Taskset):
        logger.error("Invalid taskset!")
        return -1

    total_utilization = 0  # Reset total utilization

    # Iterate over all tasks
    for task in taskset:
        # Calculate utilization-factor of task
        task_utilization = task.execution_time / min(task.deadline, task.period)

        # Add utilization-factor of task to total utilization
        total_utilization += task_utilization

    logger.debug("Total Utilization = %f", total_utilization)

    # Check schedulability
    return bool(total_utilization <= 1)


def rm_utilization_test(taskset):
    """Utilization-based schedulability test.

    This test was introduced by Liu and Layland in 1973 for the rate monothonic (RM) algorithm.
    A task-set is schedulable, if the total utilization of a processor is less than or equal to
    n(2^(1/n) - 1): U <= n(2^(1/n) - 1).
    The utilization of a task is the fraction of processing time and period: U_i = C_i / T_i.
    The test can also be used to test other fix priority algorithms, as the RM algorithm is optimal.
    Optimal means, that if the RM algorithm cannot create a feasible schedule, no other
    priority-based algorithm can do this.

    Return value:
    True/False -- schedulabilty of task-set
    -1 -- error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.utilization.rm_utilization_test')

    # Check input argument
    if taskset is None or not isinstance(taskset, Taskset):
        logger.error("Invalid task-set!")
        return -1

    total_utilization = 0  # Reset total utilization

    # Iterate over all tasks
    for task in taskset:
        # Calculate utilization-factor of task
        task_utilization = task.execution_time / task.period

        # Add utilization-factor of task to total utilization
        total_utilization += task_utilization

    # Calculate utilization bound for RM
    utilization_bound = len(taskset) * (2 ** (1 / len(taskset)) - 1)
    logger.debug("Utilization bound = %f", utilization_bound)
    logger.debug("Total Utilization = %f", total_utilization)

    # Check schedulability
    return bool(total_utilization <= utilization_bound)


def hb_utilization_test(taskset):
    """Utilization-based schedulability test.

    The test was introduced by Bini und Buttazzo 2001 and 2003. It is based on the RM-test of Liu
    and Layland 1973, but with another utilization bound. According to the so called hyperbolic
    bound (HB), a task-set is schedulable, if: prod(U_i + 1) <= 2. The utilization of a task is the
    fraction of processing time and period: U_i = C_i / T_i.

    Return value:
    True/False -- schedulabilty of task-set
    -1 -- error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.utilization_hb_utilization_test')

    # Check input argument
    if taskset is None or not isinstance(taskset, Taskset):
        logger.error("Invalid task-set!")
        return -1

    total_utilization = 1  # Reset total utilization

    # Iterate over all tasks
    for task in taskset:
        # Calculate utilization-factor of task
        task_utilization = (task.execution_time / task.period) + 1

        # Add utilization-factor of task to total utilization
        total_utilization *= task_utilization

    logger.debug("Total Utilization = %f", total_utilization)

    # Check schedulability
    return bool(total_utilization <= 2)
