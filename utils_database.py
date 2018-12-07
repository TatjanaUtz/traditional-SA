"""Methods for working with a database."""

import sqlite3
import os
import logging

# Variables
db_name = 'database_haecker.db'     # Name of the database, must include the '.db'-extension
db_path = None                      # Path to the database, None if current folder should be used
table_name = "Dataset1"             # Name of the table
db_connection = None                # Connection to the database


# Open a database
def openDb(db_name, db_path=os.path.dirname(os.path.abspath(__file__))):
    """Open the database and return a connection to the database.

    If there is no database file defined through db_name and db_path,
    a sqlite3.OperationalError is raised.
    Keyword arguments:
    db_name -- name of the database with file ending '.db'
    db_path -- optional, path to the database, default is the current folder
    Return values:
    connection to the database
    """
    logging.debug("openDb(): connection to database will be established")
    # Check if a valid path to the database is given
    if db_path is None:
        logging.debug("openDb(): No db_path given, current folder is used")
        db_path = os.path.dirname(os.path.abspath(__file__))

    full_db_name = db_path + "\\" + db_name
    return sqlite3.connect("file:" + full_db_name + "?mode=rw", uri=True)


# Close a database
def closeDb(db_connection):
    """Close a database.

    Before the database is closed, the changes are saved.
    Keyword arguments:
    db_connection -- connection to the database
    """
    logging.debug("closeDb(): connection to database will be closed")
    db_connection.commit()
    db_connection.close()


# Read a table
def readTable(db_connection, table_name):
    """Read a complete table from a database.

    If the table does not exist in the database, a sqlite3.OperationalError is raised.
    Keyword arguments:
    db_connection -- connection to the database
    table_name -- name of the table
    Return values:
    data -- Array with the data of the table
    """
    logging.debug("readTable(): Table '" + table_name + "' will be read")
    db_cursor = db_connection.cursor()
    sql_command = "SELECT * FROM " + table_name
    data = []
    for row in db_cursor.execute(sql_command):
        data.append(row)
    return data
    

if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    # Open the database
    db_connection = openDb(db_name, db_path)

    getExecutionTimes()

    # Close the database
    closeDb(db_connection)
