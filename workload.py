import logging
import math

from Task import Task
from Taskset import Taskset
from utilization import basic_utilization_test


def _get_scheduling_points(hp_taskset, check_task):
    """Get scheduling points of a task-set.

    This method generates a list of scheduling points for a given task-set.
    The set of scheduling points S_i for a task-set with tau_i and all higher priority tasks is
    defined as: S_i = { k * T_j | j = 1, ..., i; k = 1, ..., lfloor(T_i / T_j)rfloor }.
    The set includes the deadline of tau_i and all the arrival times of tasks with higher priority
    than tau_i before the deadline of tau_i.

    Args:
        hp_taskset -- task-set with all higher priority tasks
        check_task -- the task that is checked
    Return:
        list with scheduling points
        -1 -- an error occurred
    """
    # Check input arguments
    if not isinstance(hp_taskset, Taskset):  # invalid input argument for hp_taskset
        logging.error(
            "workload.py/_get_scheduling_points(): invalid input argument for hp_taskset (must be Taskset)!")
        return -1
    if not isinstance(check_task, Task):  # invalid input argument for check_task
        logging.error(
            "workload.py/_get_scheduling_points(): invalid input argument for check_task (must be Task)!")
        return -1

    # Create empty list of scheduling points
    scheduling_points = []

    # Iterate over all tasks in the hp-task-set
    for task in hp_taskset:
        k_max = math.floor(check_task.period / task.period)

        # Iterate over all k = 1, ..., k_max
        k = 1
        while k <= k_max:
            new_scheduling_point = k * task.period
            if new_scheduling_point not in scheduling_points:
                scheduling_points.append(new_scheduling_point)
            k += 1

    # Add deadline of check_task to scheduling points
    if check_task.deadline not in scheduling_points:
        scheduling_points.append(check_task.deadline)

    # Sort scheduling points according to increasing values
    scheduling_points.sort()

    return scheduling_points


def _W_i(t, taskset):
    """ Calculate workload.

    This method calculates the workload of a task tau_i for a scheduling point t.
    W_i(t) = sum_from(j=1)_to(i) { lceil(t / T_j)rceil * C_j }

    Args:
        t -- scheduling point
        taskset -- task-set with all tasks that should be considered for calculation (tau_i and all
                   tasks with higher priority)
    Return:
        the workload of the given task-set
        -1 -- an error occurred
    """
    # Check input arguments
    if not isinstance(t, int):  # invalid input argument for t
        logging.error("workload.py/W_i(): invalid input argument for t (must be int)!")
        return -1
    if not isinstance(taskset, Taskset):  # invalid input argument for taskset
        logging.error("workload.py/W_i(): invalid input argument for taskset (must be Taskset)!")
        return -1

    # Calculate workload
    w_i = 0
    for task in taskset:
        w_i += math.ceil(t / task.period) * task.execution_time

    return w_i


def _L_i_bool(scheduling_points, taskset):
    """Calculate L_i.

    This method calculates L_i according to the following formula:
    L_i = min_(t element S_i) { W_i(t) / t }
    The method stops if for any t the condition L_i <= 1 is fulfilled.

    Args:
        scheduling_points -- time points for which the schedulability should be tested
        taskset -- task-set with all relevant tasks (tau_i and all tasks with higher priority)
    Return:
        True/False -- result of condition L_i <= 1
        -1 -- an error occurred
    """
    # Check input arguments
    if not isinstance(scheduling_points, list):  # invalid input argument for scheduling_points
        logging.error(
            "workload.py/_L_i_bool(): invalid input argument for scheduling_points (must be list)!")
        return -1
    if not isinstance(taskset, Taskset):  # invalid input argument for taskset
        logging.error(
            "workload.py/_L_i_bool(): invalid input argument for taskset (must be Taskset)!")
        return -1

    # Iterate over all scheduling points
    for t in scheduling_points:

        # Calculate W_i(t)
        w_i = _W_i(t, taskset)

        # Check if W_i(t) / t <= 1
        if (w_i / t) <= 1:  # for a value of t the condition W_i(t) / t <= 1 is fulfilled
            return True

    # No value of t found for which W_i(t) / t <= 1
    return False


def workload_test_LSD(taskset):
    """Workload test.

    This method implements the workload test according to Lehoczky, Sha, Ding 1989.
    A task-set is schedulable if for every task tau_i: L_i <= 1.
    Lehoczky, Sha, Ding 1989: The Rate Monotonic Scheduling Algorithm: Exact Characterization And
                              Average Case Behavior

    Args:
        taskset -- the task-set that should be tested for schedulability
    Return:
        True/False -- schedulability of the task-set
        -1 -- an error occurred
    """
    # Check input argument
    if not isinstance(taskset, Taskset):  # invalid input argument
        logging.error(
            "workload.py/workload_test_LSD(): invalid input argument for taskset (must be Taskset)!")
        return -1

    # Perform basic utilization test
    if basic_utilization_test(taskset) == False:
        # Utilization > 1: task-set is NOT schedulable!
        logging.debug("workload.py/workload_test_LSD(): task-set is NOT schedulable (U > 1)!")
        return False

    # Iterate over all tasks and check schedulability of each task
    for check_task in taskset:

        # Generate task-set with all higher priority tasks and check_task
        hp_taskset = Taskset(tasks=[])
        for task in taskset:
            if task.priority <= check_task.priority:
                hp_taskset.add_task(task)

        # Get scheduling points
        scheduling_points = _get_scheduling_points(hp_taskset, check_task)

        # Check schedulability of check_task: schedulable if L_i <= 1
        l_i = _L_i_bool(scheduling_points, hp_taskset)
        if l_i == False:  # check_task is NOT schedulable --> task-set is NOT schedulable
            logging.debug(
                "workload.py/workload_test_LSD(): task-set is NOT schedulable (L_{} > 1)!".format(
                    check_task.id))
            return False

    # All tasks are schedulable --> task-set is schedulable
    logging.debug("workload.py/workload_test(): task-set is schedulable!")
    return True


def _W_m_bool(k, x, hp_taskset, tau_m):
    """Calculate W_m.

    This method calculates W_m according to the following formula:
    W_m(k, x) = min_(t <= x) { (sum_from(j=1)_to(m-1) C_j lceil(t / T_j)rceil + kC_m) / t }
    The numerator of the fraction gives the total cumulative processor demands made by all jobs of
    tau_1, ..., tau_m-1 and the first job of tau_m during [0, t].
    The method stops if for any t the condition W_m(k, x) <= 1 is fulfilled.

    Args:
        k -- number of jobs that must be considered for tau_m
        x -- interval that should be checked
        hp_taskset -- task-set with all tasks with higher priority than tau_m
    Return:
        True/False -- result of condition W_m <= 1
    """
    if not isinstance(k, int) or not isinstance(x, int):  # invalid input argument for k or x
        logging.error("workload.py/_W_m_bool(): invalid input argument for k or x (must be int)!")
        return -1
    if not isinstance(hp_taskset, Taskset):  # invalid input argument for hp_taskset
        logging.error(
            "workload.py/_W_m_bool(): invalid input argument for hp_taskset (must be Taskset)!")
        return -1
    if not isinstance(tau_m, Task):  # invalid input argument for tau_m
        logging.error("workload.py,/_W_m_bool(): invalid input argument for tau_m (must be Task)!")
        return -1

    # Generate list with all possible values of t that must be checked:
    # start with tau_m.execution_time and go to x
    t_values = [i for i in range(tau_m.execution_time, x + 1)]

    # Iterate over all values of t and check if for any value of t W_m is <= 1
    for t in t_values:
        w_m = 0
        # Iterate over all tasks with higher priority than tau_m
        for task in hp_taskset:
            w_m += task.execution_time * math.ceil(t / task.period)

        # Add execution time of tau_m and divide by t
        w_m = (w_m + k * tau_m.execution_time) / t

        # Check if w_m <= 1
        if w_m <= 1:  # for a value of t the condition W_m <= 1 is fulfilled
            return True

    # No value of t found for which W_m is <= 1
    return False


def workload_test(taskset):
    """Workload test.

    This method implements the workload test according to Lehoczky 1990, but for task with D_i <= T_i.
    So only the first job of every task must meet its deadline.
    A task-set is schedulable if for every task tau_m: W_m(1, Dm) <= 1 and W_m(1, T_m) <= 1.
    Lehoczky 1990: Fixed Priority Scheduling of Periodic Task Sets with Arbitrary Deadlines

    Args:
        taskset -- the task-set that should be tested for schedulability
    Return:
        True/False -- schedulability of the task-set
        -1 -- an error occurred
    """
    # Check input argument
    if not isinstance(taskset, Taskset):  # invalid input argument
        logging.error(
            "workload.py/workload_test(): invalid input argument for taskset (must be Taskset)!")
        return -1

    # Perform basic utilization test
    if basic_utilization_test(taskset) == False:
        # Utilization > 1: task-set is NOT schedulable!
        logging.debug("workload.py/workload_test(): Task-set is NOT schedulable (U > 1)!")
        return False

    # Iterate over all tasks and check schedulability of each task
    for check_task in taskset:

        # Generate task-set with all higher priority tasks
        hp_taskset = Taskset(tasks=[])
        for task in taskset:
            if task.priority <= check_task.priority and task is not check_task:
                hp_taskset.add_task(task)

        # Check schedulability of check_task: schedulable if
        # W_m(1, D_m) <= 1 and
        # W_m(1, T_m) <= 1
        w_m_d = _W_m_bool(1, check_task.deadline, hp_taskset, check_task)
        if w_m_d == False:  # check_task is NOT schedulable --> task-set is NOT schedulable
            logging.debug((
                "workload.py(workload_test(): Task-set is NOT schedulable (W_{} > 1)".format(
                    check_task.id)))
            return False

        w_m_t = _W_m_bool(1, check_task.period, hp_taskset, check_task)
        if w_m_t == False:  # one more job of check_task must be considered!
            logging.error(
                "workload.py/workload_test(): one more job of task {} must be considered (W_m_t > 1)!".format(
                    check_task.id))
            return False

    # All tasks are schedulable --> task-set is schedulable
    logging.debug("workload.py/workload_test(): task-set is schedulable!")
    return True


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
