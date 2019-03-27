"""Module for command line parser."""
import logging
import argparse

from main import VALID_SA


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
