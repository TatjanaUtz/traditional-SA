"""Main file of project.

Run this file for traditional schedulability analysis.
"""

import argparse
import logging
import time

import RTA
import database as db
import simulation
import utilization
import workload
from Taskset import Taskset

# valid schedulability analysis tests, that are currently implemented
valid_SA = [simulation.simulate,  # Simulation
            utilization.basic_utilization_test,  # Basic utilization test for FP and EDF
            utilization.rm_utilization_test,  # Utilization test for RM
            utilization.hb_utilization_test,  # Utilization test with Hyperbolic Bound
            RTA.rta_audsley,  # RTA according to Audsley
            RTA.rta_buttazzo,  # RTA according to Buttazzo
            workload.rm_workload_test,  # Workload test for RM
            workload.het_workload_test]  # HET workload test

# Select if the results should be printed to a file (True) or not (False)
output_to_file = True

# Name of the output file for results
file_name = "results_after_correcting"


def start_logging():
    """Create and initialize logging.

    Error messages are logged to the 'error.log' file.
    Info and debug messages are logged to the console.
    """
    # create logger with 'main'
    logger = logging.getLogger('traditional-SA')
    logger.setLevel(logging.INFO)

    # create file handler which logs error messages
    fh = logging.FileHandler('error.log', mode='w+')
    fh.setLevel(logging.ERROR)

    # create console handler with a lower log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # return logger
    return logger


def print_results(test_name, tp, fp, tn, fn, other):
    """Print results of a schedulability analysis method.

    Overview of the results of a schedulability test is printed.

    Args:
        test_name - name of the schedulability analysis method
        tp - true positive results
        fp - false positive reults
        tn - true negative results
        fn - false negative results
        other - not assignable results
    """
    # create logger
    logger = logging.getLogger('traditional-SA.main.print_results')

    sum = tp + fp + tn + fn  # sum of correct and incorrect results
    correct = tp + tn  # number of correct results
    incorrect = fp + fn  # number of incorrect results

    # Print results to a file
    if output_to_file is True:
        f = open(file_name, 'a+')
        f.write("\n")
        s = "---------- Results of " + test_name + " ----------"
        f.write(s + "\n")
        f.write("Correct results: {0:d} / {1:d} = {2:0.2f}% \n".format(correct, sum,
                                                                       correct * 100 / sum))
        f.write("Incorrect results: {0:d}/ {1:d} = {2:.2f}% \n".format(incorrect, sum,
                                                                       incorrect * 100 / sum))
        f.write("True positive results (tp) = {0:d} = {1:.2f}% \n".format(tp, tp * 100 / sum))
        f.write("False positive results (fp) = {0:d} = {1:.2f}% \n".format(fp, fp * 100 / sum))
        f.write("True negative results (tn) = {0:d} = {1:.2f}% \n".format(tn, tn * 100 / sum))
        f.write("False negative results (fn) = {0:d} = {1:.2f}% \n".format(fn, fn * 100 / sum))
        f.write("Other results = {0:d} \n".format(other))
        f.write("-" * len(s) + "\n")

    # Print results to console
    s = "---------- Results of " + test_name + " ----------"
    logger.info(s)
    logger.info("\t Correct results: {0:d} / {1:d} = {2:0.2f}%".format(correct, sum,
                                                                       correct * 100 / sum))
    logger.info(
        "\t Incorrect results: {0:d}/ {1:d} = {2:.2f}%".format(incorrect, sum,
                                                               incorrect * 100 / sum))
    logger.info("\t True positive results (tp) = {0:d} = {1:.2f}%".format(tp, tp * 100 / sum))
    logger.info("\t False positive results (fp) = {0:d} = {1:.2f}%".format(fp, fp * 100 / sum))
    logger.info("\t True negative results (tn) = {0:d} = {1:.2f}%".format(tn, tn * 100 / sum))
    logger.info("\t False negative results (fn) = {0:d} = {1:.2f}%".format(fn, fn * 100 / sum))
    logger.info("\t Other results = {0:d}".format(other))
    logger.info("-" * len(s))


def test_dataset(dataset, function):
    """Test a complete dataset with the given schedulability analysis method.

    Args:
        dataset - the dataset that should be analyzed
        function - the schedulability analysis method
    Return:
        -1 if an error occured
    """
    # create logger
    logger = logging.getLogger('traditional-SA.main.test_dataset')

    # Check input arguments
    if not isinstance(dataset, list):  # Check if dataset ia a list
        logger.error("Invalid dataset! Dataset must be a list!\n")
        return -1
    if not all(isinstance(item, Taskset) for item in dataset):  # Check if all items are tasksets
        logger.error("Invalid dataset! Dataset must contain tasksets!\n")
        return -1
    if function not in valid_SA:  # invalid SA function
        logger.error("Invalid schedulability analysis method!\n")
        return -1

    # Get number of task-sets in the dataset
    num_tasksets = len(dataset)

    # Variables for printing results of SA
    tp, fp, tn, fn, others = 0, 0, 0, 0, 0

    # Iterate over all task-sets and check schedulability
    for i in range(num_tasksets):
        taskset = dataset[i]
        schedulability = function(taskset)

        # Compare SA result with real result
        real_result = taskset.result
        if schedulability is True and real_result == 1:  # SA is true positive
            tp += 1
        elif schedulability is True and real_result == 0:  # SA is false positive
            fp += 1
        elif schedulability is False and real_result == 1:  # SA is false negative
            fn += 1
        elif schedulability is False and real_result == 0:  # SA is true negative
            tn += 1
        else:  # no valid combination
            others += 1

    # Print results of simulation
    print_results(function.__name__, tp, fp, tn, fn, others)


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
        tests_todo = valid_SA
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
            tests_todo.append(RTA.rta_audsley)
            tests_todo.append(RTA.rta_buttazzo)

        if args.workload:  # run workload tests
            logger.info("Doing workload tests...\n")

            # Add the corresponding tests to the to-do list
            tests_todo.append(workload.workload_test)
            tests_todo.append(workload.rm_workload_test)

    if len(tests_todo) == 0:
        logger.info("Doing nothing...\n")
        return None
    else:
        return tests_todo


def main():
    """Main function of project."""

    # Create and initialize logger
    logger = start_logging()

    # Create file if results should be written to file
    if output_to_file is True:
        f = open(file_name, 'w+')
        f.close()

    # Read the tests that should be performed (defined by command line arguments)
    test_todo = read_input()

    if test_todo is not None:  # at least one test should be done
        logger.info("Tests to do: " + str([test.__name__ for test in test_todo]) + "\n")

        # Read task-sets from database
        logger.info("Reading task-sets from the database...")
        start_time = time.time()
        dataset = db.get_dataset()
        end_time = time.time()
        logger.info("Read {} task-sets from the database!".format(len(dataset)))
        logger.info("Time elapsed = {}\n".format(end_time - start_time))

        # Iterate through the to-do list and perform tests
        for test in test_todo:
            start_time = time.time()  # Save start time
            test_dataset(dataset, test)  # Run test
            end_time = time.time()  # Save end time
            logger.info(
                "Time elapsed = {}\n".format(end_time - start_time))  # print elapsed time
            if output_to_file is True:  # print time to file
                f = open(file_name, 'a+')
                f.write("Time elapsed = {}\n".format(end_time - start_time))
                f.close()

    else:  # no test should be performed
        logger.info("Nothing to do...\n")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    # logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    main()
