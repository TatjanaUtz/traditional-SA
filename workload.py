import logging
import math

from Task import Task
from Taskset import Taskset


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
    # create logger
    logger = logging.getLogger('traditional-SA.workload._get_scheduling_points')

    # Check input arguments
    if not isinstance(hp_taskset, Taskset):  # invalid input argument for hp_taskset
        logger.error("Invalid input argument for hp_taskset (must be Taskset)!")
        return -1
    if not isinstance(check_task, Task):  # invalid input argument for check_task
        logger.error("Invalid input argument for check_task (must be Task)!")
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

    # Sort scheduling points according to increasing values
    scheduling_points.sort()

    return scheduling_points


def _W_i(t, taskset):
    """ Calculate workload.

    This method calculates the workload of a task tau_i for a scheduling point t.
    W_i(t) = sum_from(j=1)_to(i) { lceil(t / T_j)rceil * C_j }

    Args:
        t -- scheduling point
        taskset -- task-set with all tasks that should be considered for calculation (= tau_i and all
                   tasks with higher priority)
    Return:
        the workload of the given task-set at scheduling point t
        -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.workload._W_i')

    # Check input arguments
    if not isinstance(t, int):  # invalid input argument for t
        logger.error("Invalid input argument for t (must be int)!")
        return -1
    if not isinstance(taskset, Taskset):  # invalid input argument for taskset
        logger.error("Invalid input argument for taskset (must be Taskset)!")
        return -1

    # Calculate workload
    w_i = 0
    for task in taskset:
        w_i += math.ceil(t / task.period) * task.execution_time

    logger.debug("W_i({}) = {}".format(t, w_i))

    return w_i


def _L_i(t, taskset):
    """Calculate L_i(t).

    This method calculates L_i(t) according to the following formula:
    L_i(t) = W_i(t) / t

    Args:
        t -- scheduling point
        taskset -- task-set with all relevant tasks (= tau_i and all tasks with higher priority)
    Return:
        L_i(t)
        -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.workload._L_i')

    # Check input arguments
    if not isinstance(t, int):  # invalid input argument for t
        logger.error("Invalid input argument for t (must be int)!")
        return -1
    if not isinstance(taskset, Taskset):  # invalid input argument for taskset
        logger.error("Invalid input argument for taskset (must be Taskset)!")
        return -1

    # Calculate L_i(t)
    l_i = _W_i(t, taskset) / t

    logger.debug("L_i({}) = {}".format(t, l_i))

    return l_i


def rm_workload_test(taskset):
    """Workload test.

    This method implements the workload test according to Lehoczky, Sha, Ding 1989 for RM scheduler and D = T.
    A task-set is schedulable if for every task tau_i: L_i <= 1.
    Lehoczky, Sha, Ding 1989: The Rate Monotonic Scheduling Algorithm: Exact Characterization And
                              Average Case Behavior

    Args:
        taskset -- the task-set that should be tested for schedulability
    Return:
        True/False -- schedulability of the task-set
        -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.workload.rm_workload_test')

    # Check input argument
    if not isinstance(taskset, Taskset):  # invalid input argument
        logger.error("Invalid input argument for taskset (must be Taskset)!")
        return -1

    # Iterate over all tasks and check schedulability of tasks
    # The task-set is schedulable if L = max(L_i) <= 1
    # This means that if all tasks are schedulable, the task-set is also schedulable and the other way round
    for check_task in taskset:
        logger.debug("TASK {}".format(check_task.id))

        # Generate task-set with all higher priority tasks and check_task
        hp_taskset = Taskset(tasks=[])
        for task in taskset:
            if task.priority <= check_task.priority:
                hp_taskset.add_task(task)
        logger.debug("hp-set = " + str(hp_taskset))

        # Get scheduling points
        scheduling_points = _get_scheduling_points(hp_taskset, check_task)
        logger.debug("Scheduling points = " + str(scheduling_points))

        # Iterate over all scheduling points and calculate L_i(t)
        # A task is schedulable if L_i = min(L_i(t)) <= 1
        # This means that if at least for one scheduling point L_i(t) <= 1 the task is schedulable
        for t in scheduling_points:
            l_i = _L_i(t, hp_taskset)
            if l_i <= 1:  # task is schedulable, stop iteration and check next task in task-set
                logger.debug("L_i({}) <= 1 -> task schedulable".format(t))
                break
        else:  # the condition was not meet for any scheduling pint: task is not schedulable -> task-set is not schedulable
            logger.debug("Task is not schedulable -> Task-set is not schedulable")
            return False
    else:  # all tasks are schedulable -> task-set is schedulable
        logger.debug("All tasks are schedulable -> Task-set is schedulable")
        return True


_last_psi = []
_last_workload = []


def _W_i_het(i, b, taskset):
    """Calculate workload.
    This method calculates the workload of a task tau_i for its deadline T_i.
    W_[i-1](T_i) = min( sum( ceil(t / T_j) * C_j ) + (T_i - t) )
    The minimum is built over all scheduling points t.
    Implementation according to [BB01].

    Args:
        i -- position of the task in the task-set
        b -- the period of the task
    Return:
        the workload of the given task-set at T_i
        -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.workload._W_i_het')

    # Check input arguments
    if not isinstance(i, int) or i > len(taskset):  # invalid input argument for i
        logger.error("Invalid input argument for i (must be int and in taskset)!")
        return -1
    if not isinstance(b, int):  # invalid input argument for D_i
        logger.error("Invalid input argument for b (must be int)!")
        return -1
    if not isinstance(taskset, Taskset):  # invalid input argument for taskset
        logger.error("Invalid input argument for taskset (must be Taskset)!")
        return -1

    if i <= 0:  # W_0(T_1) = 0
        return 0

    global _last_psi, _last_workload
    if b <= _last_psi[i]:  # if W(i, b) already computed
        logger.debug("W({}, {}) already computed".format(i, b))
        return _last_workload[i]  # don't go further

    f = math.floor(b / taskset[i - 1].period)
    c = math.ceil(b / taskset[i - 1].period)
    logger.debug("f = {} \t c = {}".format(f, c))

    branch0 = b - f * (taskset[i - 1].period - taskset[i - 1].execution_time) + _W_i_het(i - 1, f *
                                                                                         taskset[
                                                                                             i - 1].period,
                                                                                         taskset)
    branch1 = c * taskset[i - 1].execution_time + _W_i_het(i - 1, b, taskset)
    logger.debug("branch0 = {} \t branch1 = {}".format(branch0, branch1))

    _last_psi[i] = b
    _last_workload[i] = min(branch0, branch1)

    return _last_workload[i]


def het_workload_test(taskset):
    """Hyperplanes Exact Test (HET).

    A task-set is schedulable if for all tasks C_i + W_[i-1](T_i) <= T_i is fullfilled.
    Implementation according to [BB01].

    Args:
    taskset -- the task-set that should be tested for schedulability
    Return:
    True/False -- schedulability of the task-set
    -1 -- an error occurred
    """
    # create logger
    logger = logging.getLogger('traditional-SA.workload.het_workload_test')

    # Check input argument
    if not isinstance(taskset, Taskset):  # invalid input argument
        logger.error("Invalid input argument for taskset (must be Taskset)!")
        return -1

    # clear list with already computed workload values
    global _last_psi, _last_workload
    _last_psi = [0 for x in range(len(taskset))]
    _last_workload = [0 for x in range(len(taskset))]

    # iterate over all tasks in the task-set
    for i in range(1, len(taskset) + 1):
        logger.debug("TASK {}".format(taskset[i - 1].id))

        # calculate W_[i-1](T_i)
        w = _W_i_het(i - 1, taskset[i - 1].period, taskset)
        logger.debug("W_{}({}) = {}".format(i - 1, taskset[i - 1].period, w))

        # add computation time of check_task
        sum = taskset[i - 1].execution_time + w
        logger.debug("Summe = {}".format(sum))

        # check schedulability condition: C_i + W_[i-1](T_i) <= T_i
        if sum > taskset[i - 1].deadline:  # task is NOT schedulable
            logger.debug("Task is not schedulable -> Task-set is not schedulable")
            return False
        else:  # task is schedulable
            logger.debug("Task is schedulable")

    else:  # all tasks are schedulable -> task-set is schedulable
        logger.debug("All tasks are schedulable -> Task-set is schedulable")
        return True


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
