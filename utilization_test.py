"""Utilization-based Schedulability Test.

A general taskset is schedulable, if and only if the total utilization is less than or equal 1:
U = sum(C_i / T_i) <= 1 (neccessary condition)
"""

import logging
import utils_database as db
from TaskSet import TaskSet
from Task import Task
import math

# Global variables
_response_time_old = None
_response_time = None
_first_task = None


def utilization_test_edf(taskset):
    """Utilization-based schedulabilty test for EDF.

    Keyword arguments:
    taskset -- Taskset which should be tested, represented as a list of tuples:
                [(C0, T0), (C1, T2), ..., (Cn, Tn)]
                C0 = execution time of the first task
                T0 = period of the first task
    Return value:
    True/False -- schedulability result, True if taskset is schedulable, otherwise False
    """
    logging.debug("utilization_test(): utilization-test will be performed")
    utilization = 0
    for i in range(len(taskset)):
        utilization += taskset[i][0] / taskset[i][1]
    if utilization <= 1:
        logging.debug("utilization_test(): taskset is schedulable!")
        return True
    else:
        logging.debug("utilization_test(): taskset is NOT scheudlable!")
        return False


def utilization_test_rm(taskset):
    """Utilization-based schedulabilty test for RM.

    A taskset is schedulable with RM if U <= n(2^(1/n) - 1)

    Keyword arguments:
    taskset -- Taskset which should be tested, represented as a list of tuples:
                [(C0, T0), (C1, T2), ..., (Cn, Tn)]
                C0 = execution time of the first task
                T0 = period of the first task
    Return value:
    True/False -- schedulability result, True if taskset is schedulable, otherwise False
    """
    logging.debug("utilization_test(): utilization-test will be performed")
    utilization = 0
    for i in range(len(taskset)):
        utilization += taskset[i][0] / taskset[i][1]
    utilization_bound = len(taskset) * (2**(1/len(taskset)) - 1)
    if utilization <= utilization_bound:
        logging.debug("utilization_test(): taskset is schedulable!")
        return True
    else:
        logging.debug("utilization_test(): taskset is NOT scheudlable!")
        return False


def _compute_response_time(new_task, num_elements, check_task, taskset):
    global _response_time_old, _response_time, _first_task
    _response_time_old = check_task.executionTime
    while True:
        _curr_task = taskset[0]
        _curr_task_idx = 0
        _response_time = check_task.executionTime
        for i in range(num_elements):
            _response_time += math.ceil(_response_time_old / _curr_task.period) * \
                              _curr_task.executionTime
            _curr_task_idx += 1
            _curr_task = taskset[_curr_task_idx]

        # If check_task is another task then new_task we have to add the new_task here
        if new_task != check_task:
            _response_time += math.ceil(_response_time_old / new_task.period) * \
                              new_task.executionTime

        print("response_time = {0:d}, response_time_old = {1:d}, deadline = {2:d}"
              .format(_response_time, _response_time_old, check_task.deadline))

        ''' Since the response_time is increasing with each iteration, it has to be always smaller
        then the deadline -> we can stop if we hit the deadline. '''
        if _response_time > check_task.deadline:
            # Task-Set is NOT schedulable
            print("Task-Set is NOT schedulable!")
            return False
        if _response_time_old >= _response_time:
            if _response_time <= check_task.deadline:
                # Task-Set is schedulable
                print("Task-Set is schedulable! Response time = {0:d}, deadline = {1:d}"
                      .format(_response_time, check_task.deadline))
        _response_time_old = _response_time


def RTA(new_task, rq_buf):
    global _response_time_old, _response_time, _first_task

    num_elements = len(rq_buf)
    print("num_elements = ", num_elements)

    ''' Assuming that each task is schedulable if it is alone, the task is accepted if the rq_buf
    is empty.'''
    if num_elements == 0:
        print("num_elements == 0, Task-Set is schedulable!")
        return True

    ''' RTA-Algorithm
    We assume that the existing Task-Set is schedulable without the new task. Therefore the
    response time has to e computed for the new task and all tasks having a smaller priority then
    the new task and for the new task. The tasks in the rq_buf are assumed to be sorted by
    priorities. '''
    _first_task = rq_buf[0]
    print("_first_task = ",  _first_task)
    _curr_task = _first_task
    print("_curr_task = ", _curr_task)
    print("new_task.priority=", new_task.priority, " ? rq_buf[-1].priority=", rq_buf[-1].priority)
    '''if new_task.priority < rq_buf[-1].priority:
        print("New task hast lower priority the all other tasks, priority_new = {0:d}, \
              priority_last = {1:d}".format(new_task.priority, rq_buf[-1].priority))
        _response_time_old = new_task.executionTime
        if not _compute_response_time(new_task, num_elements, new_task):
            # Task-Set is not schedulable
            print("Task-Set is not schedulable!")
            return False
    else:
        # Compute response time for all tasks having priority smaller then the new task.
        print("New task has higher or the same priority then lowest existing task, priority_new = \
              {01:d}, priority_last = {1:d}".format(new_task.priority, rq_buf[-1].priority))
        for i in range(num_elements):
            _response_time_old = _curr_task.executionTime
            if _curr_task.priority <= new_task.priority:
                if not _compute_response_time(new_task, i, _curr_task, rq_buf):
                    # Task-Set is not schedulable
                    return False

            # Check new_task at right position
            if _curr_task.priority > new_task.priority and (_curr_task+1).priority <= \
               new_task.priority and i > 0:
                if not _compute_response_time(new_task, i+1, new_task):
                    # Task-Set is not schedulable
                    print("Task-Set is not schedulable!")
                    return False
            _curr_task += 1
    print("All Task-Sets passed the RTA Algorithm -> Task-Set schedulable!")
    return True'''


def fp_sufficient_test(new_task, rq_buf):
    """Sufficient schedulability test for fixed priority.

    Test from argos-research/genode-AdmCtrl.
    Keyword arguments:
    taskset -- the taskset that should be tested
    Return value:
    True/False -- result of schedulability test (True if taskset is schedulable, otherwise False)
    """
    num_elements = len(rq_buf)
    if num_elements == 0:      # Task set has only one task -> taskset is schedulable
        print("Taskset has only one task --> is schedulable!")
        return True

    R_ub, sum_util, sum_util_wcet = 0.0, 0.0, 0.0
    curr_task_idx = 0
    _curr_task = rq_buf[curr_task_idx]
    print("Current Task = ", _curr_task)

    for i in range(num_elements):
        # Add new_task if priority bigger then curr_task
        if new_task.priority >= _curr_task.priority:
            R_ub = new_task.executionTime + sum_util_wcet / (1 - sum_util)
            print("R_ub: {0:d}.{1:d} at new_task position {2:d}, deadline: {3:d}".format(int(R_ub),
                  int(R_ub*100-int(R_ub)*100), i, new_task.deadline))
            if R_ub > new_task.deadline:    # Deadline hit for new task
                print("Deadline hit for task {0:d}, Taskset might be not schedulable! Maybe try an \
                      exact test.".format(i))
                return False
            sum_util += new_task.executionTime / new_task.period
            sum_util_wcet += new_task.executionTime * (1 - (new_task.executionTime /
                                                            new_task.period))
        R_ub = (_curr_task.executionTime + sum_util_wcet) / (1 - sum_util)
        print("R_ub: {0:d}.{1:d} at position {2:d}, deadline: {3:d}".format(int(R_ub), int(R_ub*100
              - int(R_ub*100)), i, _curr_task.deadline))

        if R_ub > _curr_task.deadline:      # Deadline hit for task i
            print("Deadline hit for task {0:d}, Taskset might be not schedulable! Maybe try an \
                  exact test.".format(i))
            return False
        sum_util += _curr_task.executionTime / _curr_task.period
        sum_util_wcet += _curr_task.executionTime * (1 - (_curr_task.executionTime /
                                                          _curr_task.period))
        curr_task_idx += 1
        if curr_task_idx < num_elements:
            _curr_task = rq_buf[curr_task_idx]
            print("Current Task = ", _curr_task)

    # Add new_task if not done before
    if new_task.priority < _curr_task.priority:
        R_ub = (new_task.executionTime + sum_util_wcet) / (1 - sum_util)
        print("R_ub = {0:d}.{1:d} at end, deadline = {2:d}".format(int(R_ub), int(R_ub*100 -
              int(R_ub*100)), new_task.deadline))
        if R_ub > new_task.deadline:
            print("Deadline hit for new task {0:d}, Taskset might be not schedulable! Maybe try an \
                  exact test.".format(curr_task_idx))
            return False
        print("Upper bound lower then deadline -> taskset is schedulable!")
    return True


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    db_connection = db.openDb(db.db_name)       # Open database
    db_cursor = db_connection.cursor()          # Create a cursor for database

    # Read execution times depending on PKG and save as dictionary
    dict_C = {}     # Empty dictionary
    # Iterate over all table rows
    for row in db_cursor.execute("SELECT * FROM ExecutionTimes"):
        dict_C[row[0]] = row[1]     # Add entry "PKG" : "Execution Time"

    table_name = "Dataset3"     # Name of the table

    # Get number of columns of the table
    db_cursor.execute("PRAGMA table_info('" + table_name + "')")
    numberOfColumns = len(db_cursor.fetchall())

    # Calculate number of tasks in dataset
    # -2 for Set_ID and Exit_Value
    # /8 because each task has 8 properties
    numberOfTasks = int((numberOfColumns - 2) / 8)

    row_counter = 0

    # Read out the table and perform the test for each taskset in table
    for row in db_cursor.execute("SELECT * FROM " + table_name):
        if row_counter == 0:
            taskset = TaskSet()     # Empty taskset
            # Iterate over all tasks
            for i in range(numberOfTasks):
                '''C = dict_C[row[4+i*8]]      # Execution time of task i
                new_task = Task(priority=row[1+i*8], deadline=row[2+i*8], quota=row[3+i*8], pkg=row[4+i*8], arg=row[5+i*8], period=row[6+i*8], numberOfJobs=row[7+i*8], offset=row[8+i*8], executionTime=C)
                if i < (numberOfTasks-1):
                    taskset.addTask(new_task)'''

                # Last task of taskset: check schedulability of taskset
                C = dict_C[row[4+i*8]]      # Execution time of task i
                new_task = Task(priority=row[1+i*8], deadline=row[2+i*8], quota=row[3+i*8], pkg=row[4+i*8], arg=row[5+i*8], period=row[6+i*8], numberOfJobs=row[7+i*8], offset=row[8+i*8], executionTime=C)
                print("New Task = ", new_task)
                print("Task-Set = ", taskset)
                schedulability = fp_sufficient_test(new_task, taskset)
                'schedulability = RTA(new_task, taskset)
                print("Schedulability = ", schedulability)
                taskset.addTask(new_task)
            row_counter += 1

    db.closeDb(db_connection)       # Close database
