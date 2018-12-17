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


class Task:

    # Constructor
    def __init__(self, id=-1, priority=-1, pkg=None, arg=None, deadline=-1, period=-1,
                 number_of_jobs=-1, execution_time=-1):
        """Constructor: initialize the attributes."""
        self.id = id
        self.priority = priority
        self.pkg = pkg
        self.arg = arg
        self.deadline = deadline
        self.period = period
        self.number_of_jobs = number_of_jobs
        self.execution_time = execution_time

    # String representation
    def __str__(self):
        """Represent task as string."""
        s = "[id=" + str(self.id) + " prio=" + str(self.priority) + " " + str(self.pkg) + "(" + str(
            self.arg) + ") D=" + str(self.deadline) + " T=" + str(self.period) + " " + str(
            self.number_of_jobs) + "x C=" + str(self.execution_time) + "]"
        return s
