"""Main file of project."""

import logging
import time

import RTA
import new_database as db
import utilization


def main():
    """Main function of project."""

    # --- Read task-sets from database ---
    print("Reading task-sets from the database...")
    start_time = time.time()
    dataset = db.get_dataset()
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    # --- Utilization Tests ---
    start_time = time.time()
    utilization.test_dataset(dataset, "basic_utilization_test")
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    start_time = time.time()
    utilization.test_dataset(dataset, "RM_utilization_test")
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    start_time = time.time()
    utilization.test_dataset(dataset, "HB_utilization_test")
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    # --- Response Time Analysis ---
    start_time = time.time()
    RTA.test_dataset(dataset, "Audsley")
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    start_time = time.time()
    RTA.test_dataset(dataset, "Buttazzo")
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    start_time = time.time()
    RTA.test_dataset(dataset, "CPA")
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

    main()
