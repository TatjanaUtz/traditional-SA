"""RTA Modul
Response Time Analysis Methods.
"""
import logging
import math

import Database as db
from Task import Task
from TaskSet import TaskSet


def _compute_response_time(new_task, num_elements, check_task, taskset):
    global _response_time_old, _response_time, _first_task
    _response_time_old = check_task.executionTime
    while True:
        _curr_task = taskset[0]
        _curr_task_idx = 0
        _response_time = check_task.executionTime
        for i in range(num_elements):
            _curr_task = taskset[_curr_task_idx]
            _response_time += math.ceil(_response_time_old / _curr_task.period) * \
                              _curr_task.executionTime
            _curr_task_idx += 1

        # If check_task is another task then new_task we have to add the new_task here
        if new_task != check_task:
            _response_time += math.ceil(_response_time_old / new_task.period) * \
                              new_task.executionTime

        logging.debug("response_time = {0:d}, response_time_old = {1:d}, deadline = {2:d}"
              .format(_response_time, _response_time_old, check_task.deadline))

        ''' Since the response_time is increasing with each iteration, it has to be always smaller
        then the deadline -> we can stop if we hit the deadline. '''
        if _response_time > check_task.deadline:
            # Task-Set is NOT schedulable
            logging.debug("Task-Set is NOT schedulable!")
            return False
        if _response_time_old >= _response_time:
            if _response_time <= check_task.deadline:
                # Task-Set is schedulable
                logging.debug("Task-Set is schedulable! Response time = {0:d}, deadline = {1:d}"
                      .format(_response_time, check_task.deadline))
                return True
        _response_time_old = _response_time


def RTA(new_task, rq_buf):
    global _response_time_old, _response_time, _first_task

    num_elements = len(rq_buf)

    ''' Assuming that each task is schedulable if it is alone, the task is accepted if the rq_buf
    is empty.'''
    if num_elements == 0:
        logging.debug("num_elements == 0, Task-Set is schedulable!")
        return True

    ''' RTA.py-Algorithm
    We assume that the existing Task-Set is schedulable without the new task. Therefore the
    response time has to e computed for the new task and all tasks having a smaller priority then
    the new task and for the new task. The tasks in the rq_buf are assumed to be sorted by
    priorities. '''
    _first_task = rq_buf[0]
    _curr_task = _first_task
    _curr_task_idx = 0
    if new_task.priority < rq_buf[-1].priority:
        logging.debug("New task hast lower priority the all other tasks, priority_new = {0:d}, \
              priority_last = {1:d}".format(new_task.priority, rq_buf[-1].priority))
        _response_time_old = new_task.executionTime
        if not _compute_response_time(new_task, num_elements, new_task, rq_buf):
            # Task-Set is not schedulable
            logging.debug("Task-Set is not schedulable!")
            return False
    else:
        # Compute response time for all tasks having priority smaller then the new task.
        logging.debug("New task has higher or the same priority then lowest existing task, priority_new = \
              {01:d}, priority_last = {1:d}".format(new_task.priority, rq_buf[-1].priority))
        for i in range(num_elements):
            _curr_task = rq_buf[_curr_task_idx]
            _response_time_old = _curr_task.executionTime
            if _curr_task.priority <= new_task.priority:
                if not _compute_response_time(new_task, i, _curr_task, rq_buf):
                    # Task-Set is not schedulable
                    return False

            # Check new_task at right position
            if _curr_task.priority > new_task.priority and (rq_buf[_curr_task_idx+1]).priority <= \
               new_task.priority and i > 0:
                if not _compute_response_time(new_task, i+1, new_task, rq_buf):
                    # Task-Set is not schedulable
                    logging.debug("Task-Set is not schedulable!")
                    return False
            _curr_task_idx += 1
    logging.debug("All Task-Sets passed the RTA.py Algorithm -> Task-Set schedulable!")
    return True

def test_RTA(dataset):
    db_connection = db.openDb(db.db_name)  # Open database
    db_cursor = db_connection.cursor()  # Create a cursor for database

    # Read execution times depending on PKG and save as dictionary
    dict_C = {}  # Empty dictionary
    # Iterate over all table rows
    for row in db_cursor.execute("SELECT * FROM ExecutionTimes"):
        dict_C[row[0]] = row[1]  # Add entry "PKG" : "Execution Time"

    # Variables for efficiency check
    tp, fp, tn, fn, total = 0, 0, 0, 0, 0

    table_name = dataset  # Name of the table

    # Get number of columns of the table
    db_cursor.execute("PRAGMA table_info('" + table_name + "')")
    numberOfColumns = len(db_cursor.fetchall())

    # Calculate number of tasks in dataset
    # -2 for Set_ID and Exit_Value
    # /8 because each task has 8 properties
    numberOfTasks = int((numberOfColumns - 2) / 8)

    # Read out the table and perform the test for each taskset in table
    for row in db_cursor.execute("SELECT * FROM " + table_name):
        taskset = TaskSet()  # Empty taskset
        schedulability = None
        # Iterate over all tasks
        for i in range(numberOfTasks):
            C = dict_C[row[4 + i * 8]]  # Execution time of task i
            new_task = Task(priority=row[1 + i * 8], deadline=row[2 + i * 8], quota=row[3 + i * 8],
                            pkg=row[4 + i * 8], arg=row[5 + i * 8], period=row[6 + i * 8],
                            numberOfJobs=row[7 + i * 8], offset=row[8 + i * 8], executionTime=C)
            if i == (numberOfTasks - 1):  # Last task of taskset: check schedulability
                schedulability = RTA(new_task, taskset)
                logging.debug("Schedulability = " + str(schedulability))
            else:
                taskset.addTask(new_task)

        # Evaluate Taskset
        exitValue = row[-1]

        # Analyse efficiency of utilization_test
        if schedulability is True and exitValue == 1:
            tp += 1
        elif schedulability is True and exitValue == -1:
            fp += 1
        elif schedulability is False and exitValue == 1:
            fn += 1
        elif schedulability is False and exitValue == -1:
            tn += 1
        total += 1

    # Print results
    print("---------- RESULTS OF RTA.py FOR " + table_name + " ----------")
    print("Correct: {0:d} / {1:d} -> {2:.0f}%".format(tp + tn, total, (tp + tn) * 100 / total))
    print("Incorrect: {0:d} / {1:d} -> {2:.0f}%".format(fp + fn, total, (fp + fn) * 100 / total))
    print("True positive (tp) = {0:d}".format(tp))
    print("False positive (fp) = {0:d}".format(fp))
    print("True negative (tn) = {0:d}".format(tn))
    print("False negative (fn) = {0:d}".format(fn))
    print("-------------------------------------------------")

    db.closeDb(db_connection)  # Close database


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    dataset = "Dataset3"

    # Test RTA.py
    '''test_RTA("Dataset1")
    test_RTA("Dataset2")
    test_RTA("Dataset3")
    test_RTA("Dataset4")
    test_RTA("Dataset5")'''