"""Module for different testing scenarios."""
import logging

import simsogui

from database import Database
from workload import het_workload_test


def test_schedulability_test():
    """Main function for testing of single schedulability tests."""
    my_database = Database()
    taskset_46429 = my_database.get_taskset(taskset_id=46429)
    print(het_workload_test(taskset_46429))

    taskset_563782 = my_database.get_taskset(taskset_id=563782)
    print(het_workload_test(taskset_563782))


def start_simso():
    """Start SimSo GUI."""
    simsogui.run_gui()


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    test_schedulability_test()
