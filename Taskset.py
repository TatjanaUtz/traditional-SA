"""Definition of class Taskset."""
import operator

from Task import Task


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
