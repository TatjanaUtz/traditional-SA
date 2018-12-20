import time

from pycpa import analysis
from pycpa import model
from pycpa import schedulers
from utilization import basic_utilization_test
import new_database as db


def CPA(taskset):
    # generate a new system
    s = model.System()

    # add one resources (CPUs) to the system
    # and register the static priority preemptive scheduler
    r1 = s.bind_resource(model.Resource("R1", schedulers.SPPSchedulerRoundRobin()))

    # create and bind tasks to r1
    # register a periodic event model for all tasks
    tasks = []
    for i in range(len(taskset)):
        tasks.append(r1.bind_task(model.Task(str(taskset[i].id), wcet=taskset[i].execution_time,
                                             scheduling_parameter=taskset[i].priority)))
        tasks[i].in_event_model = model.PJdEventModel(P=taskset[i].period)

    # perform the analysis
    task_results = analysis.analyze_system(s)

    # print the worst case response times (WCRTs)
    # check schedulability WCRT <= D
    for r in s.resources:
        i = 0
        for t in r.tasks:
            wcrt = task_results[t].wcrt
            deadline = taskset[i].deadline
            if wcrt > deadline:
                return False
            i += 1

    return True


def test_dataset(taskset_list):
    """Test a hole dataset.

    dataset -- the dataset that should be tested.
    """
    # taskset_list = db.get_dataset(dataset)

    # Get number of task-sets in the dataset
    number_of_tasksets = len(taskset_list)

    # Variable for checking result of test
    tp, fp, tn, fn = 0, 0, 0, 0

    for i in range(number_of_tasksets):  # Iterate over all task-sets
        taskset = taskset_list[i]
        if basic_utilization_test(taskset) is True:
            schedulability = CPA(taskset)
        else:
            schedulability = False
        exit_value = taskset.result

        # Analyse test
        if schedulability is True and exit_value == 1:  # True positives
            tp += 1
        elif schedulability is True and exit_value == 0:  # False positives
            fp += 1
        elif schedulability is False and exit_value == 1:  # False negatives
            fn += 1
        elif schedulability is False and exit_value == 0:  # True negatives
            tn += 1

    # Print results
    s = "-------------------- RESULTS OF RTA --------------------"
    print(s)
    print("Correct: {0:d} / {1:d} -> {2:.0f}%".format(tp + tn, number_of_tasksets,
                                                      (tp + tn) * 100 / number_of_tasksets))
    print("Incorrect: {0:d} / {1:d} -> {2:.0f}%".format(fp + fn, number_of_tasksets,
                                                        (fp + fn) * 100 / number_of_tasksets))
    print("True positive (tp) = {0:d}".format(tp))
    print("False positive (fp) = {0:d}".format(fp))
    print("True negative (tn) = {0:d}".format(tn))
    print("False negative (fn) = {0:d}".format(fn))
    print("-" * len(s))


if __name__ == "__main__":
    start_time = time.time()
    dataset = db.get_dataset()
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)

    start_time = time.time()
    test_dataset(dataset)
    end_time = time.time()
    print("Time elapsed = ", end_time - start_time)
