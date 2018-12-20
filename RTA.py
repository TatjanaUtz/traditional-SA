"""RTA Modul
Response Time Analysis Methods.
"""
import logging
import math
import time

import new_database as db
from Task import Task
from Taskset import Taskset


def RTA(taskset):
    """Response Time Analysis.

    Check the schedulability of a task-set with response time analysis.
    Calculate the response times of all tasks. The task-set is schedulable if and only if for all
    tasks: R_i <= D_i

    Keyword arguments:
        taskset -- the taskset
    Return value:
        True/False -- schedulability of task-set
        -1 -- an error occurred
    """
    # Check input argument: must be a TaskSet
    if not isinstance(taskset, Taskset):  # Invalid input argument
        logging.error("RTA/RTA(): invalid input argument, must be a TaskSet!")
        return -1

    # Check schedulability of all tasks in the task-set
    for i in range(len(taskset)):  # Iterate over all tasks
        # Get response time of task
        response_time = _caluclate_response_time(taskset, taskset[i])
        logging.debug("WCRT of Task " + str(i) + " = " + str(response_time))

        # Check schedulability of task
        if response_time == -1:  # an error occurred
            logging.error("RTA/RTA(): error value returned from _calculate_response_time()")
            return -1
        elif response_time is False or response_time > taskset[i].deadline:
            # Task-set is NOT schedulable
            logging.debug("Task-set is NOT schedulable!")
            return False

    # All tasks are schedulable -> task-set is schedulable
    logging.debug("Task-set is schedulable!")
    return True


def _caluclate_response_time(taskset, check_task):
    """Calculate the response time of a task.

    The response time of a task i is calculated through the iterative formula:
    start:  R_0 = C_i
    iteration:  R_(k+1) = C_i + sum( R_k / T_j * C_j)
    stop:   R_(k+1) = R_k = R
    The sums over j are always over all tasks with higher or same priority than i (= hp(i)).

    Keyword arguments:
        taskset -- the task-set that should be checked
        check_task -- the task for which the response time should be calculated
    Return value:
        response time of check_task
        False -- value of response time exceeds deadline of task (= period) -> task-set is not schedulable
        -1 -- an error occurred
    """

    # check input arguments
    if not isinstance(taskset, Taskset) or not isinstance(check_task,
                                                          Task):  # invalid input argument
        logging.error("RTA/_calculate_response_time(): invalid input arguments!")
        return -1

    # Create task-set with all task of higher or same priority as check_task = hp(i)
    hp = Taskset(tasks=[])
    for task in taskset:  # Iterate over all tasks
        if task.priority <= check_task.priority and task is not check_task:
            hp.add_task(task)  # Add task to hp-set

    r0 = check_task.execution_time  # Start with execution time of task i

    # Check if there are tasks of higher or same priority
    if len(hp) == 0:  # check_task is task with highest priority
        return r0  # Return response time = execution time of check_task

    r_old = 0
    r_new = r0

    while r_old != r_new:
        r_old = r_new

        sum_hp = 0
        for task in hp:  # Iterate over all higher priority tasks
            sum_hp += math.ceil(r_old / task.period) * task.execution_time

        r_new = check_task.execution_time + sum_hp

        if r_new > check_task.period:  # Deadline miss of check_task
            return False

    return r_new


def test_dataset(taskset_list):
    """Test a hole dataset.

    dataset -- the dataset that should be tested.
    """
    # taskset_list = db.get_dataset(dataset)

    # Get number of task-sets in the dataset
    number_of_tasksets = len(taskset_list)

    # Variable for checking result of test
    tp, fp, tn, fn = 0, 0, 0, 0

    for i in range(number_of_tasksets):  # Iterate over all task-sets
        taskset = taskset_list[i]
        schedulability = RTA(taskset)
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
    s = "-------------------- RESULTS OF RTA --------------------"
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

    start_time = time.time()
    test_dataset(dataset)
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)
