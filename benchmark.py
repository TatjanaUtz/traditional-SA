"""Module to benchmark runtimes of tasks.

All successfully ran jobs from the database are read. For each task the maximum, minimum and average
execution times are calculated and saved to the database.
"""
import logging

import database_interface


def benchmark_execution_times(database):
    """Benchmark test to get average execution times of tasks.

    This method reads all jobs of all tasks from the database and calculates the average execution
    time of each task defined by PKG and for each combination of PKG and Arg.

    Args:
        database -- a database object
    """
    # create logger
    logger = logging.getLogger('traditional-SA.benchmark.benchmark_execution_times')
    logger.info("Starting to benchmark execution times...")

    # read table Task
    task_list = database.read_table_task(dictionary=False)

    # create empty dictionary
    task_dict = dict()

    # iterate over all tasks
    for task in task_list:
        # get all pkg and all combinations of pkg and arg from the task list
        pkg = task[5]
        arg = task[6]
        if pkg not in task_dict:  # pkg not in the dictionary
            task_dict[pkg] = []  # add pkg
        if (pkg, arg) not in task_dict:  # (pkg, arg) not in dictionary
            task_dict[(pkg, arg)] = []  # add (pkg, arg)

        # read all sucessfully run jobs of the task
        job_attributes = database.read_table_job(task_id=task[0], exit_value='EXIT')

        # check if at least one job was read
        if job_attributes:
            # calculate execution time of each job
            job_list = _calculate_executiontimes(job_attributes)

        # add execution times to the dictionary
        task_dict[pkg].extend(job_list)  # add execution times to PKG
        task_dict[(pkg, arg)].extend(job_list)  # add execution times to (PKG, arg)

    # empty list for keys to be deleted, because no successful jobs were found
    delete_keys = []

    # iterate over all dictionary keys
    for key in task_dict:
        if task_dict[key]:  # at least one execution time was found
            # calculate average execution time
            average_c = sum(task_dict[key]) / len(task_dict[key])

            # round and save calculated value
            task_dict[key] = round(average_c)
        else:  # no execution time was found: delete key from dictionary
            delete_keys.append(key)

    # delete unused keys
    for key in delete_keys:
        del task_dict[key]

    # save execution times to database
    logger.info("Saving calculated execution times to database...")
    database.write_execution_time(task_dict)

    logger.info("Saving successful! Benchmark finished!")


def _calculate_executiontimes(job_attributes):
    """Calculate the executiontimes of jobs.

    This method calculates the executiontimes of a list of jobs with the following attributes:
        Set_ID
        Task_ID
        Job_ID
        Start_Date
        End_Date
        Exit_Value

    Args:
        job_attributes -- list with the job attributes
    Return:
        executiontimes -- list with the executiontimes
    """
    executiontimes = []  # create empty list for executiontimes

    # iterate over all jobs
    for job in job_attributes:
        execution_time = job[4] - job[3]  # calculate executiontime = end_date - start_date

        # check if execution_time is valid
        if execution_time > 0:
            executiontimes.append(execution_time)  # append executiontime to list

    return executiontimes


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    # create Database object - benchmark is started within constructor
    database_interface.Database(db_dir="C:\\Users\\tatjana.utz\\PycharmProjects\\Datenbanken",
                                db_name="panda_v3.db")
