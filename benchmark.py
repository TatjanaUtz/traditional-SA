"""Module to benchmark the execution times of tasks."""
import logging
import time

import database_interface


def benchmark_execution_times(database):
    """Benchmark to get average execution times of tasks.

    This method determines for each task the task-sets, that consist only of this task. Then all jobs of this
    task-sets and for the task are read from the database. The execution time of the jobs is calculated from the start-
    and end-date and the average value is built upon this execution times.

    Args:
        database -- a Database-object
    """
    logger = logging.getLogger('traditional-SA.benchmark.benchmark_execution_times')
    logger.info("Starting to benchmark execution times...")
    start_time = time.time()

    task_list = database.read_table_task(dict=False)  # read table 'Task'
    c_dict = dict()  # create empty dictionary for execution times

    for task in task_list:  # iterate over all tasks
        # get all task-sets where the current task is the only task
        taskset_list = database.read_table_taskset(task_id=task[0], convert=False)

        job_list = []  # create empty list for the jobs

        for taskset in taskset_list:  # iterate over all task-sets
            # add all successfully run jobs of the current task and task-set
            job_list.extend(database.read_table_job(set_id=taskset[0], task_id=task[0], exit_value='EXIT'))

        if job_list:  # at least one job was read
            # calculate execution time of each job
            job_list = _calculate_executiontimes(job_list)

            # calculate average execution time of current task
            average_c = sum(job_list) / len(job_list)

            # round and add execution time to the dictionary
            c_dict[task[0]] = round(average_c)

    end_time = time.time()
    logger.info("Benchmark of execution times finished!")
    logger.info("Time elapsed: %f", end_time - start_time)

    # write execution times to the database
    logger.info("Saving calculated execution times to database...")
    database.write_execution_time(c_dict)
    logger.info("Saving successful!")


def _calculate_executiontimes(job_attributes):
    """Calculate the execution times of the given jobs.

    This method calculates the execution times of a list of jobs with the following attributes:
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
    executiontimes = []  # create empty list for execution times

    # iterate over all jobs
    for job in job_attributes:
        execution_time = job[4] - job[3]  # calculate execution time = end_date - start_date

        # check if execution_time is valid
        if execution_time > 0:
            executiontimes.append(execution_time)  # append execution time to list

    return executiontimes


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # create Database object - benchmark is started within constructor
    database_interface.Database(db_dir="C:\\Users\\tatjana.utz\\PycharmProjects\\Datenbanken",
                                db_name="panda_v3.db")
