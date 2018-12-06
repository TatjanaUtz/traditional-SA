"""Main file of project."""
import logging
from utilization_test import utilization_test


def main():
    """Main function of the project."""
    # Perform utilzation-based schedulability analysis
    example_taskset = [(5000, 10000), (3001, 10000), (2000, 10000)]
    result = utilization_test(example_taskset)
    print(result)


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main()
