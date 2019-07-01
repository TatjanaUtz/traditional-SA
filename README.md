This project is part of my master thesis at the Technical University Munich and also part of the 
MaLSAMi project of the Chair for Operating Systems at the Department of Informatics.


# Traditional Schedulability Analysis
Traditional schedulability analysis (SA) for fixed priority (FP) scheduler.
Possible analysis methods are:
- Simulation (simulation.py)
- Utilization Test (utilization.py)
- Response Time Analysis (rta.py)
- Workload Test (workload.py)

# Simulation
Simulation is an exact method to determine schedulability of a task-set. If all tasks are equally
activated at time t = 0, then simulation upon the hyperperiod is sufficient.
For Simulation the framework SimSo is used. The results of the simulation are checked for deadline-
misses. If no task misses its deadline, the task-set is schedulable.

# Utilization Test
Utilization-based test. There are three tests implemented:
- basic_utilization_test: classical utilization test for FP and EDF scheduler, U = sum[C_i / min(D_i, T_i)]) <= 1
- rm_utilization_test: utilization test for RM (rate-monotonic) scheduler, U = sum(C_i / T_i) <= n(2^[1/n] - 1)
- hb_utilization_test: utilization test with hyperbolic bound (HB), prod[U_i + 1] <= 2

# Response Time Analysis (RTA)
The response time analysis is an exact schedulability analysis for the FP scheduler. If all tasks
 start at time t = 0, the worst-case response time (WCRT) is calculated and compared to the 
 deadline. If the condition R_i <= D_i is true for all tasks of a task-set, then the task-set is 
 schedulable. If only for one task this condition isn't true, the task-set is not schedulable. 
 The worst-case response time of a task is calculated as follows:
 R_i^(k+1) = C_i + I_i,
 with I_i as the interference of tasks with higher or equal priority. The calculation of the 
 response time is recursive. There are two different start values implemented:
 - RTA according to Audsley: start with execution time of task.
 - RTA according to Buttazzo: start with the sum of execution time of the task and all tasks with
  higher or equal priority.
  The calculation can be stopped, if there is no more change in the response time.

# Workload Test
The workload tests are based on the level-i workload, that is the computing time in an interval 
[0, t] of a task i and all tasks with higher or same priority. There are two tests implemented:
- rm_workload_test: exact test for the RM (rate monotonic) scheduler.
- het_workload_test: Hyperplanes delta-Exact Test, exact analysis method for the FP scheduler.

# Data
The Task-Sets are given through a SQL-database with the following three tables:
- TaskSet: Set_ID, Successful, TASK1_ID, TASK2_ID, TASK3_ID, TASK4_ID
- Task: Task_ID, Priority, Deadline, Quota, CAPS, PKG, Arg, CORES, COREOFFSET, CRITICALTIME, 
Period, Number_of_Jobs, OFFSET
- Job: Set_ID, Task_ID, Job_ID, Start_Date, End_Date, Exit_Value

# Installation and Start
Download or clone the hole project. Add the database as described above to the project directory. Change to the project directory and type  
```bash
vagrant up
```
to start the vagrant machine. Then type
```bash
vagrant ssh
``` 
to ssh into the vagrant machine. Change the directory with
```bash
cd /vagrant
``` 
to the project directory. Then you can start the schedulability analysis by
```bash
python 3.6 main.py "db_dir" --test_all
``` 
where *db_dir* is the absolute path to the database file and *--test_all* are 
the schedulability analysis methods to perform. There are the following possibilities for the last 
argument:  

Argument | Description  
--- | ---
-h, --help | show the help information
--test_all | perform all implemented schedulability analysis methods
-s, --simulation | do simulation
-u, --utilization | do utilization tests
-rta, --response_time_analysis | do response time analysis
-w, --workload | do workload tests

