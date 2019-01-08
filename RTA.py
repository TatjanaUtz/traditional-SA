"""RTA Modul
Response Time Analysis Methods.
"""
import logging
import math
import time

from pycpa import analysis
from pycpa import model
from pycpa import schedulers

import new_database as db
from Task import Task
from Taskset import Taskset
from utilization import basic_utilization_test

# Global variables
RTA_tests = ["Audsley", "Buttazzo", "CPA"]


def RTA(taskset, test_name):
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
    global RTA_tests
    if test_name not in RTA_tests:
        # Invalid test name
        logging.error("RTA/RTA(): Invalid test name!")
        return

    # Check input argument: must be a TaskSet
    if not isinstance(taskset, Taskset):  # Invalid input argument
        logging.error("RTA/RTA(): invalid input argument, must be a TaskSet!")
        return -1

    # Check schedulability of all tasks in the task-set
    for i in range(len(taskset)):  # Iterate over all tasks
        # Get response time of task
        if test_name == "Audsley":
            response_time = _caluclate_response_time_audsley(taskset, taskset[i])
        elif test_name == "Buttazzo":
            response_time = _caluclate_response_time_buttazzo(taskset, taskset[i])
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


def _caluclate_response_time_audsley(taskset, check_task):
    """Calculate the response time of a task.

    The response time of a task i is calculated according to Audsley through the iterative formula:
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


def _caluclate_response_time_buttazzo(taskset, check_task):
    """Calculate the response time of a task.

    The response time of a task i is calculated according to Buttazzo through the iterative formula:
    start:  R_0 = sum(C_j)
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
    # Add the execution times of all higher or same priority tasks to R0
    hp = Taskset(tasks=[])
    r0 = 0
    for task in taskset:  # Iterate over all tasks
        if task.priority <= check_task.priority and task is not check_task:
            hp.add_task(task)  # Add task to hp-set
            r0 += task.execution_time

    r0 += check_task.execution_time  # Add execution time of task i

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


def CPA(taskset):
    # generate a new system
    s = model.System()

    # add resources (CPUs) to the system
    # and register the static priority preemptive scheduler
    r1 = s.bind_resource(model.Resource("R1", schedulers.SPPSchedulerRoundRobin()))

    # create and bind tasks to r1
    # register a periodic event model for all tasks
    tasks = []
    for i in range(len(taskset)):
        tasks.append(r1.bind_task(model.Task(str(taskset[i].id), wcet=taskset[i].execution_time,
                                             scheduling_parameter=taskset[i].priority)))
        tasks[i].in_event_model = model.PJdEventModel(P=taskset[i].period)

    # perform the analysis
    task_results = analysis.analyze_system(s)

    # print the worst case response times (WCRTs)
    # check schedulability WCRT <= D
    for r in s.resources:
        i = 0
        for t in r.tasks:
            wcrt = task_results[t].wcrt
            deadline = taskset[i].deadline
            if wcrt > deadline:
                return False
            i += 1

    return True


def test_dataset(taskset_list, test_name):
    """Test a hole dataset.

    Keyword arguments:
        dataset -- the dataset that should be tested.
        test_name -- test that should be used.
    """

    global RTA_tests
    if test_name not in RTA_tests:
        # Invalid test name
        logging.error("RTA/test_dataset(): Invalid test name!")
        return

    # Get number of task-sets in the dataset
    number_of_tasksets = len(taskset_list)

    # Variable for checking result of test
    tp, fp, tn, fn = 0, 0, 0, 0

    for i in range(number_of_tasksets):  # Iterate over all task-sets
        taskset = taskset_list[i]
        if test_name == "Audsley" or test_name == "Buttazzo":  # RTA according to Audsley or Buttazzo
            schedulability = RTA(taskset, test_name)
        elif test_name == "CPA":  # RTA with pyCPA
            if basic_utilization_test(taskset) is True:
                schedulability = CPA(taskset)
            else:
                schedulability = False
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
    s = "-------------------- RESULTS OF RTA ACCORDING TO " + test_name.upper() + " --------------------"
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
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

    print("Reading task-sets from the database...")
    start_time = time.time()
    dataset = db.get_dataset()
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    start_time = time.time()
    test_dataset(dataset, "CPA")
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)
