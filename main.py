"""Main file of project."""

import logging

import Database as db


def main():
    """Main function of project."""
    taskset = db.get_taskset(1)
    print(taskset)


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    main()
