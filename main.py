"""Main file of project."""
import logging
import utilization_test as ut
import utils_database as ud


def main():
    """Main function of project."""
    print("Hello World! Main function is empty :P")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    main()
