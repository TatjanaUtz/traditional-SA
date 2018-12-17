"""For the new database 'panda_v1'."""
import logging  # for logging
import os
import sqlite3  # for working with the database

# attributes of the database
db_dir = os.path.dirname(
    os.path.abspath(__file__))  # path to the database = current working directory
db_name = "panda_v1"  # name of the database

_db_connection = None  # connection to the database
_db_cursor = None  # cursor for working with the database

_execution_time = {
    ("hey", 0): 1045,
    ("hey", 1000): 1094,
    ("hey", 1000000): 1071,

    ("pi", 100): 1574,
    ("pi", 10000): 1693,
    ("pi", 100000): 1870,

    ("cond_42", 41): 1350,
    ("cond_42", 42): 1376,
    ("cond_42", 10041): 1413,
    ("cond_42", 10042): 1432,
    ("cond_42", 1000041): 1368,
    ("cond_42", 1000042): 1396,

    ("cond_mod", 100): 1323,
    ("cond_mod", 103): 1351,
    ("cond_mod", 10000): 1395,
    ("cond_mod", 10003): 1391,
    ("cond_mod", 1000000): 1342,
    ("cond_mod", 1000003): 1391,

    ("tumatmul", 10): 1511,
    ("tumatmul", 11): 1543,
    ("tumatmul", 10000): 1692,
    ("tumatmul", 10001): 1662,
    ("tumatmul", 1000000): 3009,
    ("tumatmul", 1000001): 3121,

    "hey": 1070,
    "pi": 1712,
    "cond_42": 1389,
    "cond_mod": 1366,
    "tumatmul": 2090
}


# Open database
def open_DB():
    """Open the database.

    If the database can be found, a connection and cursor is created and saved.
    If there is no database file defined through db_dir and db_name,
    an error message is printed.
    """
    global db_name
    db_path = db_dir + "\\" + db_name

    # Check if database exists
    if os.path.exists(db_path):  # database exists
        global _db_connection, _db_cursor
        _db_connection = sqlite3.connect(db_path)
        _db_cursor = _db_connection.cursor()
    else:  # database does not exist
        logging.error("new_database/open_DB(): Database '" + db_name + "' not found!")


# Close database
def close_DB():
    """Close the database.

    If the database is open, the changes are saved before the database is closed.
    """
    global _db_connection, _db_cursor
    if _db_connection is not None:  # database is open
        _db_connection.commit()
        _db_connection.close()
        _db_connection = None
        _db_cursor = None
    else:  # database is already closed
        logging.error("new_database/close_DB(): No open database!")


if __name__ == "__main__":
    # Configure logging: format should be "LEVELNAME: Message",
    # logging level should be DEBUG (all messages are shown)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
