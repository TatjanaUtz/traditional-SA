"""Main file of project.

Run this file for traditional schedulability analysis.
"""

import logging
import time

import rta
import simulation
import utilization
import workload
from Taskset import Taskset
from database_interface import Database
import command_parser

import logging_config

# valid schedulability analysis tests, that are currently implemented
VALID_SA = [simulation.simulate,  # Simulation
            utilization.basic_utilization_test,  # Basic utilization test for FP and EDF
            utilization.rm_utilization_test,  # Utilization test for RM
            utilization.hb_utilization_test,  # Utilization test with Hyperbolic Bound
            rta.rta_audsley,  # RTA according to Audsley
            rta.rta_buttazzo,  # RTA according to Buttazzo
            workload.rm_workload_test,  # Workload test for RM
            workload.het_workload_test]  # HET workload test


def test_dataset(dataset, function):
    """Test a complete dataset with the given schedulability analysis method.

    Args:
        dataset - the dataset that should be analyzed
        function - the schedulability analysis method
    """
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

    # Print results of simulation
    logging_config.print_results(function.__name__,
                  [true_positive, false_positive, true_negative, false_negative, others])




def main():
    """Main function of project."""

    # Create and initialize logger
    logger = logging_config.init_logging()

    # Read the tests that should be performed (defined by command line arguments)
    tests_todo = command_parser.read_input()

    if tests_todo is not None:  # at least one test should be done
        logger.info("Tests to do: %s \n", [test.__name__ for test in tests_todo])

        # Create a database object
        try:
            my_database = Database()
        except Exception as exc:
            logger.error('Could not create database object: {}'.format(exc))
            return

        # Read task-sets from database
        logger.info("Reading task-sets from the database...")
        start_time = time.time()
        dataset = my_database.get_dataset()
        end_time = time.time()
        logger.info("Read %d task-sets from the database!", len(dataset))
        logger.info("Time elapsed = %f\n", end_time - start_time)

        # Iterate through the to-do list and perform tests
        for test in tests_todo:
            start_time = time.time()  # Save start time
            test_dataset(dataset, test)  # Run test
            end_time = time.time()  # Save end time
            logger.info("Time elapsed = %f\n", end_time - start_time)  # print elapsed time

            log_file = open(logging_config.LOG_FILE_NAME, 'a+')
            log_file.write("Time elapsed = {}\n".format(end_time - start_time))
            log_file.close()

    else:  # no test should be performed
        logger.info("Nothing to do...\n")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main()