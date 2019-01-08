"""Simulation of a task"""

import logging
from functools import reduce

from simso.configuration import Configuration
from simso.core import Model


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


def main():
    # Manual configuration
    # The configuration class stores all the details about a system.
    configuration = Configuration()

    # Add property "priority" of type int to tasks
    configuration.task_data_fields['priority'] = 'int'

    # Calculate the hyperperiod
    H = _lcm([7000, 5000, 5000])

    # Calculate activation dates
    activation_dates = []
    activation_dates.append(_get_activation_dates(H, 7000, 3))
    activation_dates.append(_get_activation_dates(H, 5000, 7))
    activation_dates.append(_get_activation_dates(H, 5000, 8))

    # Add tasks to the list of tasks
    configuration.add_task(name="T1", identifier=1, period=7000, wcet=1070, deadline=6500,
                           list_activation_dates=activation_dates[0])
    configuration.task_info_list[0].data['priority'] = int(2)
    configuration.add_task(name="T2", identifier=2, period=5000, wcet=1070, deadline=4500,
                           list_activation_dates=activation_dates[1])
    configuration.task_info_list[1].data['priority'] = int(2)
    configuration.add_task(name="T3", identifier=3, period=5000, wcet=1712, deadline=4500,
                           list_activation_dates=activation_dates[2])
    configuration.task_info_list[2].data['priority'] = int(2)

    # Get the hyperperiod of the tasks: H = lcm(T1, ..., Tn)
    # H = _lcm([x.period for x in configuration.task_info_list])

    # Define length of simulation = H
    # configuration.duration = 420 * configuration.cycles_per_ms
    configuration.duration = H * configuration.cycles_per_ms

    # Add a processor to the list of processors
    configuration.add_processor(name="CPU 1", identifier=1)

    # Add a scheduler
    # configuration.scheduler_info.filename = "fp_edf_scheduler.py"  # use a custom scheduler
    configuration.scheduler_info.clas = "simso.schedulers.FP"  # use a scheduler embedded with SimSo

    # Check the correctness of the configuration (without simulating it) before trying to run it
    configuration.check_all()

    # Init a model from the configuration
    model = Model(configuration)

    # Execute the simulation
    model.run_model()

    # Print logs
    # for log in model.logs:
    #     print(log)

    # Print the computation time of the jobs
    for task in model.results.tasks:
        print(task.name + ":")
        for job in task.jobs:
            print("{0:s} {1:.3f} ms".format(job.name, job.computation_time))

    # Print number of preemptions per task
    # for task in model.results.tasks.values():
    #     print("{0:s} {1:d}".format(task.name, task.preemption_count))


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


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

    main()
    import simsogui

    simsogui.run_gui()
