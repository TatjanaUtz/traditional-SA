"""Functions to read data from a database."""

import os
import sqlite3
import numpy as np
from Task import Task
import Task as tsk

# path to the database
db_path = "C:\\Users\\tatjana.utz\\Google Drive\\WS2018_19\\Programmierung"
# define the name of the database
db_name = "database_haecker" + ".db"
# define the dataset (name of the table in the database)
table_name = "Dataset2"
# connection to the database
db_connection = None

# A Taskset
taskset = []


def output(msg):
    """Output a message.

    Keyword arguments:
    msg -- message to output

    Return values:
    None
    """
    for line in msg.splitlines():
        print("ReadDatabase: " + line)


def openDb(db):
    """Open a database.

    Keyword arguments:
    db -- the database

    Return values:
    connection to the database
    """
    # Check if db exists
    if not os.path.exists(db):      # db doesn't exist
        output("ERROR: no database found!")
        return

    # db exists: create connection to db
    output("Database " + db + " exists!")
    db_connection = sqlite3.connect(db)

    # Check if successful connected
    if db_connection is None:
        output("ERROR: Connection to database unsuccessful!")
        return

    # Return db connection
    return db_connection


def closeDb(db_connection):
    """Close a database.

    Keyword arguments:
    db_connection -- connection to a database

    Return values:
    None
    """
    # Save changes of the database
    db_connection.commit()
    # Close database
    db_connection.close()


def getNumberOfEntries(db_connection, table_name, id_field):
    """Return the number of entries.

    Keyword arguments:
    db_connection -- connection to a database
    table_name -- name of a table
    id_field -- name of a ID field

    Return values:
    number of entries
    """
    sql_command = "SELECT count(" + id_field + ") FROM " + table_name
    db_cursor = db_connection.cursor()
    db_cursor.execute(sql_command)
    return db_cursor.fetchone()[0]


def getData(db_connection, table_name):
    """Get the data from a table.

    Keyword arguments:
    db_connection -- connection to a database
    table_name -- name of a table

    Return values:
    array of data
    """
    sql_command = "SELECT * FROM " + table_name
    db_cursor = db_connection.cursor()
    db_cursor.execute(sql_command)

    data = []
    currentLine = db_cursor.fetchone()
    if currentLine is None:
        return (0)

    # store data from database in array
    while currentLine is not None:
        data.append(currentLine)
        currentLine = db_cursor.fetchone()
    data = np.array(data)

    # check if there is data
    if len(data) == 0:
        output("No data in table '" + table_name + "' available!")
        return ()

    return data


def separateData(data):
    """Seperate results from data.

    Keyword arguments:
    data -- the data array

    Return values:
    [data], [results]
    """
    i = 0
    range = []
    while i < (len(data[0]) - 1):   # last field for result
        if i != 0:                  # 0 is the id field
            range.append(i)
        i += 1

    return data[:, range], data[:, (len(data[0]) - 1)]


def readDataset(db_connection, table_name):
    """ Read a dataset from a dataset .

    Keyword arguments:
    db_connection -- connection to a database
    table_name -- name of the table / name of the dataset

    Return values:
    dictionary of the dataset
    """
    data = getData(db_connection, table_name)

    numberOfTasks = int((len(data[0]) - 2) / Task.numberOfProperties)    # -2 for Set_ID and Exit_Value

    dataset = []
    i = 0
    while i < len(data):
        taskset = []
        j = 0
        while j < numberOfTasks:
            taskset.append(Task(data[0][1+j], data[0][2+j], data[0][3+j], data[0][4+j], data[0][5+j], data[0][6+j], data[0][7+j], data[0][8+j]))
            j += 1
        dataset.append(taskset)
        i += 1

    return dataset


if __name__ == "__main__":

    # open database
    db_connection = openDb(db_path + "\\" + db_name)

    # get number of entries
    output("Number of entries = " + str(getNumberOfEntries(db_connection, table_name, "Set_ID")))

    # test Function
    dataset = readDataset(db_connection, table_name)
    output(str(dataset))

    # get data
    X_data, y_data = separateData(getData(db_connection, table_name))
    output("X_data: " + str(X_data[0]))
    output("y_data: " + str(y_data[0]))

    # close database
    closeDb(db_connection)
