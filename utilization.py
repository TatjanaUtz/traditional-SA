"""Utilization-based Schedulability Tests."""

import logging

import Database as db
from TaskSet import TaskSet

# Global variables
_response_time_old = None
_response_time = None
_first_task = None


def basic_utilization_test(taskset):
    """Utilization-based schedulability test.

    A task-set is schedulable, if the total utilization of a processor is less than or equal to 1: U <= 1.
    The utilization of a task is the fraction of processing time and period: U_i = C_i / T_i.

    Return value:
    True/False -- schedulabilty of task-set
    -1 -- error occurred
    """
    # Check input argument
    if taskset is None or not isinstance(taskset, TaskSet):
        logging.error(
            "utilization/basic_utilization_test(): wrong input argument or no task-set given!")
        return -1

    total_utilization = 0  # Reset total utilization

    # Iterate over all tasks
    for task in taskset:
        # Calculate utilization-factor of task
        task_utilization = task.execution_time / task.period

        # Add utilization-factor of task to total utilization
        total_utilization += task_utilization

    # Check schedulability
    if total_utilization <= 1:  # Task-set is schedulable
        return True
    else:  # Task-set is NOT schedulable
        return False


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
        schedulability = basic_utilization_test(taskset)
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
        "---------- RESULTS OF basic_utilization_test FOR " + dataset + " ----------")
    print("Correct: {0:d} / {1:d} -> {2:.0f}%".format(tp + tn, number_of_tasksets,
                                                      (tp + tn) * 100 / number_of_tasksets))
    print("Incorrect: {0:d} / {1:d} -> {2:.0f}%".format(fp + fn, number_of_tasksets,
                                                        (fp + fn) * 100 / number_of_tasksets))
    print("True positive (tp) = {0:d}".format(tp))
    print("False positive (fp) = {0:d}".format(fp))
    print("True negative (tn) = {0:d}".format(tn))
    print("False negative (fn) = {0:d}".format(fn))
    print("--------------------------------------------------------------------")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # Test basic_utilization_test
    test_dataset("Dataset5")
