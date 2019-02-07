# Traditional Schedulability Analysis
Traditional schedulability analysis (SA) for fixed priority (FP) scheduler.
Possible analysis tools are:
- simulation
- utilization test
- response time analysis (RTA)
- workload test

# Simulation
Simulate a task-set upon the hyperperiod and get schedulability of task-set (true = schedulable, false = not schedulable).

# Utilization
Utilization-based test. There are three tests implemented:
- basic_utilization_test: classical utilization test for FP and EDF scheduler, U = sum[C_i / min(D_i, T_i)]) <= 1
- rm_utilization_test: utilization test for RM (rate-monotonic) scheduler, U = sum(C_i / T_i) <= n(2^[1/n] - 1)
- hb_utilization_test: utilization test with hyperbolic bound (HB), prod[U_i + 1] <= 2

# RTA
Response Time Analysis (RTA) with two different start values

# Workload
Worload-based test. There are two test implemented.