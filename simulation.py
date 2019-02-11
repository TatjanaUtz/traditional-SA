"""Simulation of a task"""

import logging
from functools import reduce

from simso.configuration import Configuration
from simso.core import Model

from Taskset import Taskset


def simulate(taskset):
    """Simulation.

    This method executes the simulation of a task-set. The simulation is run over the hyperperiod, which
    is the least common mean of all task periods. The task-set is schedulable if all jobs of all tasks
    in the hyperperiod can meet their deadlines.

    Args:
        taskset - the task-set that should be analyzed
    Return:
        True - the task-set is schedulable
        False - the task-set is not schedulable
        -1 - an error occured
    """
    # create logger
    logger = logging.getLogger('traditional-SA.simulation.simulate')

    # Check input argument
    if taskset is None or not isinstance(taskset, Taskset):
        logger.error("Invalid input argument or no task-set given!")
        return -1

    # Manual configuration: the configuration class stores all the details about a system
    configuration = Configuration()

    # Get the periods of the tasks
    periods = []
    for task in taskset:
        if task.period not in periods:
            periods.append(task.period)

    # Calculate the hyperperiod of the tasks
    H = _lcm(periods)
    logger.debug("simulation.py/simulate(): Hyperperiod H = " + str(H))

    # Define the length of simulation (= H)
    configuration.duration = H * configuration.cycles_per_ms

    # Add a property 'priority' to the task data fields
    configuration.task_data_fields['priority'] = 'int'  # 'priority' is of type int

    # Add the tasks to the list of tasks
    i = 1
    for task in taskset:
        task_name = "T" + str(task.id)
        activation_dates = _get_activation_dates(H, task.period, task.number_of_jobs)
        configuration.add_task(name=task_name, identifier=i, task_type="Sporadic",
                               period=task.period, activation_date=0, wcet=task.execution_time,
                               deadline=task.deadline, list_activation_dates=activation_dates,
                               data={'priority': task.priority})
        i += 1

    # Add a processor to the list of processors
    configuration.add_processor(name="CPU1", identifier=1)

    # Add a scheduler:
    configuration.scheduler_info.filename = "fp_edf_scheduler.py"  # use a custom scheduler
    # configuration.scheduler_info.clas="simso.schedulers.RM"   # use a scheduler embedded with SimSo

    # Check the correctness of the configuration (without simulating it) before trying to run it
    configuration.check_all()

    # Init a model from the configuration
    model = Model(configuration)

    # Execute the simulation
    model.run_model()

    # Schedulability analysis: check for deadline miss of each job of every task
    for task in model.results.tasks:
        # print(task.name + ":")
        for job in task.jobs:
            if job.exceeded_deadline:  # deadline miss
                logger.debug("simulation.py/simulate(): {0:s} Deadline miss".format(job.name))
                return False

    return True


def _get_activation_dates(H, T, number_of_jobs):
    """Determine all activation dates of a task.

    This method calculates the activation dates of a task according to the three input arguments.

    Args:
        H - the hyperperiod
        T - the period of the task
        number_of_jobs - number of the jobs = how often should the task be activated
    Return:
        list of activation dates
    """
    activation_dates = []  # create empty list
    current_activation_date = 0  # initialize current activation date
    while current_activation_date <= H and len(activation_dates) < number_of_jobs:
        if current_activation_date not in activation_dates:
            activation_dates.append(current_activation_date)
        current_activation_date += T

    return activation_dates


def _lcm(numbers):
    """Calculate the least common multiple.

    This function calculates the least common multiple (LCM) of a list of numbers.

    Args:
        number_list - list with the numbers
    Return:
        the least common multiple of the numbers in the given list
    """
    return reduce(lcm, numbers, 1)


def lcm(a, b):
    """Calculate the least common multiple.

    This function calculates the least common multiple (LCM) of two numbers a, b.

    Args:
        a, b - numbers for which the LCM should be calculated
    Return:
        the least common multiple of a and b
    """
    return (a * b) // _gcd(a, b)


def _gcd(*numbers):
    """ Calculate the greatest common divisor.

    This function calculates the greatest common divisor (GCD).

    Args:
        numbers - list with integers, for which the GCD should be calcualated
    Return:
        the greatest common divisor
    """
    from math import gcd
    return reduce(gcd, numbers)
