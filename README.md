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
Response Time Analysis (RTA) with two different start values

# Workload Test
Worload-based test. There are two test implemented.