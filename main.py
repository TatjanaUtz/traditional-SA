"""Main file of project 'traditional-SA'.

Run the main method of this file for traditional schedulability analysis.
"""

import time

import command_line_interface
import logging_config
import logging
import rta
import simulation
import utilization
import workload
from database_interface import Database

# valid schedulability analysis methods, that are currently implemented
VALID_SA = [simulation.simulate,  # simulation
            utilization.basic_utilization_test,  # basic utilization test
            utilization.rm_utilization_test,  # utilization test for RM
            utilization.hb_utilization_test,  # utilization test with hyperbolic bound
            rta.rta_audsley,  # RTA according to Audsley
            rta.rta_buttazzo,  # RTA according to Buttazzo
            workload.rm_workload_test,  # workload test for RM
            workload.het_workload_test  # hyperplanes exact test based on workload
            ]


def main():
    """Main function of project 'traditional-SA'."""
    # read and process command line arguments
    db_dir, db_name, tests_todo = command_line_interface.read_input()

    # create and initialize logger
    logger = logging_config.init_logging(db_name)

    if tests_todo is not None:  # at least one test should be done
        logger.info("Tests to do: %s \n", [test.__name__ for test in tests_todo])

        # load the dataset
        dataset = load_dataset(db_dir, db_name)

        for test in tests_todo:  # iterate through the to-do list
            results = test_dataset(dataset, test)  # perform test
            logging_config.log_results(test.__name__, results)  # log results


def load_dataset(db_dir, db_name):
    """Load the dataset from the database.

    Args:
        db_dir -- directory of the database
        db_name -- name of the database
    Return:
        dataset --- list of Taskset-objects
    """
    logger = logging.getLogger('traditional-SA.main.load_dataset')

    # try to create a Database-object
    try:
        my_database = Database(db_dir=db_dir, db_name=db_name)
    except ValueError as val_err:
        logger.error("Could not create Database-object: %s", val_err)
        return None

    # read the data-set from the database
    logger.info("Reading task-sets from the database...")
    start_time = time.time()
    dataset = my_database.read_table_taskset()  # read table 'TaskSet'
    end_time = time.time()
    logger.info("Read %d task-sets from the database.", len(dataset))
    logger.info("Time elapsed: %f \n", end_time - start_time)

    return dataset


def test_dataset(dataset, function):
    """Test the data-set with the given schedulability analysis method.

    Args:
        dataset -- the data-set that should be analyzed
        function -- the schedulability analysis method
    Return:
        result_dict -- dictionary with the result of the schedulability analysis method
    """
    # variables for results of schedulability analysis
    true_positive, false_positive, true_negative, false_negative = 0, 0, 0, 0

    # test the data-set with the schedulability analysis method
    start_time = time.time()
    for taskset in dataset:  # iterate over all task-sets
        schedulability = function(taskset)  # check schedulability of task-set
        real_result = taskset.result  # real result of the task-set

        # compare test result with real result
        if schedulability is True and real_result == 1:  # true positive
            true_positive += 1
        elif schedulability is True and real_result == 0:  # false positive
            false_positive += 1
        elif schedulability is False and real_result == 1:  # false negative
            false_negative += 1
        elif schedulability is False and real_result == 0:  # true negative
            true_negative += 1
    end_time = time.time()

    # create dictionary with the result of the test
    result_dict = {'tp': true_positive, 'fp': false_positive, 'tn': true_negative,
                   'fn': false_negative, 'time': end_time - start_time}

    return result_dict


if __name__ == "__main__":
    main()
