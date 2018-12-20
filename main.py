"""Main file of project."""

import logging
import time

import RTA
import new_database as db
import test_pycpa


def main():
    """Main function of project."""
    start_time = time.time()
    dataset = db.get_dataset()
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    start_time = time.time()
    RTA.test_dataset(dataset)
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    start_time = time.time()
    test_pycpa.test_dataset(dataset)
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

    main()
