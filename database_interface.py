"""Class and functions for database connectivity."""
import logging  # for logging
import math  # for ceil-function
import os  # for current directory dir
import sqlite3  # for working with the database

from Task import Task  # for creating tasks
from Taskset import Taskset  # for creating task-sets
from benchmark_runtimes import benchmark_runtimes

# task execution times
EXECUTION_TIME_DICT = {
    ("hey", 0): (1045, 1045, 1045),
    ("hey", 1000): (1094, 1094, 1094),
    ("hey", 1000000): (1071, 1071, 1071),

    ("pi", 100): (1574, 1574, 1574),
    ("pi", 10000): (1693, 1693, 1693),
    ("pi", 100000): (1870, 1870, 1870),

    ("cond_42", 41): (1350, 1350, 1350),
    ("cond_42", 42): (1376, 1376, 1376),
    ("cond_42", 10041): (1413, 1413, 1413),
    ("cond_42", 10042): (1432, 1432, 1432),
    ("cond_42", 1000041): (1368, 1368, 1368),
    ("cond_42", 1000042): (1396, 1396, 1396),

    ("cond_mod", 100): (1323, 1323, 1323),
    ("cond_mod", 103): (1351, 1351, 1351),
    ("cond_mod", 10000): (1395, 1395, 1395),
    ("cond_mod", 10003): (1391, 1391, 1391),
    ("cond_mod", 1000000): (1342, 1342, 1342),
    ("cond_mod", 1000003): (1391, 1391, 1391),

    ("tumatmul", 10): (1511, 1511, 1511),
    ("tumatmul", 11): (1543, 1543, 1543),
    ("tumatmul", 10000): (1692, 1692, 1692),
    ("tumatmul", 10001): (1662, 1662, 1662),
    ("tumatmul", 1000000): (3009, 3009, 3009),
    ("tumatmul", 1000001): (3121, 3121, 3121),

    "hey": (1070, 1070, 1070),
    "pi": (1712, 1712, 1712),
    "cond_42": (1389, 1389, 1389),
    "cond_mod": (1366, 1366, 1366),
    "tumatmul": (2090, 2090, 2090)
}


class Database:
    """Class representing a database.

    The database is defined by following attributes:
        db_dir -- path to the database file (*.db)
        db_name -- name of the database file (incl. .db)
    Also following settings are saved within the class:
        round_execution_time -- saves if execution times should be rounded (True) or not (False)
        c_type -- value representing which execution time type should be used
    """

    # constructor
    def __init__(self):
        """Constructor of class Database."""

        # path to the database = current working directory
        self.db_dir = os.path.dirname(os.path.abspath(__file__))

        # name of the database
        self.db_name = "panda_v2.db"

        # round up execution time to next higher int -> little bit faster
        self.round_execution_time = True

        # Which type of execution time should be used?
        # 0: minimum execution time (BCET, best case execution time)
        # 1: maximum execution time (WCET, worst case execution time)
        # 2: average execution time
        self.c_type = 2

        # connection to the database
        self.db_connection = None

        # cursor for working with the database
        self.db_cursor = None

        # check if database exists
        if not self._check_if_database_exists():
            # database does not exist at the defined path
            raise Exception("database '{}' not found in {}".format(self.db_name, self.db_dir))

        # check database: check if all necessary tables exist
        check_value, table_name = self._check_database()
        if not check_value:
            # something is not correct with the database: at least one table is missing
            raise Exception("no such table: " + table_name)

        # dictionary with execution times of all tasks
        self.execution_time_dict = EXECUTION_TIME_DICT
        self.read_execution_times()

    def _open_db(self):
        """Open the database.

        This methods opens the database defined by self.db_dir and self.db_name by creating a
        database connection and a cursor.
        """
        # create full path to the database
        db_path = self.db_dir + "\\" + self.db_name

        # create database connection and a cursor
        self.db_connection = sqlite3.connect(db_path)
        self.db_cursor = self.db_connection.cursor()

    def _close_db(self):
        """Close the database.

        This method commits the changes to the database and closes it by closing and deleting the
        database connection and the cursor.
        """
        # commit changes and close connection to the database
        self.db_connection.commit()
        self.db_connection.close()

        # delete database connection and cursor
        self.db_connection = None
        self.db_cursor = None

    def _check_if_database_exists(self):
        """Check if the database file exists.

        This method checks if the database defined by self.db_dir and self.db_name exists.

        Return:
            True/False -- whether the database exists
        """
        # create full path to database
        db_path = self.db_dir + "\\" + self.db_name

        # Check if database exists
        if os.path.exists(db_path):  # database exists
            return True
        return False

    def _check_database(self):
        """Check the database.

        This method checks the database, i.e. if all necessary tables are present. The necessary
        tables are
            Job
            Task
            TaskSet
            ExecutionTimes
        If a table does not exist in the database, it is created (if possible).

        Return:
            True/False -- whether all necessary tables exist
            the name of the table which doesn't exist in the database
        """
        # Check table Job
        if not self._check_if_table_exists('Job'):  # table Job does not exist
            return False, 'Job'

        # Check table Task
        if not self._check_if_table_exists('Task'):  # table Task does not exist
            return False, 'Task'

        # check table TaskSet
        if not self._check_if_table_exists('TaskSet'):  # table TaskSet does not exist
            return False, 'TaskSet'

        # Check table ExecutionTimes
        if not self._check_if_table_exists('ExecutionTimes'):
            # table ExecutionTime does not exist: create it through benchmark
            benchmark_runtimes(self)

        # all tables exist
        return True, None

    def _check_if_table_exists(self, table_name):
        """Check if a table exists in the database.

        This method checks if the table defined by table_name exists in the database. This is done
        by executing a SQL query and evaluate the fetched rows. If nothing could be fetched (no rows
        available), the table doesn't exist.

        Args:
            table_name -- name of the table that should be checked
        Return:
            True/False -- whether the table exists/doesn't exist in the database
        """
        self._open_db()  # open database

        # execute the following query to determine if the table exists
        sql_query = "SELECT * from sqlite_master " \
                    "WHERE type = 'table' AND name = '{}'".format(table_name)
        self.db_cursor.execute(sql_query)

        # fetch all rows
        rows = self.db_cursor.fetchall()

        if not rows:  # no row could be fetched - table doesn't exist
            self._close_db()  # close database
            return False

        # at least one row was fetched - table exists
        self._close_db()  # close database
        return True

    ###############################

    def get_dataset(self):
        """Create a dataset of task-sets.

        This method reads all task-sets from the table TaskSet and creates a dataset with them.

        Return:
            dataset -- list with task-sets as Taskset-objects
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database.get_dataset')

        # read table 'TaskSet'
        self._open_db()  # open database
        # read all task-sets
        self.db_cursor.execute("SELECT * FROM TaskSet")
        rows = self.db_cursor.fetchall()
        self._close_db()  # close database

        if not rows:  # no task-set read
            logger.debug("No task-set read!")
            return None

        # Limit number of rows
        rows = rows[:5]

        # read table 'Task': get dictionary with task attributes
        # (key = task ID, value = Task object)
        task_attributes = self._read_table_task()

        dataset = []  # create empty list

        # iterate over all rows
        for row in rows:
            # split taskset ID, label and taskset IDs
            taskset_id = row[0]
            label = row[1]
            task_ids = row[2:]

            # create empty task-set
            new_taskset = Taskset(taskset_id=taskset_id, result=label, tasks=[])

            # iterate over all tasks and add them to the task-set
            for task_id in task_ids:
                if task_id != -1:  # valid task-id
                    new_task = task_attributes[task_id]  # get task
                    new_taskset.add_task(new_task)  # add task to task-set

            # add task-set to dataset
            dataset.append(new_taskset)

        return dataset

    def _read_table_task(self):
        """Read the table Task.

        Read all rows and columns from the table Task and save the task attributes as a dictionary
        with    key = Task_ID
                value = object of class Task.

        Return:
            task_attributes -- dictionary with the task attributes
        """
        # create logger
        logger = logging.getLogger("traditional-SA.database_interface.read_table_task")

        self._open_db()  # open database
        # read all tasks
        self.db_cursor.execute("SELECT * FROM Task")
        rows = self.db_cursor.fetchall()
        self._close_db()  # close database

        if not rows:  # no task read
            logger.debug("No task read!")
            return None

        task_attributes = dict()  # create empty dictionary

        for row in rows:  # iterate over all rows
            # extract task attributes
            task_id = row[0]
            priority = row[1]
            pkg = row[5]
            arg = row[6]
            deadline = row[9]
            period = row[10]
            number_of_jobs = row[11]

            # define execution time depending on pkg and arg
            if (pkg, arg) in self.execution_time_dict:  # combination of pkg and arg exists
                execution_time = self.execution_time_dict[(pkg, arg)][self.c_type]
            else:  # combination of pkg and arg does not exist
                # use only pkg to determine execution time
                execution_time = self.execution_time_dict[pkg][self.c_type]

            # Create new task
            new_task = Task(task_id=task_id, priority=priority, pkg=pkg, arg=arg, deadline=deadline,
                            period=period, number_of_jobs=number_of_jobs,
                            execution_time=execution_time)

            # add task to dictionary
            task_attributes[task_id] = new_task

        return task_attributes

    ################################

    # TODO: can be deleted if testing.py is deleted
    def get_taskset(self, taskset_id=0):
        """Get a task-set.

        Read a task-set from the database. If no ID is given, the first task-set is returned.

        Input arguments:
            taskset_id -- index of the task-set, corresponds to ID of task-set (column Set-ID)
        Return value:
            the task-set
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database.get_taskset')

        # Check input argument - must be a positive integer number
        if not isinstance(taskset_id, int) or taskset_id < 0:  # invalid input
            raise ValueError("Invalid input argument - must be an positive int!")

        self._open_db()  # open database
        # read the task-set from the database
        self.db_cursor.execute("SELECT * FROM TaskSet WHERE Set_ID = ?", (taskset_id,))
        row = self.db_cursor.fetchall()
        self._close_db()  # close database

        if not row:  # no task-set with Set_ID = id found
            logger.debug("No task-set with ID = %d found!", taskset_id)
            return None

        if len(row) > 1:  # more than one task-set with Set_ID = id found
            raise ValueError("Something is wrong - more than one task-set with ID = %d found",
                             taskset_id)

        # one task-set was found: extract task-set attributes
        taskset_id = row[0][0]
        label = row[0][1]
        task_ids = row[0][2:]

        # Create empty task-set
        new_taskset = Taskset(taskset_id=taskset_id, result=label, tasks=[])

        # Iterate over all tasks and create task-set
        for task_id in task_ids:
            if task_id != -1:  # Valid task-id
                new_task = self.get_task(task_id)  # get task from database
                new_taskset.add_task(new_task)  # add task to task-set

        # return created task-set
        return new_taskset

    # TODO: can be deleted if get_taskset is deleted
    def get_task(self, task_id):
        """Read a task from the database.

        Extracts the attributes of a task with the Task-ID defined by task_id and creates a new
        object of class Task.
        Input arguments:
            task_id -- id of the task, corresponds to Task_ID
        Return values:
            task
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database.get_task')

        # Check input argument - must be a positive integer number
        if not isinstance(task_id, int) or task_id < 0:  # invalid input
            raise ValueError("task_id must be of type int")

        self._open_db()  # open database
        # Read the task defined by id
        self.db_cursor.execute("SELECT * FROM Task WHERE Task_ID = ?", (task_id,))
        row = self.db_cursor.fetchall()
        self._close_db()  # close database

        # Check number of rows
        if not row:  # no task with Task_ID = id found
            logger.debug("No task with Task_ID = %d found!", task_id)
            return None
        if len(row) > 1:  # more than one task with Task_ID = id found
            raise ValueError("More than one task with Task_ID = %d found!", task_id)

        # one task was found: extract attributes of the task
        task_id = row[0][0]
        priority = row[0][1]
        pkg = row[0][5]
        arg = row[0][6]
        deadline = row[0][9]
        period = row[0][10]
        number_of_jobs = row[0][11]

        # Define execution time depending on pkg and arg
        if (pkg, arg) in self.execution_time_dict:  # combination of pkg and arg exists
            execution_time = self.execution_time_dict[(pkg, arg)][self.c_type]
        else:  # combination of pkg and arg does not exist
            # use only pkg to determine execution time
            execution_time = self.execution_time_dict[pkg][self.c_type]

        # Create new task
        new_task = Task(task_id=task_id, priority=priority, pkg=pkg, arg=arg, deadline=deadline,
                        period=period, number_of_jobs=number_of_jobs, execution_time=execution_time)

        # Return created task
        return new_task

    def get_all_tasks(self):
        """Read all tasks from the database.

        Extracts the attributes of all tasks and creates a list of task-objects.
        Return:
            list with all tasks
            -1 - an error occurred
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database.get_all_tasks')

        # open database if not connected
        if self.db_connection is None or self.db_cursor is None:
            self._open_db()

        # read all tasks
        self.db_cursor.execute("SELECT * FROM Task")
        rows = self.db_cursor.fetchall()

        # close database
        self._close_db()

        # check number of rows
        if not rows:  # no tasks found
            logger.error("No tasks found!")
            return -1

        # at least one task was found
        task_list = []  # empty list for tasks

        # iterate over all rows, extract attributes and create task
        for row in rows:
            task_id = row[0]
            priority = row[1]
            pkg = row[5]
            arg = row[6]
            deadline = row[9]
            period = row[10]
            number_of_jobs = row[11]

            new_task = Task(task_id=task_id, priority=priority, pkg=pkg, arg=arg, deadline=deadline,
                            period=period, number_of_jobs=number_of_jobs)

            task_list.append(new_task)
        return task_list

    # get all jobs of a task
    def get_jobs_c_of_task(self, task_id):
        """Read all jobs execution times of a task from the database.

        All jobs of a task are read and the execution time is calculated using start and end time.
        Args:
            task_id - id of the task which jobs execution times are wanted
        Return:
            list with execution times of jobs
            -1 -  an error occurred
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database.get_jobs_C')

        # Check input argument - must be a positive integer number
        if not isinstance(task_id, int) or task_id < 0:
            logger.error("Invalid input argument - must be a positive int!")
            return -1

        # Open database if not connected
        if self.db_connection is None or self.db_cursor is None:
            self._open_db()

        # Read all jobs of task defined by task_id with successful execution (Exit_Value = EXIT)
        self.db_cursor.execute("SELECT * FROM Job WHERE Task_ID = ? AND Exit_Value = ?",
                               (task_id, "EXIT"))
        rows = self.db_cursor.fetchall()

        # close database
        self._close_db()

        # Check number of rows
        if not rows:  # no jobs found
            logger.error("No jobs for Task-ID %d found!", task_id)
            return -1

        # create empty list for execution times
        execution_times = []

        # For each job extract attributes and create a new job-object
        for row in rows:
            start_date = row[3]
            end_date = row[4]
            execution_time = end_date - start_date

            if execution_time > 0:  # execution time is valid
                execution_times.append(execution_time)

        return execution_times

    # save execution times of tasks
    def save_execution_times(self, task_dict):
        """Save execution times in the database.

        Saves the given execution times to the database.
        The values of a key consist of (min_C, max_C, average_C).
        Args:
            task_dict - dictionary with task execution times
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database.save_execution_times')

        # Open database if not connected
        if self.db_connection is None or self.db_cursor is None:
            self._open_db()

        # create table "ExecutionTimes" if it does not exist
        create_table_sql = "CREATE TABLE IF NOT EXISTS ExecutionTimes (" \
                           "[PKG(Arg)] text PRIMARY KEY, " \
                           "[Min_C] integer, " \
                           "[Max_C] integer, " \
                           "[Average_C] integer" \
                           ");"
        try:
            self.db_cursor.execute(create_table_sql)
        except sqlite3.Error as sqle:
            logger.error(sqle)

        # sql statement for inserting or replacing a row in the ExecutionTimes table
        insert_or_replace_sql = "INSERT OR REPLACE INTO ExecutionTimes" \
                                "([PKG(Arg)], Min_C, Max_C, Average_C) VALUES(?, ?, ?, ?)"

        # iterate over all dictionary keys
        for key in task_dict:
            # insert or replace the row with the given execution times
            if isinstance(key, str):  # key = (PKG)
                self.db_cursor.execute(insert_or_replace_sql,
                                       (key, task_dict[key][0], task_dict[key][1],
                                        task_dict[key][2]))
            elif len(key) == 2:  # key is combination of pkg and arg: key = (PKG, Arg)
                self.db_cursor.execute(insert_or_replace_sql, (
                    key[0] + "(" + str(key[1]) + ")", task_dict[key][0], task_dict[key][1],
                    task_dict[key][2]))

        # save (commit) the changes
        self.db_connection.commit()

        # close database
        self._close_db()

    # read execution times from database
    def read_execution_times(self):
        """Read the execution times of the tasks from the database.

        The minimum, maximum and average execution times of all tasks are saved in the table
        ExecutionTimes. If this table is not present in the database, the default execution times in
        EXECUTION_TIMES are used.
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database.read_execution_times')

        self._open_db()  # open database

        # read table ExecutionTimes
        self.db_cursor.execute("SELECT * FROM ExecutionTimes")
        rows = self.db_cursor.fetchall()

        # close database
        self._close_db()

        # check if execution times where found
        if not rows:  # now row was read
            logger.error("Table ExecutionTimes does not exist or is empty!")

        # update execution time dictionary
        for row in rows:  # iterate over all rows
            # get data from row
            pkg_arg = row[0]
            min_c = row[1]
            max_c = row[2]
            average_c = row[3]

            if self.round_execution_time:  # round execution time to next higher int
                average_c = math.ceil(average_c)

            # split pkg and arg and create dictionary entry
            if '(' in pkg_arg:  # string contains pkg and arg
                pkg, arg = pkg_arg.split('(')
                arg = int(arg[:-1])  # delete last character = ')' and format to int
                dict_entry = {(pkg, arg): (min_c, max_c, average_c)}
            else:  # string contains only pkg, no arg
                pkg = pkg_arg
                dict_entry = {pkg: (min_c, max_c, average_c)}

            # update dictionary
            self.execution_time_dict.update(dict_entry)
