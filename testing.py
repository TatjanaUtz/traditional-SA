"""Module for different testing scenarios."""
import logging

import simsogui

from database_interface import Database
from workload import rm_workload_test


def test_schedulability_test():
    """Main function for testing of single schedulability tests."""
    my_database = Database()
    taskset_46429 = my_database.read_table_taskset(taskset_id=46429)
    taskset_563782 = my_database.read_table_taskset(taskset_id=563782)


def start_simso():
    """Start SimSo GUI."""
    simsogui.run_gui()


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    test_schedulability_test()
