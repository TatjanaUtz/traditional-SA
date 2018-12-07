"""Main file of project."""
import logging
import utilization_test as ut
import utils_database as ud


def main():
    """Main function of project."""
    # Perform utilzation-based schedulability analysis
    db_connection = ud.openDb(ud.db_name)   # Open database
    db_cursor = db_connection.cursor()  # Create a cursor for database

    # Read out execution times of tasks depending on PKG and save as dictionary
    dict_C = {}  # Empty dictionary for execution times C
    for row in db_cursor.execute("SELECT * FROM ExecutionTimes"):
        dict_C[row[0]] = row[1]

    # Variable for efficiency check
    tp, fp, tn, fn, total = 0, 0, 0, 0, 0

    # Name of table
    table_name = "Dataset1"

    # Get number of columns of table 'Dataset1'
    db_cursor.execute("PRAGMA table_info('" + table_name + "')")
    numberOfColumns = len(db_cursor.fetchall())

    # Calculate number of tasks in dataset
    # -2 for Set_ID and Exit_Value
    # /8 because each task has 8 properties
    numberOfTasks = int((numberOfColumns - 2) / 8)

    # Read out table 'Dataset1' and perform utilization test for each taskset in table
    for row in db_cursor.execute("SELECT * FROM " + table_name):
        # Create taskset through iteration over all tasks
        taskset = []    # Empty taskset
        for i in range(numberOfTasks):
            executionTime = dict_C[row[4+i*8]]  # Execution time of task i
            period = row[6+i*8]  # Period of task i
            taskset. append((executionTime, period))

        # Perform utilization test
        schedulability = ut.utilization_test_rm(taskset)
        exitValue = row[-1]  # Exit value from database

        # Analyse efficiency of utilization_test
        if schedulability is True and exitValue == 1:
            tp += 1
        elif schedulability is True and exitValue == -1:
            fp += 1
        elif schedulability is False and exitValue == 1:
            fn += 1
        elif schedulability is False and exitValue == -1:
            tn += 1
        total += 1

    print("---------- RESULTS FOR " + table_name + " ----------")
    print("Correct: {0:d} / {1:d} -> {2:.0f}%".format(tp+tn, total, (tp+tn)*100/total))
    print("Incorrect: {0:d} / {1:d} -> {2:.0f}%".format(fp+fn, total, (fp+fn)*100/total))
    print("True positive (tp) = {0:d}".format(tp))
    print("False positive (fp) = {0:d}".format(fp))
    print("True negative (tn) = {0:d}".format(tn))
    print("False negative (fn) = {0:d}".format(fn))
    print("------------------------------------------")

    ud.closeDb(db_connection)   # Close database


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    main()
