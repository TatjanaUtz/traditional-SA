#import simsogui
#simsogui.run_gui()

import database as db
import logging
from utilization import basic_utilization_test
from simulation import simulate

# Configure logging: format should be "LEVELNAME: Message",
# logging level should be DEBUG (all messages are shown)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

db.read_execution_times()

taskset_46429 = db.get_taskset(id=46429)
print(simulate(taskset_46429))

taskset_563782 = db.get_taskset(id=563782)
print(simulate(taskset_563782))



