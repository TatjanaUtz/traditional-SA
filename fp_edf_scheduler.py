"""Defines the scheduling policy of the Fiasco.OS scheduler.

    The algorithm is the following: a list of ready jobs is kept up-to-date using the on_activate
    and on_terminated methods. When the schedule method is called, the ready job is chosen according
    to the priorities:
    - Tasks can have priority values from 1 ... 127.
    - A priority from 1 ... 126 means, that the task is scheduled according to the fixed priority (FP) algorithm.
    Priority order is:
                        1 - highest priority
                        126 - lowest priority
    - All tasks left with priority 127 are scheduled according to the earliest deadline first (EDF) algorithm.

    Source:
    http://projects.laas.fr/simso/doc/write_scheduler.html
"""

from simso.core import Scheduler  # import scheduler class


class fp_edf_scheduler(Scheduler):  # define fp_edf_scheduler as subclass of scheduler
    """The implementation of a scheduler.

    Subclass of abstract class Scheduler.
    The scheduling events are modeled by method calls which take as arguments the jobs and the processors.
    The init(), on_activate(), on_terminate() and schedule() methods should be redefined in order to interact with the simulation.

    Args:
        sim - Model instance
        scheduler_info - a SchedulerInfo representing the scheduler

    Attributes:
        sim - Model instance, useful to get current time with sim.now_ms() (in ms) or sim.now() (in cycles)
        processors - list of processors handled by this scheduler
        task_list: list of tasks handled by this scheduler
    """

    def init(self):
        """Init method.

        This method is called when the system is ready to run.
        This method is guaranteed to be called when the simulation starts, after the tasks are instantiated.
        The scheduler logic should be initialized here.
        """
        self.read_list = []  # define a empty ready list

    def on_activate(self, job):
        """On_activate method.

        This method is called upon a job activation.

        Args:
            job -   the activated job
        """
        self.read_list.append(job)  # append the job to the ready list
        job.cpu.resched()  # indirectly call the scheduler
        # self.processors[0].resched()   # run the scheduler on the first (and only) processor of the system

    def on_terminated(self, job):
        """On_terminated method.

        This method is called when a job finish (termination or abortion).

        Args:
            job - the job that terminates
        """
        self.read_list.remove(job)  # remove the job from the ready list
        job.cpu.resched()  # indirectly call the scheduler
        # self.processors[0].resched()   # run the scheduler on the first (and only) processor of the system

    def schedule(self, cpu):
        """Schedule method.

        The schedule method is called by the processor (cpu) when it needs to run the scheduler.
        This method takes the scheduling decision.
        This method should not be called directly. A call to the resched method is required.

        Args:
            cpu - the processor on which the scheduler runs
        Return:
            a decision or a list of decisions, a decision is a couple (job, cpu)
        """
        if self.read_list:  # at least one job is ready
            job = min(self.read_list,
                      key=lambda x: x.absolute_deadline)  # select job with the highest priority
        else:  # no job is ready
            job = None

        return (job, cpu)
