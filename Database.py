"""Representation of a Database.

    Currently only the following attributes are integrated:
    dir -- path to the database
    name -- name of the database with '.db' extension
    datasets -- list with the names of those tables, that contain the task-sets
    executionTimes -- name of the table with the execution times depending on the task 'Arg'-attribut
    """

import logging
import os
import re
import sqlite3

import Task
from TaskSet import TaskSet

# Attributes of database
dir = os.path.dirname(os.path.abspath(__file__))
name = "database_haecker.db"
datasets = ["Dataset1", "Dataset2", "Dataset3", "Dataset4", "Dataset5"]
executionTimes = "ExecutionTimes"

# Private variables
_db_connection = None  # Connection to the database
_db_cursor = None  # Cursor to work with the database
_current_dataset = 0  # Dataset index: start with first dataset in list
_current_taskset = 0  # Task-set index: start with first task-set in dataset


# Open database
def open_DB():
    """Open the database.

    If there is no database file defined through self.dir and self.name,
    a sqlite3.OperationalError is raised.
    """
    db_path = dir + "\\" + name
    try:
        global _db_connection
        _db_connection = sqlite3.connect("file:" + db_path + "?mode=rw", uri=True)
    except sqlite3.OperationalError as oe:
        logging.error("open_DB(): Database not found! Error message = " + oe)
    else:
        global _db_cursor
        _db_cursor = _db_connection.cursor()


# Close a database
def close_DB():
    """Close the database.

    Before the database is closed, the changes are saved.
    """
    global _db_connection, _db_cursor
    _db_connection.commit()
    _db_connection.close()
    _db_connection = None
    _db_cursor = None


# Set _current_database
def set_current_dataset(new_dataset):
    """Set _current_database to the given value."""
    if new_dataset in datasets:  # new_dataset is valid
        global _current_dataset, _current_taskset
        _current_dataset = new_dataset  # Set dataset index to given value
        _current_taskset = 0  # Reset task-set index
    else:  # new_dataset is invalid
        logging.error("set_current_dataset(): new_datset is invalid!")


# Get a task-set
def get_taskset(dataset=_current_dataset, taskset=_current_taskset):
    """Get a task-set.

    If no arguments are given, the _current_dataset and _current_taskset is returned.
    dataset -- index of the dataset
    taskset -- index of the taskset
    """

    # Get a row (= task-set) from the database
    open_DB()
    sql = "SELECT * FROM " + datasets[dataset]
    _db_cursor.execute(sql)
    row = _db_cursor.fetchall()[taskset]
    close_DB()

    # Get number of tasks within the taskset (= last number of dataset-name)
    number_of_tasks = int(re.findall(r'\d+', datasets[dataset])[-1])

    # Create empty task-set
    taskset = TaskSet(id=row[0], exit_value=row[-1])

    # Iterate over all tasks in task-set
    for i in range(number_of_tasks):
        # Extract task properties
        priority = row[1 + i * Task.number_of_properties]
        deadline = row[2 + i * Task.number_of_properties]
        quota = row[3 + i * Task.number_of_properties]
        pkg = row[4 + i * Task.number_of_properties]
        arg = row[5 + i * Task.number_of_properties]
        period = row[6 + i * Task.number_of_properties]
        number_of_jobs = row[7 + i * Task.number_of_properties]
        offset = row[8 + i * Task.number_of_properties]

        # Get execution time depending on pkg
        execution_time = _get_executionTime(pkg)

        # Create new task
        new_task = Task.Task(priority, deadline, quota, pkg, arg, period, number_of_jobs, offset,
                             execution_time)

        # Add new task to task-set
        taskset.addTask(new_task)

    # Return the created task-set
    return taskset


# Get execution time of a task
def _get_executionTime(pkg=None):
    """Get the execution time of a task defined by pkg.

    If no pkg is given, 0 is returned.
    """
    if pkg is None:  # no argument given
        return 0
    else:
        open_DB()
        sql = "SELECT ExecutionTime FROM " + executionTimes + " WHERE PKG=?"
        _db_cursor.execute(sql, (pkg,))
        execution_time = _db_cursor.fetchall()
        close_DB()
        return execution_time[0][0]