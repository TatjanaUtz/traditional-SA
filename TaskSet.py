"""Representation of a task-set."""

import operator


class TaskSet:
    """Representation of a Task-Set.

    A taskset is a set of different tasks and is defined by the following attributes:
    id -- id of the task-set
    task -- list of tasks
    exit_value -- exit_value of the task-set
    _task_counter -- number of tasks in the task-set
    """

    # Constructor
    def __init__(self, id=None, tasks=[], exit_value=None):
        """Constructor: initialize a task-set from a list of tasks."""
        self.id = id
        self._tasks = []  # Create empty taskset
        self._task_counter = 0  # Set task counter to 0, as taskset is empty
        for t in tasks:  # Iterate over all tasks
            self._tasks.append(t)  # Add task to taskset
            self._task_counter += 1  # Raise task counter
        self.sort()  # Sort tasks according to increasing priorities
        self.exit_value = exit_value

    # String representation
    def __str__(self):
        """Represent task-set as string."""
        s = "Set_ID = " + str(self.id) + ", Tasks: "
        s += str([str(task) for task in self._tasks])
        s += ", Exit_Value = " + str(self.exit_value)
        return s

    # Add a task
    def addTask(self, task):
        """Add a new task to the task-set."""
        self._tasks.append(task)  # Add task to task-set
        self._task_counter += 1  # Raise task counter
        self.sort()  # Sort tasks according to increasing priorities

    # Length of task-set
    def __len__(self):
        """Get length of task-set = number of tasks."""
        return self._task_counter

    # Iterator
    def __iter__(self):
        """Iterate over all tasks."""
        return self._tasks.__iter__()

    # Index
    def __getitem__(self, index):
        """Get task at index."""
        return self._tasks[index]

    # Sort task-set
    def sort(self):
        """Sort the task-set.

        The task-set is sorted according to the task priorities in increasing order.
        The first task in list is the task with highest priority.
        """
        self._tasks.sort(key=operator.attrgetter('priority'))
