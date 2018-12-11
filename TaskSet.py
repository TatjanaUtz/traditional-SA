"""Representation of a taskset."""


class TaskSet:
    """Representation of a TaskSet.

    A taskset is a set of different tasks.
    """

    # Constructor
    def __init__(self, tasks=[]):
        """Constructor: initialize a taskset from a list of tasks."""
        self._tasks = []        # Create empty taskset
        self._task_counter = 0  # Set task counter to 0, as taskset is empty
        for t in tasks:         # Iterate over all tasks
            self._tasks.append(t)       # Add task to taskset
            self._task_counter += 1     # Raise task counter

    # String representation
    def __str__(self):
        """Represent taskset as string."""
        return self._tasks.__str__()
