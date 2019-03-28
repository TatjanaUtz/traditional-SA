"""Main file of project.

Run this file for traditional schedulability analysis.
"""

import logging
import time

import command_line_interface
import logging_config
import rta
import simulation
import utilization
import workload
from database_interface import Taskset
from database_interface import Database

# valid schedulability analysis methods, that are currently implemented
VALID_SA = [simulation.simulate,  # simulation
            utilization.basic_utilization_test,  # basic utilization test
            utilization.rm_utilization_test,  # utilization test for RM
            utilization.hb_utilization_test,  # utilization test with hyperbolic bound
            rta.rta_audsley,  # RTA according to Audsley
            rta.rta_buttazzo,  # RTA according to Buttazzo
            workload.rm_workload_test,  # workload test for RM
            workload.het_workload_test]  # hyperplanes exact test based on workload


def main():
    """Main function."""
    logger = logging_config.init_logging()  # create and initialize logging

    # read and process command line arguments
    db_dir, db_name, tests_todo = command_line_interface.read_input()

    if tests_todo is not None:  # at least one test should be done
        logger.info("Tests to do: %s \n", [test.__name__ for test in tests_todo])

        # load the dataset
        dataset = load_dataset(db_dir, db_name)

        # Iterate through the to-do list and perform tests
        for test in tests_todo:
            test_dataset(dataset, test)


def load_dataset(db_dir, db_name):
    """Load the dataset from the database.

    Args:
        db_dir -- directory of the database
        db_name -- name of the database
    Return:
        dataset --- list with the task-sets of type Taskset
    """
    # create logger
    logger = logging.getLogger('traditional-SA.main.load_dataset')

    # create a database object
    try:
        # TODO: replace with variables
        my_database = Database(db_dir="C:\\Users\\tatjana.utz\\PycharmProjects\\Datenbanken",
                               db_name="panda_v3.db")
    except Exception as exc:
        logger.error("Could not create database object: %s", format(exc))
        return

    logger.info("Reading task-sets from the database...")
    start_time = time.time()

    # read table 'TaskSet'
    dataset = my_database.read_table_taskset()

    end_time = time.time()
    logger.info("Read %d task-sets from the database!", len(dataset))
    logger.info("Time elapsed = %f\n", end_time - start_time)

    return dataset


def test_dataset(dataset, function):
    """Test a complete dataset with the given schedulability analysis method.

    Args:
        dataset - the dataset that should be analyzed
        function - the schedulability analysis method
    """
    start_time = time.time()

    # create logger
    logger = logging.getLogger('traditional-SA.main.test_dataset')

    # Check input arguments
    if not isinstance(dataset, list):  # Check if dataset ia a list
        raise ValueError("Invalid dataset! Dataset must be a list!\n")
    if not all(isinstance(item, Taskset) for item in dataset):  # Check if all items are tasksets
        raise ValueError("Invalid dataset! Dataset must contain tasksets!\n")
    if function not in VALID_SA:  # invalid SA function
        raise ValueError("Invalid schedulability analysis method!\n")

    # Get number of task-sets in the dataset
    num_tasksets = len(dataset)

    # Variables for printing results of SA
    true_positive, false_positive, true_negative, false_negative, others = 0, 0, 0, 0, 0

    # Iterate over all task-sets and check schedulability
    for i in range(num_tasksets):
        taskset = dataset[i]
        schedulability = function(taskset)

        # Compare SA result with real result
        real_result = taskset.result
        if schedulability is True and real_result == 1:  # SA is true positive
            true_positive += 1
        elif schedulability is True and real_result == 0:  # SA is false positive
            false_positive += 1
        elif schedulability is False and real_result == 1:  # SA is false negative
            false_negative += 1
        elif schedulability is False and real_result == 0:  # SA is true negative
            true_negative += 1
        else:  # no valid combination
            others += 1

    end_time = time.time()

    # Print results of simulation
    logging_config.print_results(function.__name__,
                                 [true_positive, false_positive, true_negative, false_negative,
                                  others])

    # log elapsed time
    log_file = open(logging_config.LOG_FILE_NAME, 'a+')
    log_file.write("Time elapsed = {}\n".format(end_time - start_time))
    log_file.close()


if __name__ == "__main__":
    main()
