"""Cofiguration for logging."""
import logging

LOG_FILE_NAME = "results.log"

def init_logging():
    """Initializes logging.

    Configures logging. Error messages are logged to the 'error.log' file. All messages are logged
    to the console.
    """
    # create logger for 'traditional-SA# project
    logger = logging.getLogger('traditional-SA')
    logger.setLevel(logging.INFO)

    # create file handler which logs error messages
    log_file_handler = logging.FileHandler('error.log', mode='w+')
    log_file_handler.setLevel(logging.ERROR)

    # create console handler with a lower log level
    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_handler.setFormatter(formatter)
    log_console_handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(log_file_handler)
    logger.addHandler(log_console_handler)

    # Create file to which results should be written to
    log_file = open(LOG_FILE_NAME, 'w+')
    log_file.close()

    return logger

def print_results(test_name, results):
    """Print results of a schedulability analysis method.

    Overview of the results of a schedulability test is printed.

    Args:
        test_name - name of the schedulability analysis method
        results -- list of results:
            [0] -- true positive results
            [1] -- false positive reults
            [2] -- true negative results
            [3] -- false negative results
            [4] -- not assignable (other) results
    """
    # create logger
    logger = logging.getLogger('traditional-SA.main.print_results')

    # check input arguments
    if not isinstance(test_name, str):  # invalid argument for test_name
        raise ValueError("Invalid argument for test_name (must be string)!")
    if not isinstance(results, list):  # invalid argument for results
        raise ValueError("Invalid argument for results (must be list)!")
    if len(results) < 5:  # to less results are given
        raise ValueError("Invalid argument for results: must be a list containing "
                     "[true_positives, false_positives, true_negatives, false_negatives, other]!}")

    sum_results = sum(results[:4])  # sum of correct and incorrect results
    correct = results[0] + results[2]  # number of correct results
    incorrect = results[1] + results[3]  # number of incorrect results

    # Print results to a file
    log_file = open(LOG_FILE_NAME, 'a+')
    log_file.write("\n")
    result_title_string = "---------- Results of " + test_name + " ----------"
    log_file.write(result_title_string + "\n")
    log_file.write("Correct results: {0:d} / {1:d} = {2:0.2f}% \n"
                   .format(correct, sum_results, correct * 100 / sum_results))
    log_file.write("Incorrect results: {0:d}/ {1:d} = {2:.2f}% \n"
                   .format(incorrect, sum_results, incorrect * 100 / sum_results))
    log_file.write("True positive results (tp) = {0:d} = {1:.2f}% \n"
                   .format(results[0], results[0] * 100 / sum_results))
    log_file.write("False positive results (fp) = {0:d} = {1:.2f}% \n"
                   .format(results[1], results[1] * 100 / sum_results))
    log_file.write("True negative results (tn) = {0:d} = {1:.2f}% \n"
                   .format(results[2], results[2] * 100 / sum_results))
    log_file.write("False negative results (fn) = {0:d} = {1:.2f}% \n"
                   .format(results[3], results[3] * 100 / sum_results))
    log_file.write("Other results = {0:d} \n".format(results[4]))
    log_file.write("-" * len(result_title_string) + "\n")

    # Print results to console
    result_title_string = "---------- Results of " + test_name + " ----------"
    logger.info(result_title_string)
    logger.info("\t Correct results: {0:d} / {1:d} = {2:0.2f}%"
                .format(correct, sum_results, correct * 100 / sum_results))
    logger.info("\t Incorrect results: {0:d}/ {1:d} = {2:.2f}%"
                .format(incorrect, sum_results, incorrect * 100 / sum_results))
    logger.info("\t True positive results (tp) = {0:d} = {1:.2f}%"
                .format(results[0], results[0] * 100 / sum_results))
    logger.info("\t False positive results (fp) = {0:d} = {1:.2f}%"
                .format(results[1], results[1] * 100 / sum_results))
    logger.info("\t True negative results (tn) = {0:d} = {1:.2f}%"
                .format(results[2], results[2] * 100 / sum_results))
    logger.info("\t False negative results (fn) = {0:d} = {1:.2f}%"
                .format(results[3], results[3] * 100 / sum_results))
    logger.info("\t Other results = {0:d}".format(results[4]))
    logger.info("-" * len(result_title_string))


