import logging

import new_database as db


def benchmark_runtimes():
    """ Benchmark test to get execution times of tasks.

    Reads all jobs of all tasks from the database and calculates the minimum, maximum and average
    execution time of each task defined by PKG and for each combination of PKG and arg.
    """
    logging.debug("benchmark_runtimes.py/benchmark_runtimes(): Starting to benchmark runtimes...")

    # Get all tasks from the database
    task_list = db.get_all_tasks()

    # create empty dictionary
    task_dict = dict()

    # iterate over all tasks
    for task in task_list:
        # get all pkg and all combinations of pkg and arg from the task list
        if task.pkg not in task_dict:  # pkg not in the dictionary
            task_dict[task.pkg] = []  # add pkg
        if (task.pkg, task.arg) not in task_dict:  # (pkg, arg) not in dictionary
            task_dict[(task.pkg, task.arg)] = []  # add (pkg, arg)

        # get execution times of all jobs of the current task
        job_list = db.get_jobs_C(task.id)

        # add execution times to the dictionary
        if job_list is not -1:  # at least one job was found
            task_dict[task.pkg].extend(job_list)  # add execution times to PKG
            task_dict[(task.pkg, task.arg)].extend(job_list)  # add execution times to (PKG, arg)

    # empty list for keys to be deleted, because no successful jobs were found
    delete_keys = []

    # iterate over all dictionary keys
    for key in task_dict:
        if len(task_dict[key]) > 0:  # at least one execution time was found
            min_C = min(task_dict[key])  # calculate minimum execution time
            max_C = max(task_dict[key])  # calculate maximum execution time
            average_C = sum(task_dict[key]) / len(
                task_dict[key])  # calculate average execution time

            # save calculated values
            task_dict[key] = (min_C, max_C, average_C)
        else:  # no execution time was found: delete key from dictionary
            delete_keys.append(key)

    # delete unused keys
    for key in delete_keys:
        del task_dict[key]

    logging.debug(
        "benchmark_runtimes.py/benchmark_runtimes(): saving calculated execution times to database...")

    # save execution times to database
    db.save_execution_times(task_dict)

    logging.debug(
        "benchmark_runtimes.py/benchmark_runtimes(): saving successful! Benchmark finished!")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    benchmark_runtimes()
