"""Configurations for logging."""
import logging
import os

LOG_FILE_NAME = "traditional-SA_results"


def init_logging(db_dir, db_name):
    """Initializes logging.

    Configures logging. Error messages are logged to the 'error.log' file. Info messages are logged
    to the console. The results are save in a 'result_' log file.

    Args:
        db_dir -- directory of the database, used to create file for results
        db_name -- name of the database, used to create file name for results
    """
    # create logger for traditional-SA project
    logger = logging.getLogger('traditional-SA')
    logger.setLevel(logging.INFO)

    # create file handler which logs error messages
    log_file_handler = logging.FileHandler('error.log', mode='w+')
    log_file_handler.setLevel(logging.ERROR)

    # create console handler with a lower log level (e.g debug or info)
    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_handler.setFormatter(formatter)
    log_console_handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(log_file_handler)
    logger.addHandler(log_console_handler)

    # create log file for results
    db_name = os.path.splitext(db_name)[0]  # remove file extension from the database name
    global LOG_FILE_NAME
    LOG_FILE_NAME = LOG_FILE_NAME + "_" + db_name + ".log"  # edit log file name
    log_file = open(os.path.join(db_dir, LOG_FILE_NAME), 'w+')  # create or clear file
    log_file.close()  # close file

    return logger


def log_results(test_name, results):
    """Print results of a schedulability analysis method.

    Overview of the results of a schedulability test is printed to the result file and the console.

    Args:
        test_name -- name of the schedulability analysis method
        results -- dictionary of results:
            tp -- true positive results
            fp -- false positive results
            tn -- true negative results
            fn -- false negative results
            time -- time elapsed for test
    """
    # create logger
    logger = logging.getLogger('traditional-SA.logging_config.print_results')

    # check input arguments
    if not isinstance(test_name, str):  # invalid argument for test_name
        raise ValueError("test_name must be of type String")
    if not isinstance(results, dict):  # invalid argument for results
        raise ValueError("results must be of type list")
    if len(results) < 4:  # to less results are given
        raise ValueError("results must be a dictionary containing entries for "
                         "'tp', 'fp', 'tn' and 'fn'")

    # calculate sum of all results
    sum_results = results['tp'] + results['fp'] + results['tn'] + results['fn']

    results['accuracy'] = (results['tp'] + results['tn']) / (sum_results)  # calculate accuracy
    results['precision'] = results['tp'] / (results['tp'] + results['fp'])  # calculate precision
    results['recall'] = results['tp'] / (results['tp'] + results['fn'])  # calculate recall

    # log results to the result log file
    log_file = open(LOG_FILE_NAME, 'a+')
    log_file.write("\n")
    result_title_string = "---------- Results of " + test_name + " ----------"
    log_file.write(result_title_string + "\n")
    log_file.write("True positive results (tp) = {0:d} = {1:.2f}% \n"
                   .format(results['tp'], results['tp'] / sum_results * 100))
    log_file.write("False positive results (fp) = {0:d} = {1:.2f}% \n"
                   .format(results['fp'], results['fp'] / sum_results * 100))
    log_file.write("True negative results (tn) = {0:d} = {1:.2f}% \n"
                   .format(results['tn'], results['tn'] / sum_results * 100))
    log_file.write("False negative results (fn) = {0:d} = {1:.2f}% \n"
                   .format(results['fn'], results['fn'] / sum_results * 100))
    log_file.write("Total = {0:d} \n".format(sum_results))
    log_file.write("-" * len(result_title_string) + "\n")
    log_file.write("Accuracy = {0:.2f}% \n".format(results['accuracy'] * 100))
    log_file.write("Precision = {0:.2f}% \n".format(results['precision'] * 100))
    log_file.write("Recall = {0:.2f}% \n".format(results['recall'] * 100))
    log_file.write("-" * len(result_title_string) + "\n")
    log_file.write("Time elapsed: {0:f}s \n".format(results['time']))
    log_file.write("-" * len(result_title_string) + "\n")

    # log results to the console
    result_title_string = "---------- Results of " + test_name + " ----------"
    logger.info(result_title_string)
    logger.info("True positive results (tp) = %d = %.2f%%",
                results['tp'], results['tp'] / sum_results * 100)
    logger.info("False positive results (fp) = %d = %.2f%%",
                results['fp'], results['fp'] / sum_results * 100)
    logger.info("True negative results (tn) = %d = %.2f%%",
                results['tn'], results['tn'] / sum_results * 100)
    logger.info("False negative results (fn) = %d = %.2f%%",
                results['fn'], results['fn'] / sum_results * 100)
    logger.info("Total = %d", sum_results)
    logger.info("%s", "-" * len(result_title_string))
    logger.info("Accuracy = %.2f%%", results['accuracy'] * 100)
    logger.info("Precision = %.2f%%", results['precision'] * 100)
    logger.info("Recall = %.2f%%", results['recall'] * 100)
    logger.info("%s", "-" * len(result_title_string))
    logger.info("Time elapsed: %fs", results['time'])
    logger.info("%s \n", "-" * len(result_title_string))
