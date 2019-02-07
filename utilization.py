"""Utilization-based Schedulability Tests."""

import logging

from Taskset import Taskset


def basic_utilization_test(taskset):
    """Utilization-based schedulability test.

    A task-set is schedulable, if the total utilization of a processor is less than or equal to 1: U <= 1.
    The utilization of a task is the fraction of processing time and deadline or period:
    U_i = C_i / min(D_i, T_i).

    Return value:
    True/False -- schedulabilty of task-set
    -1 -- error occurred
    """
    # Check input argument
    if taskset is None or not isinstance(taskset, Taskset):
        logging.error(
            "utilization.py/basic_utilization_test(): invalid taskset!")
        return -1

    total_utilization = 0  # Reset total utilization

    # Iterate over all tasks
    for task in taskset:
        if task.deadline < task.period:  # deadline is smaller than period
            # Calculate utilization-factor of task with deadline
            task_utilization = task.execution_time / task.deadline
        elif task.period < task.deadline:  # period is smaller than deadline
            # Calculate utilization-factor of task with period
            task_utilization = task.execution_time / task.period
        else:  # deadline and period are equal
            # Calculate utilization-factor of task
            task_utilization = task.execution_time / task.period

        # Add utilization-factor of task to total utilization
        total_utilization += task_utilization

    logging.debug("utilization.py/basic_utilization_test(): total Utilization = " + str(total_utilization))

    # Check schedulability
    if total_utilization <= 1:  # Task-set is schedulable
        return True
    else:  # Task-set is NOT schedulable
        return False


def rm_utilization_test(taskset):
    """Utilization-based schedulability test.

    This test was introduced by Liu and Layland in 1973 for the rate monothonic (RM) algorithm.
    A task-set is schedulable, if the total utilization of a processor is less than or equal to
    n(2^(1/n) - 1): U <= n(2^(1/n) - 1).
    The utilization of a task is the fraction of processing time and period: U_i = C_i / T_i.
    The test can also be used to test other fix priority algorithms, as the RM algorithm is optimal.
    Optimal means, that if the RM algorithm cannot create a feasible schedule, no other priority-based
    algorithm can do this.

    Return value:
    True/False -- schedulabilty of task-set
    -1 -- error occurred
    """
    # Check input argument
    if taskset is None or not isinstance(taskset, Taskset):
        logging.error(
            "utilization.py/rm_utilization_test(): invalid task-set!")
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
    logging.debug("utilization.py/rm_utilization_test(): Utilization bound = " + str(utilization_bound))
    logging.debug("utilization.py/rm_utilization_test(): total Utilization = " + str(total_utilization))

    # Check schedulability
    if total_utilization <= utilization_bound:  # Task-set is schedulable
        return True
    else:  # Task-set is NOT schedulable
        return False


def hb_utilization_test(taskset):
    """Utilization-based schedulability test.

    The test was introduced by Bini und Buttazzo 2001 and 2003. It is based on the RM-test of Liu and
    Layland 1973, but with another utilization bound. According to the so called hyperbolic bound (HB),
    a task-set is schedulable, if: prod(U_i + 1) <= 2.
    The utilization of a task is the fraction of processing time and period: U_i = C_i / T_i.

    Return value:
    True/False -- schedulabilty of task-set
    -1 -- error occurred
    """
    # Check input argument
    if taskset is None or not isinstance(taskset, Taskset):
        logging.error(
            "utilization.py/hb_utilization_test(): invalid task-set!")
        return -1

    total_utilization = 0  # Reset total utilization

    # Iterate over all tasks
    for task in taskset:
        # Calculate utilization-factor of task
        task_utilization = task.execution_time / task.period

        # Add utilization-factor of task to total utilization
        total_utilization *= task_utilization + 1

    logging.debug("utilization.py/hb_utilization_test(): total Utilization = " + str(total_utilization))

    # Check schedulability
    if total_utilization <= 2:  # Task-set is schedulable
        return True
    else:  # Task-set is NOT schedulable
        return False


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
