"""Utilization-based Schedulability Tests."""

import logging
import time

import new_database as db
from Taskset import Taskset

# Global variables
utilization_tests = ["basic_utilization_test", "RM_utilization_test", "HB_utilization_test"]


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
            "utilization/basic_utilization_test(): wrong input argument or no task-set given!")
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

    # Check schedulability
    if total_utilization <= 1:  # Task-set is schedulable
        return True
    else:  # Task-set is NOT schedulable
        return False


def RM_utilization_test(taskset):
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
            "utilization/RM_utilization_test(): wrong input argument or no task-set given!")
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

    # Check schedulability
    if total_utilization <= utilization_bound:  # Task-set is schedulable
        return True
    else:  # Task-set is NOT schedulable
        return False


def HB_utilization_test(taskset):
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
            "utilization/basic_utilization_test(): wrong input argument or no task-set given!")
        return -1

    total_utilization = 0  # Reset total utilization

    # Iterate over all tasks
    for task in taskset:
        # Calculate utilization-factor of task
        task_utilization = task.execution_time / task.period

        # Add utilization-factor of task to total utilization
        total_utilization *= task_utilization + 1

    # Check schedulability
    if total_utilization <= 2:  # Task-set is schedulable
        return True
    else:  # Task-set is NOT schedulable
        return False


def test_dataset(taskset_list, test_name):
    """Test a hole dataset.

    Keyword arguments:
        dataset -- the dataset that should be tested
        test_name -- the test that should be performed
    """
    global utilization_tests
    if test_name not in utilization_tests:
        # Invalid test name
        logging.error("utilization/test_dataset(): Invalid test name!")
        return

    # Get number of task-sets in the dataset
    number_of_tasksets = len(taskset_list)

    # Variable for checking result of test
    tp, fp, tn, fn = 0, 0, 0, 0

    for i in range(number_of_tasksets):  # Iterate over all task-sets
        taskset = taskset_list[i]
        if test_name == "basic_utilization_test":
            schedulability = basic_utilization_test(taskset)
        elif test_name == "RM_utilization_test":
            schedulability = RM_utilization_test(taskset)
        elif test_name == "HB_utilization_test":
            schedulability = HB_utilization_test(taskset)

        exit_value = taskset.result

        # Analyse test
        if schedulability is True and exit_value == 1:  # True positives
            tp += 1
        elif schedulability is True and exit_value == 0:  # False positives
            fp += 1
        elif schedulability is False and exit_value == 1:  # False negatives
            fn += 1
        elif schedulability is False and exit_value == 0:  # True negatives
            tn += 1

    # Print results
    s = "---------- RESULTS OF " + test_name + " ----------"
    print(s)
    print("Correct: {0:d} / {1:d} -> {2:.0f}%".format(tp + tn, number_of_tasksets,
                                                      (tp + tn) * 100 / number_of_tasksets))
    print("Incorrect: {0:d} / {1:d} -> {2:.0f}%".format(fp + fn, number_of_tasksets,
                                                        (fp + fn) * 100 / number_of_tasksets))
    print("True positive (tp) = {0:d}".format(tp))
    print("False positive (fp) = {0:d}".format(fp))
    print("True negative (tn) = {0:d}".format(tn))
    print("False negative (fn) = {0:d}".format(fn))
    print("-" * len(s))


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    start_time = time.time()
    dataset = db.get_dataset()
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)
    test_dataset(dataset, "basic_utilization_test")
    test_dataset(dataset, "RM_utilization_test")
    test_dataset(dataset, "HB_utilization_test")
