"""For testing pyCPA."""
from pycpa import *

# Generate a new system (empty container for all other objects)
s = model.System('example1')

# Add three resources (2 CPUs, 1 Bus) to the system
# and register the SPP scheduler (and SPNP for the bus)
r1 = s.bind_resource(model.Resource("CPU1", schedulers.SPPScheduler()))

# Create and bind tasks to r1
t1 = r1.bind_task(model.Task("T1", wcet=1045, bcet=1045, scheduling_parameter=3))
t2 = r1.bind_task(model.Task("T2", wcet=1574, bcet=1574, scheduling_parameter=2))
t3 = r1.bind_task(model.Task("T3", wcet=1413, bcet=1413, scheduling_parameter=1))

# Register a periodic with jitter event model for T11 and T12
t1.in_event_model = model.PJdEventModel(P=10000, J=0)
t2.in_event_model = model.PJdEventModel(P=10000, J=0)
t3.in_event_model = model.PJdEventModel(P=10000, J=0)

# Graph the system to visualize the architecture
g = graph.graph_system(s, filename='%s.pdf' % s.name, dotout='%s.dot' % s.name, show=False)

 # Perform the analysis
print("\nPerforming analysis of system '%s'" % s.name)
task_results = analysis.analyze_system(s)

# Print the worst case response times (WCRTs)
print("Result:")
for r in sorted(s.resources, key=str):
    for t in sorted(r.tasks & set(task_results.keys()), key=str):
        print("%s: wcrt=%d" % (t.name, task_results[t].wcrt))
        print("    b_wcrt=%s" % (task_results[t].b_wcrt_str()))
