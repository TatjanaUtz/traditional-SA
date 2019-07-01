"""Module for different testing scenarios."""
import logging
import os

import simsogui
import time

from database_interface import Database
from rta import rta_audsley, rta_buttazzo
from simulation import simulate
from utilization import basic_utilization_test, rm_utilization_test, hb_utilization_test
from workload import rm_workload_test, het_workload_test


def test_schedulability_test():
    """Main function for testing of single schedulability tests."""
    my_database = Database(os.getcwd(), "panda_v3.db")

    taskset_46429 = my_database.read_table_taskset(taskset_id=46429)[0]

    print("----- Simulation -----")
    start_t = time.time()
    result = simulate(taskset_46429)
    end_t = time.time()
    print("Result: %r -- Time elapsed: %f s" % (result, end_t - start_t))

    print("----- Basic Utilization -----")
    start_t = time.time()
    result = basic_utilization_test(taskset_46429)
    end_t = time.time()
    print("Result: %r -- Time elapsed: %f s" % (result, end_t - start_t))

    print("----- RM Utilization -----")
    start_t = time.time()
    result = rm_utilization_test(taskset_46429)
    end_t = time.time()
    print("Result: %r -- Time elapsed: %f s" % (result, end_t - start_t))

    print("----- HB Utilization -----")
    start_t = time.time()
    result = hb_utilization_test(taskset_46429)
    end_t = time.time()
    print("Result: %r -- Time elapsed: %f s" % (result, end_t - start_t))

    print("----- RTA Audsley -----")
    start_t = time.time()
    result = rta_audsley(taskset_46429)
    end_t = time.time()
    print("Result: %r -- Time elapsed: %f s" % (result, end_t - start_t))

    print("----- RTA Buttazzo -----")
    start_t = time.time()
    result = rta_buttazzo(taskset_46429)
    end_t = time.time()
    print("Result: %r -- Time elapsed: %f s" % (result, end_t - start_t))

    print("----- RM Workload -----")
    start_t = time.time()
    result = rm_workload_test(taskset_46429)
    end_t = time.time()
    print("Result: %r -- Time elapsed: %f s" % (result, end_t - start_t))

    print("----- HET Workload -----")
    start_t = time.time()
    result = het_workload_test(taskset_46429)
    end_t = time.time()
    print("Result: %r -- Time elapsed: %f s" % (result, end_t - start_t))


def start_simso():
    """Start SimSo GUI."""
    simsogui.run_gui()


def time_per_taskset():
    # load the dataset
    my_database = Database(os.getcwd(), "panda_v3.db")
    dataset = my_database.read_table_taskset()

    # create empty list for times
    times = []

    for taskset in dataset:  # iterate over all task-sets
        # do schedulability analysis
        start_t = time.time()
        simulate(taskset)
        end_t = time.time()

        # add time
        times.append(end_t - start_t)

    # calculate average time
    average_t = sum(times) / len(times)
    print("SIMULATION -- Average time per task-set: %f s" % (average_t))


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    # start_simso()
    test_schedulability_test()

    # start SimSo GUI
    start_simso()
