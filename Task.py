""" Model of a task. """

numberOfProperties = 8


class Task:
    """Representation of a Task as class."""
    numberOfProperties = 8

    def __init__(self, priority=0, deadline=0, quota='0', pkg='0', arg=0, period=0, numberOfJobs=0, offset=0):
        """Constructor of class Task. Initialize all variables."""
        self.priority = priority
        self.deadline = deadline
        self.quota = quota
        self.pkg = pkg
        self.arg = arg
        self.period = period
        self.numberOfJobs = numberOfJobs
        self.offset = offset

    # String representation
    def __str__(self):
        """String representation of a Task."""
        s = [self.priority, self.deadline, self.quota, self.pkg, self.arg, self.period, self.numberOfJobs, self.offset]
        return str(s)

    # Getter
    def getPriority(self):
        return self.priority

    def getDeadline(self):
        return self.deadline

    def getQuota(self):
        return self.quota

    def getPkg(self):
        return self.pkg

    def getArg(self):
        return self.arg

    def getPeriod(self):
        return self.period

    def getNumberOfJobs(self):
        return self.getNumberOfJobs

    def getOffset(self):
        return self.offset
