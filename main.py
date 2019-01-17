"""Main file of project."""

import argparse
import logging
import time

import RTA
import new_database as db
import simulation
import utilization
import workload
from Taskset import Taskset

valid_SA = [simulation.simulate, utilization.basic_utilization_test,
            utilization.rm_utilization_test, utilization.hb_utilization_test, RTA.rta_audsley,
            RTA.rta_buttazzo, workload.workload_test, workload.workload_test_LSD]


def print_results(test_name, tp, fp, tn, fn, other):
    """Print results of a schedulability analysis method.

    Args:
        test_name - name of the schedulability analysis method
        tp - true positive results
        fp - false positive reults
        tn - true negative results
        fn - false negative results
        other - not assignable results
    """
    sum = tp + fp + tn + fn  # sum of correct and incorrect results
    correct = tp + tn  # number of correct results
    incorrect = fp + fn  # number of incorrect results
    print("\n")
    s = "---------- Results of " + test_name + " ----------"
    print(s)
    print("Correct results: {0:d} / {1:d} = {2:.0f}%".format(correct, sum, correct * 100 / sum))
    print(
        "Incorrect results: {0:d}/ {1:d} = {2:.0f}%".format(incorrect, sum, incorrect * 100 / sum))
    print("True positive results (tp) = {0:d} = {1:.0f}%".format(tp, tp*100/sum))
    print("False positive results (fp) = {0:d} = {1:.0f}%".format(fp, fp*100/sum))
    print("True negative results (tn) = {0:d} = {1:.0f}%".format(tn, tn*100/sum))
    print("False negative results (fn) = {0:d} = {1:.0f}%".format(fn, fn*100/sum))
    print("Other results = {0:d}".format(other))
    print("-" * len(s))


def test_dataset(dataset, function):
    """Test a complete dataset with a schedulability analysis method.

    Args:
        dataset - the dataset that should be analyzed
        function - the sche3dulability analysis method
    Return:
        -1 if an error occured
    """
    # Check input arguments
    if not isinstance(dataset, list):  # Check if dataset ia a list
        logging.error("main.py/test_dataset(): Invalid dataset! Dataset must be a list!")
        return -1
    if not all(isinstance(item, Taskset) for item in dataset):  # Check if all items are tasksets
        logging.error("main.py/test_dataset(): Invalid dataset! Dataset must contain tasksets!")
        return -1
    if function not in valid_SA:  # invalid SA function
        logging.error("main.py/test_dataset(): Invalid schedulability analysis method!")
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
        print("Testing all...")
        tests_todo = valid_SA
    else:
        if args.simulation:  # run simulation
            print("Simulating...")

            # Add simulation to the to-do list
            tests_todo.append(simulation.simulate)

        if args.utilization:  # run utilization tests
            print("Doing utiliziaton tests...")

            # Add the corresponding tests to the to-do list
            tests_todo.append(utilization.basic_utilization_test)
            tests_todo.append(utilization.rm_utilization_test)
            tests_todo.append(utilization.hb_utilization_test)

        if args.response_time_analysis:  # run response time analysis
            print("Doing response time analyis...")

            # Add the corresponding tests to the to-do list
            tests_todo.append(RTA.rta_audsley)
            tests_todo.append(RTA.rta_buttazzo)

        if args.workload:  # run workload tests
            print("Doing workload tests...")

            # Add the corresponding tests to the to-do list
            tests_todo.append(workload.workload_test)
            tests_todo.append(workload.workload_test_LSD)

    if len(tests_todo) == 0:
        print("Doing nothing...")
        return None
    else:
        return tests_todo


def main():
    """Main function of project."""

    # Read the tests that should be performed (defined by command line arguments)
    test_todo = read_input()

    if test_todo is not None:  # at least one test should be done
        print("Tests to do: " + str([test.__name__ for test in test_todo]))

        # Read task-sets from database
        print("Reading task-sets from the database...")
        start_time = time.time()
        dataset = db.get_dataset()
        end_time = time.time()
        print("Read {} task-sets from the database!".format(len(dataset)))
        print("Time elapsed = ", end_time - start_time)

        # Iterate through the to-do list and perform tests
        for test in test_todo:
            start_time = time.time()  # Save start time
            test_dataset(dataset, test)  # Run test
            end_time = time.time()  # Save end time
            print("Time elapsed = ", end_time - start_time)  # print elapsed time

    else:  # no test should be performed
        print("Nothing to do...")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

    main()
