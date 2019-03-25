"""Main file of project.

Run this file for traditional schedulability analysis.
"""

import argparse
import logging
import time

import rta
import simulation
import utilization
import workload
from Taskset import Taskset
from database_interface import Database

# valid schedulability analysis tests, that are currently implemented
VALID_SA = [simulation.simulate,  # Simulation
            utilization.basic_utilization_test,  # Basic utilization test for FP and EDF
            utilization.rm_utilization_test,  # Utilization test for RM
            utilization.hb_utilization_test,  # Utilization test with Hyperbolic Bound
            rta.rta_audsley,  # RTA according to Audsley
            rta.rta_buttazzo,  # RTA according to Buttazzo
            workload.rm_workload_test,  # Workload test for RM
            workload.het_workload_test]  # HET workload test

# Name of the output file for results
LOG_FILE_NAME = "final_results.log"


def start_logging():
    """Create and initialize logging.

    Error messages are logged to the 'error.log' file.
    Info and debug messages are logged to the console.
    """
    # create logger for 'traditional-SA# project
    logger = logging.getLogger('traditional-SA')
    logger.setLevel(logging.INFO)

    # create file handler which logs error messages
    log_file_handler = logging.FileHandler('error.log', mode='w+')
    log_file_handler.setLevel(logging.ERROR)

    # create console handler with a lower log level
    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_handler.setFormatter(formatter)
    log_console_handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(log_file_handler)
    logger.addHandler(log_console_handler)

    # Create file to which results should be written to
    log_file = open(LOG_FILE_NAME, 'w+')
    log_file.close()


    # return logger
    return logger


def print_results(test_name, results):
    """Print results of a schedulability analysis method.

    Overview of the results of a schedulability test is printed.

    Args:
        test_name - name of the schedulability analysis method
        results -- list of results:
            [0] -- true positive results
            [1] -- false positive reults
            [2] -- true negative results
            [3] -- false negative results
            [4] -- not assignable (other) results
    """
    # create logger
    logger = logging.getLogger('traditional-SA.main.print_results')

    # check input arguments
    if not isinstance(test_name, str):  # invalid argument for test_name
        logger.error("Invalid argument for test_name (must be string)!")
        return
    if not isinstance(results, list):  # invalid argument for results
        logger.error("Invalid argument for results (must be list)!")
        return
    if len(results) < 5:  # to less results are given
        logger.error("Invalid argument for results: must be a list containing "
                     "[true_positives, false_positives, true_negatives, false_negatives, other]!}")
        return

    sum_results = sum(results[:4])  # sum of correct and incorrect results
    correct = results[0] + results[2]  # number of correct results
    incorrect = results[1] + results[3]  # number of incorrect results

    # Print results to a file
    log_file = open(LOG_FILE_NAME, 'a+')
    log_file.write("\n")
    result_title_string = "---------- Results of " + test_name + " ----------"
    log_file.write(result_title_string + "\n")
    log_file.write("Correct results: {0:d} / {1:d} = {2:0.2f}% \n"
                   .format(correct, sum_results, correct * 100 / sum_results))
    log_file.write("Incorrect results: {0:d}/ {1:d} = {2:.2f}% \n"
                   .format(incorrect, sum_results, incorrect * 100 / sum_results))
    log_file.write("True positive results (tp) = {0:d} = {1:.2f}% \n"
                   .format(results[0], results[0] * 100 / sum_results))
    log_file.write("False positive results (fp) = {0:d} = {1:.2f}% \n"
                   .format(results[1], results[1] * 100 / sum_results))
    log_file.write("True negative results (tn) = {0:d} = {1:.2f}% \n"
                   .format(results[2], results[2] * 100 / sum_results))
    log_file.write("False negative results (fn) = {0:d} = {1:.2f}% \n"
                   .format(results[3], results[3] * 100 / sum_results))
    log_file.write("Other results = {0:d} \n".format(results[4]))
    log_file.write("-" * len(result_title_string) + "\n")

    # Print results to console
    result_title_string = "---------- Results of " + test_name + " ----------"
    logger.info(result_title_string)
    logger.info("\t Correct results: {0:d} / {1:d} = {2:0.2f}%"
                .format(correct, sum_results, correct * 100 / sum_results))
    logger.info("\t Incorrect results: {0:d}/ {1:d} = {2:.2f}%"
                .format(incorrect, sum_results, incorrect * 100 / sum_results))
    logger.info("\t True positive results (tp) = {0:d} = {1:.2f}%"
                .format(results[0], results[0] * 100 / sum_results))
    logger.info("\t False positive results (fp) = {0:d} = {1:.2f}%"
                .format(results[1], results[1] * 100 / sum_results))
    logger.info("\t True negative results (tn) = {0:d} = {1:.2f}%"
                .format(results[2], results[2] * 100 / sum_results))
    logger.info("\t False negative results (fn) = {0:d} = {1:.2f}%"
                .format(results[3], results[3] * 100 / sum_results))
    logger.info("\t Other results = {0:d}".format(results[4]))
    logger.info("-" * len(result_title_string))


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
        logger.error("Invalid dataset! Dataset must be a list!\n")
        return
    if not all(isinstance(item, Taskset) for item in dataset):  # Check if all items are tasksets
        logger.error("Invalid dataset! Dataset must contain tasksets!\n")
        return
    if function not in VALID_SA:  # invalid SA function
        logger.error("Invalid schedulability analysis method!\n")
        return

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
    print_results(function.__name__,
                  [true_positive, false_positive, true_negative, false_negative, others])


def read_input():
    """Read input from command line.

    This methods reads the arguments of the script-call.

    Return:
        list with tests that should be done
        None -- no test was selected
    """
    # create logger
    logger = logging.getLogger('traditional-SA.main.read_input')

    # Create argument parser
    parser = argparse.ArgumentParser()

    # Add arguments to the parser
    parser.add_argument("--test_all", help="run all available tests",
                        action="store_true")  # add argument for running all tests
    parser.add_argument("-s", "--simulation", help="run simulation",
                        action="store_true")  # add argument for simulation
    parser.add_argument("-u", "--utilization", help="run utilization tests",
                        action="store_true")  # add argument for utilization tests
    parser.add_argument("-rta", "--response_time_analysis", help="run response time analysis",
                        action="store_true")  # add argument for response time analysis (RTA)
    parser.add_argument("-w", "--workload", help="run workload tests",
                        action="store_true")  # add argument for workload tests

    # Parse arguments
    args = parser.parse_args()

    # Create empty to-do list for tests that should be run
    tests_todo = []

    if args.test_all:  # run all tests
        logger.info("Testing all...\n")
        tests_todo = VALID_SA
    else:
        if args.simulation:  # run simulation
            logger.info("Simulating...\n")

            # Add simulation to the to-do list
            tests_todo.append(simulation.simulate)

        if args.utilization:  # run utilization tests
            logger.info("Doing utiliziaton tests...\n")

            # Add the corresponding tests to the to-do list
            tests_todo.append(utilization.basic_utilization_test)
            tests_todo.append(utilization.rm_utilization_test)
            tests_todo.append(utilization.hb_utilization_test)

        if args.response_time_analysis:  # run response time analysis
            logger.info("Doing response time analyis...\n")

            # Add the corresponding tests to the to-do list
            tests_todo.append(rta.rta_audsley)
            tests_todo.append(rta.rta_buttazzo)

        if args.workload:  # run workload tests
            logger.info("Doing workload tests...\n")

            # Add the corresponding tests to the to-do list
            tests_todo.append(workload.rm_workload_test)
            tests_todo.append(workload.het_workload_test)

    if not tests_todo:  # no test to do
        logger.info("Doing nothing...\n")
        return None

    # at least one test to do
    return tests_todo


def main():
    """Main function of project."""

    # Create and initialize logger
    logger = start_logging()

    # Read the tests that should be performed (defined by command line arguments)
    tests_todo = read_input()

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

            log_file = open(LOG_FILE_NAME, 'a+')
            log_file.write("Time elapsed = {}\n".format(end_time - start_time))
            log_file.close()

    else:  # no test should be performed
        logger.info("Nothing to do...\n")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main()