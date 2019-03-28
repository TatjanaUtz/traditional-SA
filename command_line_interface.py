"""Command-line interface.

Following arguments are neccessary when calling the main-method of the traditional-SA package:
    db_path     path to the database file.
Additional there are optional arguments:
    -h, --help                          show a help message and exit
    --test_all                          run all available schedulability analysis methods
    -s, --simulate                      run simulation
    -u, --utilization                   run all utilization based schedulability analysis methods
    -rta, --response_time_analysis      run all response time analyses
    -w, --workload                      run all workload based schedulability analysis methods
The full call looks like the following:
    main.py [-h] [--test_all] [-s] [-u] [-rta] [-w] db_path
"""
import argparse
import logging
import os

import rta
import simulation
import utilization
import workload
from main import VALID_SA


def read_input():
    """Read arguments from the command line.

    This methods reads the arguments of the script-call from the command line.

    Return:
        db_dir -- directory of the database file
        db_name -- name of the database file
        tests_todo -- list with schedulability tests that should be done
    """
    # create logger
    logger = logging.getLogger('traditional-SA.command_line_interface.read_input')

    # create argument parser
    parser = _create_argparser()

    # parse arguments
    args = parser.parse_args()

    # extract directory and name of the database file
    (db_dir, db_name) = os.path.split(args.db_path)

    # create empty list: schedulability analysis methods that should be done
    tests_todo = []

    # add the selected test to the to-do list
    if args.test_all:  # run all available schedulability analysis methods
        logger.info("Doing all available schedulability tests...\n")
        tests_todo = VALID_SA
    else:
        if args.simulation:  # run simulation
            tests_todo.append(simulation.simulate)

        if args.utilization:  # run all utilization based schedulability analysis methods
            tests_todo.append(utilization.basic_utilization_test)
            tests_todo.append(utilization.rm_utilization_test)
            tests_todo.append(utilization.hb_utilization_test)

        if args.response_time_analysis:  # run all response time analyses
            tests_todo.append(rta.rta_audsley)
            tests_todo.append(rta.rta_buttazzo)

        if args.workload:  # run all workload based schedulability analysis methods
            tests_todo.append(workload.rm_workload_test)
            tests_todo.append(workload.het_workload_test)

    if not tests_todo:  # no schedulability method selected
        logger.info("No schedulability test selected! Doing nothing...\n")
        return None

    return db_dir, db_name, tests_todo


def _create_argparser():
    """Create a parser for command-line options, arguments and sub-commands.

    This method creates an argument parser and adds the neccessary arguments.

    Return:
        parser -- the created argument parser
    """

    # create argument parser
    parser = argparse.ArgumentParser(description="traditional schedulability analysis methods")

    # add positional arguments arguments to the parser
    parser.add_argument("db_path", help="path to the database file")

    # add optional arguments to the parser
    parser.add_argument("--test_all", help="run all available schedulability analysis methods",
                        action="store_true")
    parser.add_argument("-s", "--simulation", help="run simulation", action="store_true")
    parser.add_argument("-u", "--utilization",
                        help="run all utilization based schedulability analysis methods",
                        action="store_true")
    parser.add_argument("-rta", "--response_time_analysis", help="run all response time analyses",
                        action="store_true")
    parser.add_argument("-w", "--workload",
                        help="run all workload based schedulability analysis methods",
                        action="store_true")

    # return argument parser
    return parser
