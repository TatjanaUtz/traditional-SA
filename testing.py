# import simsogui
# simsogui.run_gui()

import database as db
import logging

from workload import het_workload_test

# Configure logging: format should be "LEVELNAME: Message",
# logging level should be DEBUG (all messages are shown)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

db.read_execution_times()

taskset_46429 = db.get_taskset(taskset_id=46429)
print(het_workload_test(taskset_46429))

taskset_563782 = db.get_taskset(taskset_id=563782)
print(het_workload_test(taskset_563782))




