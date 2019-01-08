import logging
import math

from Task import Task
from Taskset import Taskset


def get_scheduling_points(taskset):
    sp = []  # List of scheduling points

    # Get scheduling points (s)
    for task in taskset:
        k_max = int(taskset[-1].period / task.period)
        k = 1
        while k <= k_max:
            s_ele = k * task.period
            if s_ele not in sp:
                sp.append(s_ele)
                sp.sort()
            k += 1

    return sp


def workload_test_Lehoczky(sp, taskset):
    for s_list in sp:
        w = 0.0
        for task in taskset:
            w += task.execution_time * math.ceil(s_list / task.period)

        if w <= s_list:
            print("Taskset is schedulable!")
            return True

    print("Taskset is NOT schedulable!")
    return False


def workload_test_arb_d(taskset, check_task):
    # check input arguments
    if not isinstance(taskset, Taskset) or not isinstance(check_task, Task):  # invalid input arguments
        logging.error("workload/workload_test_arb_d(): invalid input arguments!")
        return -1

    hp = Taskset(tasks=[])
    for task in taskset:  # iterate over all tasks
        if task.priority <= check_task.priority and task is not check_task:
            hp.add_task(task)



if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    task1 = Task(id=1, priority=1, period=100, execution_time=40)
    task2 = Task(id=2, priority=2, period=150, execution_time=40)
    task3 = Task(id=3, priority=3, period=350, execution_time=100)

    taskset = Taskset(result=0, tasks=[task1, task2, task3])

    workload_test_arb_d(taskset, task3)

    scheduling_points = get_scheduling_points(taskset)
    print(scheduling_points)
    schedulability = workload_test_Lehoczky(scheduling_points, taskset)
    print(schedulability)
