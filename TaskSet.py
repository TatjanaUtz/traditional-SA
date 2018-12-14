"""Representation of a taskset."""

import operator


class TaskSet:
    """Representation of a TaskSet.

    A taskset is a set of different tasks.
    """

    # Constructor
    def __init__(self, id=None, tasks=[], exit_value=None):
        """Constructor: initialize a taskset from a list of tasks."""
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
        """Represent taskset as string."""
        s = "Set_ID = " + str(self.id) + ", Tasks: "
        s += str([str(task) for task in self._tasks])
        s += ", Exit_Value = " + str(self.exit_value)
        return s

    # Add a task
    def addTask(self, task):
        """Add a new task to the taskset."""
        self._tasks.append(task)  # Add task to taskset
        self._task_counter += 1  # Raise task counter
        self.sort()  # Sort tasks according to increasing priorities

    # Length of taskset
    def __len__(self):
        """Get length of Taskset = number of tasks."""
        return self._task_counter

    # Iterator
    def __iter__(self):
        """Iterate over all tasks."""
        return self._tasks.__iter__()

    # Index
    def __getitem__(self, index):
        """Get task at index."""
        return self._tasks[index]

    # Sort taskset
    def sort(self):
        """Sort the taskset.

        The taskset is sorted according to the task priorities in increasing order.
        """
        self._tasks.sort(key=operator.attrgetter('priority'))
