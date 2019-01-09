"""Main file of project."""

import logging
import time

import RTA
import new_database as db
import simulation
import utilization

valid_SA = [simulation.simulate, utilization.basic_utilization_test,
            utilization.rm_utilization_test,
            utilization.hb_utilization_test,
            "RTA_audsley", "RTA_buttazzo", RTA.cpa]


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
    s = "---------- Results of " + test_name + " ----------"
    print(s)
    print("Correct results: {0:d} / {1:d} = {2:.0f}%".format(correct, sum, correct * 100 / sum))
    print(
        "Incorrect results: {0:d}/ {1:d} = {2:.0f}%".format(incorrect, sum, incorrect * 100 / sum))
    print("True positive results (tp) = {0:d}".format(tp))
    print("False positive results (fp) = {0:d}".format(fp))
    print("True negative results (tn) = {0:d}".format(tn))
    print("False negative results (fn) = {0:d}".format(fn))
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
    print_results(str(function), tp, fp, tn, fn, others)


def main():
    """Main function of project."""

    # --- Read task-sets from database ---
    print("Reading task-sets from the database...")
    start_time = time.time()
    dataset = db.get_dataset()
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    # --- Simulation ---
    start_time = time.time()
    test_dataset(dataset, simulation.simulate)
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    # --- Utilization Tests ---
    # start_time = time.time()
    # test_dataset(dataset, utilization.basic_utilization_test)
    # # utilization.test_dataset(dataset, "basic_utilization_test")
    # end_time = time.time()
    # print("Time elapsed = ", end_time - start_time)

    # start_time = time.time()
    # utilization.test_dataset(dataset, "RM_utilization_test")
    # end_time = time.time()
    # print("Time elapsed = ", end_time - start_time)
    #
    # start_time = time.time()
    # utilization.test_dataset(dataset, "HB_utilization_test")
    # end_time = time.time()
    # print("Time elapsed = ", end_time - start_time)

    # --- Response Time Analysis ---
    # start_time = time.time()
    # RTA.test_dataset(dataset, "Audsley")
    # end_time = time.time()
    # print("Time elapsed = ", end_time - start_time)
    #
    # start_time = time.time()
    # RTA.test_dataset(dataset, "Buttazzo")
    # end_time = time.time()
    # print("Time elapsed = ", end_time - start_time)
    #
    # start_time = time.time()
    # RTA.test_dataset(dataset, "CPA")
    # end_time = time.time()
    # print("Time elapsed = ", end_time - start_time)


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

    main()
