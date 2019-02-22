"""Module Taskset."""
import logging
import operator

from Task import Task


class Taskset:
    """Representation of a task-set.

    Currently only the following attributes are integrated:
        id -- id of the task-set, corresponds to column 'Set_ID'
        result -- 1 if task-set could be successfully scheduled, otherwise 0
        tasks -- list of tasks (task objects)
    """

    # Constructor
    def __init__(self, taskset_id=-1, result=-1, tasks=None):
        """Constructor: initialize the task-set."""
        self.taskset_id = taskset_id
        self.result = result
        if tasks is None:
            self.tasks = []
        else:
            self.tasks = tasks

        # Sort tasks according to increasing priorities
        self.sort()

    # String representation
    def __str__(self):
        """Represent task-set as string."""
        representation_string = "id=" + str(self.taskset_id) + " result=" + str(self.result) + " " \
                                + str([str(task) for task in self.tasks])
        return representation_string

    # Add task
    def add_task(self, task):
        """Add a new task to the task-set.

        Check the input argument. If a correct input is given, add the task to the task-set and
        sort it according to priorities.
        Input arguments:
            task -- the task that should be added, must be of type 'Task'
        """
        # Check input arguments
        if not isinstance(task, Task):  # Wrong input argument
            logging.error("Taskset/add_task(): wrong input argument - must be of type 'Task'")
            return

        self.tasks.append(task)  # Add task to task-set
        self.sort()  # Sort tasks according to increasing priorities

    # Length of task-set
    def __len__(self):
        """Get length of task-set = number of tasks."""
        return len(self.tasks)

    # Iterator
    def __iter__(self):
        """Iterate over the task-list."""
        return self.tasks.__iter__()

    # Index
    def __getitem__(self, index):
        """Get task at index."""
        return self.tasks[index]

    # Sort task-set
    def sort(self):
        """Sort the task-set.

        The task-set is sorted according to the task priorities in increasing order.
        """
        self.tasks.sort(key=operator.attrgetter('priority'))
