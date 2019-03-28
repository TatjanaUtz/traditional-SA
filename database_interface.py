"""Class and methods for database connectivity.

This module provides classes and methods for importing task-sets from the SQLite database
and formatting data into a format usable with tensorflow.
"""

import logging
import operator
import os
import sqlite3

from benchmark import benchmark_execution_times

# default task execution times
DEFAULT_EXECUTION_TIMES = {
    ("hey", 0): 1045,
    ("hey", 1000): 1094,
    ("hey", 1000000): 1071,

    ("pi", 100): 1574,
    ("pi", 10000): 1693,
    ("pi", 100000): 1870,

    ("cond_42", 41): 1350,
    ("cond_42", 42): 1376,
    ("cond_42", 10041): 1413,
    ("cond_42", 10042): 1432,
    ("cond_42", 1000041): 1368,
    ("cond_42", 1000042): 1396,

    ("cond_mod", 100): 1323,
    ("cond_mod", 103): 1351,
    ("cond_mod", 10000): 1395,
    ("cond_mod", 10003): 1391,
    ("cond_mod", 1000000): 1342,
    ("cond_mod", 1000003): 1391,

    ("tumatmul", 10): 1511,
    ("tumatmul", 11): 1543,
    ("tumatmul", 10000): 1692,
    ("tumatmul", 10001): 1662,
    ("tumatmul", 1000000): 3009,
    ("tumatmul", 1000001): 3121,

    "hey": 1070,
    "pi": 1712,
    "cond_42": 1389,
    "cond_mod": 1366,
    "tumatmul": 2090
}


class Task():
    """Representation of a task.

    Currently only the following attributes are integrated:
        id -- id of the task, corresponds to column 'Task_ID'
        priority -- priority of task, 1 is the highest priority
        pkg -- name of the task, corresponds to column 'PKG'
        arg -- argument of task, has influence on the execution time
        deadline -- deadline of the task
        period -- period of the task
        number_of_jobs -- number of jobs, defines how often the task is executed
        execution_time -- time needed to execute the task
    """

    def __init__(self, task_id=-1, priority=-1, pkg=None, arg=None, deadline=-1, period=-1,
                 number_of_jobs=-1, execution_time=-1):
        """Constructor"""
        self.task_id = task_id
        self.priority = priority
        self.pkg = pkg
        self.arg = arg
        self.deadline = deadline
        self.period = period
        self.number_of_jobs = number_of_jobs
        self.execution_time = execution_time
        if self.deadline == -1:
            self.deadline = self.period

    def __str__(self):
        """Represent task as string."""
        repr_str = "(id=" + str(self.task_id) + " prio=" + str(self.priority) + " " + str(self.pkg) \
                   + "(" + str(self.arg) + ") D=" + str(self.deadline) + " T=" + str(self.period) \
                   + " " + str(self.number_of_jobs) + "x C=" + str(self.execution_time) + ")"
        return repr_str


class Taskset:
    """Representation of a task-set.

    Currently only the following attributes are integrated:
        taskset_id -- ID of the task-set, corresponds to column 'Set_ID'
        result -- 1 if task-set could be successfully scheduled, otherwise 0, corresponds to column
                  'Sucessful'
        tasks -- list of tasks (of type Task)
    """

    def __init__(self, taskset_id=-1, result=-1, tasks=None):
        """Constructor."""
        self.taskset_id = taskset_id
        self.result = result
        if tasks is None:
            self.tasks = []
        else:
            self.tasks = tasks

        # Sort tasks according to priorities
        self.tasks.sort(key=operator.attrgetter('priority'))

    def __str__(self):
        """Represent Taskset object as String."""
        representation_string = "id=" + str(self.taskset_id) + " result=" + str(self.result) + " " \
                                + str([str(task) for task in self.tasks])
        return representation_string

    def __len__(self):
        """Get length of task-set = number of tasks."""
        return len(self.tasks)

    def __iter__(self):
        """Iterate over the task-list."""
        return self.tasks.__iter__()

    def __getitem__(self, index):
        """Get task at index."""
        return self.tasks[index]

    def add_task(self, task):
        """Add a new task to the task-set.

        Check the input argument. If a correct input is given, add the task to the task-set and
        sort it according to priorities.

        Args:
            task -- the task that should be added, must be of type 'Task'
        """
        # check input arguments
        if not isinstance(task, Task):  # wrong input argument
            raise ValueError("task must be of type Task")

        self.tasks.append(task)  # add task to task-set
        self.tasks.sort(
            key=operator.attrgetter('priority'))  # sort tasks according to increasing priorities


class Database:
    """Class representing a database.

    The database is defined by following attributes:
        db_dir -- path to the database file (*.db)
        db_name -- name of the database file (incl. .db)
    Additional attributes of a Database object are:
        db_connection -- connection to the database
        db_cursor -- cursor for working with the database
        execution_time_dict -- dictionary with the execution times of the tasks
    """

    def __init__(self, db_dir, db_name):
        """Constructor of class Database."""

        self.db_dir = db_dir  # path to the database
        self.db_name = db_name  # name of the database
        self.db_connection = None  # connection to the database
        self.db_cursor = None  # cursor for working with the database

        # initalize execution times with default values
        self.execution_time_dict = DEFAULT_EXECUTION_TIMES

        # check that database exists
        self._check_if_database_exists()

        # check the database: check if all necessary tables exist
        self._check_database()

        # read table 'ExecutionTime': update execution times
        self.execution_time_dict = self.read_table_executiontime()

    #############################
    # check database and tables #
    #############################

    def _check_if_database_exists(self):
        """Check if the database file exists.

        This method checks if the database defined by self.db_dir and self.db_name exists. If not,
        an exception is raise.
        """
        db_path = self.db_dir + "\\" + self.db_name  # create full path to database

        # check if database exists
        if not os.path.exists(db_path):  # database doesn't exists: raise exception
            raise Exception("database '%s' not found in %s", self.db_name, self.db_dir)

    def _check_database(self):
        """Check the database.

        This method checks the database, i.e. if all necessary tables are present. The necessary
        tables are
            Job
            Task
            TaskSet
            ExecutionTime.
        If a table does not exist in the database, it is created (if possible) or an Exception is
        raised.
        """
        # check table Job
        if not self._check_if_table_exists('Job'):  # table Job does not exist
            raise Exception("no such table: %s", 'Job')

        # check table Task
        if not self._check_if_table_exists('Task'):  # table Task does not exist
            raise Exception("no such table: %s", 'Task')

        # check table TaskSet
        if not self._check_if_table_exists('TaskSet'):  # table TaskSet does not exist
            raise Exception("no such table: %s", 'TaslSet')

        # check table ExecutionTime
        if not self._check_if_table_exists('ExecutionTime'):
            # table ExecutionTime does not exist: create it through benchmark
            benchmark_execution_times(self)

            # check that table was successfully created
            if not self._check_if_table_exists('ExecutionTime'):  # something went wrong
                raise Exception("nos such table %s - creation not possible", 'ExecutionTime')

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

        rows = self.db_cursor.fetchall()  # fetch all rows
        self._close_db()  # close database

        if not rows:  # no row could be fetched - table doesn't exist
            return False

        # at least one row was fetched - table exists
        return True

    #########################
    # open / close database #
    #########################

    def _open_db(self):
        """Open the database.

        This methods opens the database defined by self.db_dir and self.db_name by creating a
        database connection and a cursor.
        """
        db_path = self.db_dir + "\\" + self.db_name  # create full path to the database

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

    #######################
    # read / write tables #
    #######################

    def read_table_job(self, task_id=None, exit_value=None):
        """Read the table Job.

        This method reads the table Job of the database. If task_id is not specified, the hole table
        is read. If task_id is specified, only the jobs of the task defined by task_id are read.
        If exit_value is specified, only the jobs with this exit_value are read.

        Args:
            task_id -- ID of the task which jobs should be read
            exit_value -- exit_value of the jobs that should be read
        Return:
            rows -- list with the job attributes
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database_interface.read_table_job')

        self._open_db()  # open database

        if task_id is not None and exit_value is not None:
            # read all jobs of task_id with exit_value
            self.db_cursor.execute("SELECT * FROM Job WHERE Task_ID = ? AND Exit_Value = ?",
                                   (task_id, exit_value))
        else:  # read all jobs
            self.db_cursor.execute("SELECT * FROM Job")

        rows = self.db_cursor.fetchall()
        self._close_db()  # close database

        return rows

    def read_table_task(self, task_id=None, dict=True):
        """Read the table Task.

        This method reads the table Task of the database. If task_id is not specified, the hole
        table is read. If task_id is specified, only the task defined by task_id is read.

        Args:
            task_id -- ID of the task which should be read
            dict -- whether the tasks should be returned as list or dictionary
        Return:
            rows -- list with the task attributes
            task_dict -- dictionary of the task attributes (key = task ID, value = Task-object)
        """
        self._open_db()  # open database

        if task_id is not None:  # read task with task_id
            self.db_cursor.execute("SELECT * FROM Task WHERE Task_ID = ?", (task_id,))
        else:  # read all tasks
            self.db_cursor.execute("SELECT * FROM Task")

        rows = self.db_cursor.fetchall()
        self._close_db()  # close database

        if dict:  # convert task attributes to dictionary
            task_dict = self._convert_to_task_dict(rows)
            return task_dict

        return rows

    def read_table_taskset(self, taskset_id=None, convert=True):
        """Read the table TaskSet.

        This method reads the table TaskSet of the database.

        Args:
            taskset_id -- ID of the task-set which should be read
            convert -- whether the task-sets should be converted to objects of type Taskset
        Return:
            dataset -- list with the task-sets
        """
        self._open_db()  # open database

        if taskset_id is not None:  # read task-set with taskset_id
            self.db_cursor.execute("SELECT * FROM TaskSet WHERE Set_ID = ?", (taskset_id,))
        else:  # read all tasks-sets
            self.db_cursor.execute("SELECT * FROM TaskSet")

        rows = self.db_cursor.fetchall()
        self._close_db()  # close database

        # TODO: Limit number of rows
        rows = rows[:5]

        if convert:  # convert task-sets to objects of type Taskset
            dataset = self._convert_to_taskset(rows)
            return dataset

        return rows

    def read_table_executiontime(self, dict=True):
        """Read the table ExecutionTime.

        This method reads the table ExecutionTime. The hole table is read, i.e. all rows.

        Args:
            dict -- whether the execution times should be returned as list or dictionary

        Return:
            execution_times -- list with the execution times
            c_dict -- dictionary of the execution times (key = PKG or (PKG, Arg), value = execution
                      time)
        """
        self._open_db()  # open database

        # read all execution times
        self.db_cursor.execute("SELECT * FROM ExecutionTime")
        rows = self.db_cursor.fetchall()
        self._close_db()  # close database

        if dict:  # convert execution times to dictionary
            c_dict = self._convert_to_executiontime_dict(rows)
            return c_dict

        return rows

    def write_execution_time(self, c_dict):
        """Write the execution times to the database.

        Args:
            task_dict -- dictionary with all task execution times
        """
        # create logger
        logger = logging.getLogger('traditional-SA.database._write_execution_time')

        self._open_db()  # open database

        # create table ExecutionTime if it does not exist
        create_table_sql = "CREATE TABLE IF NOT EXISTS ExecutionTime (" \
                           "[PKG(Arg)] TEXT, " \
                           "[Average_C] INTEGER, " \
                           "PRIMARY KEY([PKG(Arg)])" \
                           ");"
        try:
            self.db_cursor.execute(create_table_sql)
        except sqlite3.Error as sqle:
            logger.error(sqle)

        # sql statement for inserting or replacing a row in the ExecutionTime table
        insert_or_replace_sql = "INSERT OR REPLACE INTO ExecutionTime" \
                                "([PKG(Arg)], Average_C) VALUES(?, ?)"

        # iterate over all keys
        for key in c_dict:
            if isinstance(key, str):  # key = (PKG)
                # insert or replace task-set
                self.db_cursor.execute(insert_or_replace_sql, (key, c_dict[key]))
            elif len(key) == 2:  # key = (PKG, Arg)
                self.db_cursor.execute(insert_or_replace_sql,
                                       (key[0] + "(" + str(key[1]) + ")", c_dict[key]))

        self._close_db()  # close database

    ##############
    # conversion #
    ##############

    def _convert_to_task_dict(self, task_attributes):
        """Convert a list of task attributes to a dictionary of Task-objects.

        This function converts a list of task attributes to a dictionary with
            key = task ID
            value = object of type Task.

        Args:
            task_attributes -- list with pure task attributes
        Return:
            task_dict -- dictionary with Task-objects
        """
        task_dict = dict()  # create empty dictionary for tasks

        for row in task_attributes:  # iterate over all task attribute rows
            # get execution time of task depending on PKG and Arg
            pkg = row[5]
            arg = row[6]
            if (pkg, arg) in self.execution_time_dict:  # (PKG, Arg)
                execution_time = self.execution_time_dict[(pkg, arg)]
            else:  # (PKG)
                execution_time = self.execution_time_dict[pkg]

            # create new task
            new_task = Task(task_id=row[0], priority=row[1], pkg=row[5], arg=row[6],
                            deadline=row[9], period=row[10], number_of_jobs=row[11],
                            execution_time=execution_time)

            # add task to dictionary
            task_dict[row[0]] = new_task

        return task_dict

    def _convert_to_taskset(self, rows):
        """Convert a list of task-sets to objects of type Taskset.

        This function converts a list of task-sets from the table TaskSet to a list of Taskset
        objects.

        Args:
            rows -- the rows read from the table TaskSet
        Return:
            dataset -- list of Taskset objects
        """
        # read table 'Task': get dictionary with task attributes
        # (key = task ID, value = Task-object)
        task_attributes = self.read_table_task()

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

    def _convert_to_executiontime_dict(self, execution_times):
        """Convert a list of execution times to a dictionary.

        This function converts a list of execution times to a dictionary with
            key = PKG or (PKG, Arg)
            value = execution time.

        Args:
            execution_times -- list with pure execution times
        Return:
            c_dict -- dictionary with execution times
        """
        # create dictionary with default execution times
        c_dict = DEFAULT_EXECUTION_TIMES

        for row in execution_times:  # iterate over all execution time rows
            # extract identifier and execution time
            pkg_arg = row[0]
            average_c = row[1]

            # split pkg and arg and create new dictionary entry
            if '(' in pkg_arg:  # string contains pkg and arg
                pkg, arg = pkg_arg.split('(')
                arg = int(arg[:-1])  # delete last character = ')' and format to int
                dict_entry = {(pkg, arg): average_c}
            else:  # string contains only pkg, no arg
                pkg = pkg_arg
                dict_entry = {pkg: average_c}

            # update dictionary
            c_dict.update(dict_entry)

        return c_dict
