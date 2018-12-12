"""Representation of a task."""

# Variables
number_of_properties = 8


class Task:
    """Representation of a Task.

    A task is defined by the attributes priority, deadline, quota, pkg,
    arg, period, numberOfJobs, offset and execution time.
    """

    # Constructor
    def __init__(self, priority=None, deadline=None, quota='10M', pkg=None, arg=None, period=None,
                 numberOfJobs=1, offset=None, executionTime=None):
        """Constructor: initialize the attributes."""
        self.priority = priority
        self.deadline = deadline
        self.quota = quota
        self.pkg = pkg
        self.arg = arg
        self.period = period
        self.numberOfJobs = numberOfJobs
        self.offset = offset
        self.executionTime = executionTime

    # String representation
    def __str__(self):
        """Represent task as string."""
        dict = {
            "Priority": self.priority,
            "Deadline": self.deadline,
            "Quota": self.quota,
            "PKG": self.pkg,
            "Arg": self.arg,
            "Period": self.period,
            "Number of Jobs": self.numberOfJobs,
            "Offset": self.offset,
            "Execution Time": self.executionTime
        }
        return str(dict)
