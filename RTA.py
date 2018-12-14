"""RTA Modul
Response Time Analysis Methods.
"""
import logging
import math

import Database as db
from TaskSet import TaskSet


def RTA(taskset):
    """Response Time Analysis.

    Check the schedulability of a task-set with response time analysis.
    Calculate the response times of all tasks. The task-set is schedulable if and only if for all
    tasks: D_i = T_i <= R_i

    Keyword arguments:
        taskset -- the taskset
    Return value:
        True/False -- schedulability of task-set
        -1 -- an error occurred
    """
    # Check input argument: must be a TaskSet
    if not isinstance(taskset, TaskSet):  # Invalid input argument
        logging.error("RTA/RTA(): invalid input argument, must be a TaskSet!")
        return -1

    # Sort the task-set according to priorities: first task has highest priority
    taskset.sort()
    logging.debug("Task-set = " + str(taskset))

    # Check schedulability of all tasks in the task-set
    for i in range(len(taskset)):  # Iterate over all tasks
        # Get response time of task
        response_time = _caluclate_response_time(taskset, taskset[i])

        # Check schedulability of task
        if response_time is False or response_time > taskset[i].period:
            # Task-set is NOT schedulable
            logging.debug("Task-set is NOT schedulable!")
            return False

    # All tasks are schedulable -> task-set is schedulable
    logging.debug("Task-set is schedulable!")
    return True


def _caluclate_response_time(taskset, check_task):
    """Calculate the response time of a task.

    The response time of a task i is calculated through the iterative formula:
    start:  R0 = C_i
    iteration:  R_(n+1) = C_i + sum( R_n / T_k * C_k)
    stop:   R_(n+1) = R_n = R_i
    The sums over k are always over all tasks with higher or same priority than i = hp(i).

    Keyword arguments:
        taskset -- the task-set
        check_task -- the task for which the response time should be calculated
    Return value:
        response time
        False -- value of response time exceeds deadline of task (= period) -> task-set is not schedulable
    """
    # Create task-set with all task of higher or same priority as check_task = hp(i)
    hp = TaskSet()
    for task in taskset:  # Iterate over all tasks
        if task.priority <= check_task.priority and task is not check_task:
            hp.addTask(task)  # Add task to hp-set
    logging.debug("hp(i) = " + str(hp))

    r0 = check_task.execution_time  # Start with execution time of task i

    # Check if there are tasks of higher or same priority
    if len(hp) == 0:  # check_task is task with highest priority
        return r0  # Return response time = execution time of check_task

    r_old = 0
    r_new = r0

    while r_old != r_new:
        r_old = r_new
        logging.debug("R_n = " + str(r_old))

        sum_hp = 0
        for task in hp:  # Iterate over all higher priority tasks
            sum_hp += math.ceil(r_old / task.period) * task.execution_time
        logging.debug("sum_hp = " + str(sum_hp))

        r_new = check_task.execution_time + sum_hp
        logging.debug("R_(n+1) = " + str(r_new))

        if r_new > check_task.period:  # Deadline miss of check_task
            return False

    return r_new


def test_dataset(dataset):
    """Test a hole dataset.

    dataset -- the dataset that should be tested.
    """
    taskset_list = db.get_dataset(dataset)

    # Get number of task-sets in the dataset
    number_of_tasksets = len(taskset_list)

    # Variable for checking result of test
    tp, fp, tn, fn = 0, 0, 0, 0

    for i in range(number_of_tasksets):  # Iterate over all task-sets
        taskset = taskset_list[i]
        schedulability = RTA(taskset)
        exit_value = taskset.exit_value

        # Analyse test
        if schedulability is True and exit_value == 1:  # True positives
            tp += 1
        elif schedulability is True and exit_value == -1:  # False positives
            fp += 1
        elif schedulability is False and exit_value == 1:  # False negatives
            fn += 1
        elif schedulability is False and exit_value == -1:  # True negatives
            tn += 1

    # Print results
    print(
        "---------- RESULTS OF RTA FOR " + dataset + " ----------")
    print("Correct: {0:d} / {1:d} -> {2:.0f}%".format(tp + tn, number_of_tasksets,
                                                      (tp + tn) * 100 / number_of_tasksets))
    print("Incorrect: {0:d} / {1:d} -> {2:.0f}%".format(fp + fn, number_of_tasksets,
                                                        (fp + fn) * 100 / number_of_tasksets))
    print("True positive (tp) = {0:d}".format(tp))
    print("False positive (fp) = {0:d}".format(fp))
    print("True negative (tn) = {0:d}".format(tn))
    print("False negative (fn) = {0:d}".format(fn))
    print("-------------------------------------------------")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # Test RTA
    test_dataset("Dataset5")
