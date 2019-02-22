"""Response Time Analysis.

Response Time Analysis Methods:
    rta_audsley: RTA according to Audsley.
    rta_buttazzo: RTA according to Buttazzo.
The methods only differ in their starting value for response time calculation.
"""
import logging
import math

from Task import Task
from Taskset import Taskset


def rta_audsley(taskset):
    """Response Time Analysis according to Audsley.

    Check the schedulability of a task-set with response time analysis.
    Calculate the response times of all tasks. The task-set is schedulable if and only if for all
    tasks: R_i <= D_i

    Keyword arguments:
        taskset -- the task-set that should be tested
    Return value:
        True/False -- schedulability of task-set
        -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.RTA.rta_audsley')

    # Check input argument: must be a TaskSet
    if not isinstance(taskset, Taskset):  # Invalid input argument
        logger.error("Invalid input argument, must be a TaskSet!")
        return -1

    # Check schedulability of all tasks in the task-set
    for check_task in taskset:  # Iterate over all tasks
        # Get response time of task
        response_time = _caluclate_response_time_audsley(taskset, check_task)

        # Check schedulability of task
        if response_time == -1:  # an error occurred
            logger.error("Error value returned from _calculate_response_time_audsley()")
            return -1

        if response_time is False or response_time > check_task.deadline:
            # Task-set is NOT schedulable
            return False

    # All tasks are schedulable -> task-set is schedulable
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
        False -- value of response time exceeds deadline of task (= period)
                 -> task-set is not schedulable
        -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.RTA._calculate_response_time_audsley')

    # check input arguments
    if not isinstance(taskset, Taskset) or not isinstance(check_task,
                                                          Task):  # invalid input argument
        logger.error("Invalid input arguments!")
        return -1

    logger.debug("TASK %s", str(check_task.task_id))

    # Create task-set with all task of higher or same priority as check_task = hp(i)
    high_prio_set = Taskset(tasks=[])
    for task in taskset:  # Iterate over all tasks
        if task.priority <= check_task.priority and task is not check_task:
            high_prio_set.add_task(task)  # Add task to hp-set
    logger.debug("hp-set = %s", str(high_prio_set))

    resp_time_0 = check_task.execution_time  # Start with execution time of task i
    logger.debug("R0 = %s", str(resp_time_0))

    # Check if there are tasks of higher or same priority
    if not high_prio_set:  # check_task is task with highest priority
        return resp_time_0  # Return response time = execution time of check_task

    r_old = 0
    r_new = resp_time_0

    while r_old != r_new:
        r_old = r_new

        sum_hp = 0
        for task in high_prio_set:  # Iterate over all higher priority tasks
            sum_hp += math.ceil(r_old / task.period) * task.execution_time

        r_new = check_task.execution_time + sum_hp
        logger.debug("R = %s", str(r_new))

        if r_new > check_task.deadline:  # Deadline miss of check_task
            logger.debug("R > D")
            return False

    return r_new


def rta_buttazzo(taskset):
    """Response Time Analysis according to Buttazzo.

    Check the schedulability of a task-set with response time analysis.
    Calculate the response times of all tasks. The task-set is schedulable if and only if for all
    tasks: R_i <= D_i

    Keyword arguments:
        taskset -- the task-set that should be tested
    Return value:
        True/False -- schedulability of task-set
        -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.RTA_rta_buttazzo')

    # Check input argument: must be a TaskSet
    if not isinstance(taskset, Taskset):  # Invalid input argument
        logger.error("Invalid input argument, must be a TaskSet!")
        return -1

    # Check schedulability of all tasks in the task-set
    for check_task in taskset:  # Iterate over all tasks
        # Get response time of task
        response_time = _caluclate_response_time_buttazzo(taskset, check_task)

        # Check schedulability of task
        if response_time == -1:  # an error occurred
            logger.error("Error value returned from _calculate_response_time_buttazzo()")
            return -1

        if response_time is False or response_time > check_task.deadline:
            # Task-set is NOT schedulable
            return False

    # All tasks are schedulable -> task-set is schedulable
    return True


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
        False -- value of response time exceeds deadline of task (= period)
                  -> task-set is not schedulable
        -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.RTA._calculate_response_time_buttazzo')

    # check input arguments
    if not isinstance(taskset, Taskset) or not isinstance(check_task,
                                                          Task):  # invalid input argument
        logger.error("Invalid input arguments!")
        return -1

    logger.debug("TASK %s", str(check_task.task_id))

    # Create task-set with all task of higher or same priority as check_task = hp(i)
    # Add the execution times of all higher or same priority tasks to R0
    high_prio_set = Taskset(tasks=[])
    resp_time_0 = 0
    for task in taskset:  # Iterate over all tasks
        if task.priority <= check_task.priority and task is not check_task:
            high_prio_set.add_task(task)  # Add task to hp-set
            resp_time_0 += task.execution_time
    logger.debug("hp-set = %s", str(high_prio_set))

    resp_time_0 += check_task.execution_time  # Add execution time of task i
    logger.debug("R0 = %s", str(resp_time_0))

    # Check if there are tasks of higher or same priority
    if not high_prio_set:  # check_task is task with highest priority
        return resp_time_0  # Return response time = execution time of check_task

    # Check if deadline is already exceeded
    if resp_time_0 > check_task.deadline:  # Deadline miss of check_task
        logger.debug("R > D")
        return False

    r_old = 0
    r_new = resp_time_0

    while r_old != r_new:
        r_old = r_new

        sum_hp = 0
        for task in high_prio_set:  # Iterate over all higher priority tasks
            sum_hp += math.ceil(r_old / task.period) * task.execution_time

        r_new = check_task.execution_time + sum_hp
        logger.debug("R = %s", str(r_new))

        if r_new > check_task.deadline:  # Deadline miss of check_task
            logger.debug("R > D")
            return False

    return r_new


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)
