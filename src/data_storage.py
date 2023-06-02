import os, json
from flask import jsonify
import concurrent.futures
import time
from multiprocessing.pool import ThreadPool
import sqlite3
from sqlite3 import Error
from threading import Lock

from clocks import new_clock
from utils import RepeatedTimer
from pathlib import Path

Path(os.path.dirname(__file__)+"/.metadata").mkdir(exist_ok=True)
# define
DATA_PATH = os.path.dirname(__file__) + "/.metadata/"
DATA_ENCODING = "iso-8859-1"
DATA_PERSISTANCE_PERIODICITY = 10  # in seconds
LOCK = Lock()

"""
TODO:
    1. Establish an eviction policy for in memory data
        - 4 MB?
    2. Delete items from disk
"""
# SQLite database functionality

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        # The Data Base capacity is 1 GB
        connection.cursor().execute('PRAGMA page_size = 1000000000')
    except Error as e:
        raise e
    return connection

def execute_query(connection, query, data=None):
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
    except Error as e:
        raise e
    
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        raise e

# DataStorage object is an interface for the storage system on each local node 
class DataStorage:
    def __init__(self, data={}, data_clocks={}, last_writer={}, owner="0.0.0.0"):
        self.data = data
        self.data_clocks = data_clocks
        self.last_writer = last_writer
        self.owner = owner
        # Launch disk persistance routine
        #self.timer = RepeatedTimer(DATA_PERSISTANCE_PERIODICITY, self._persist_all_data)
        # Set up SQL database
        self.db_connection = create_connection(DATA_PATH+"data_storage.db")
        execute_query(self.db_connection,
                       """CREATE TABLE IF NOT EXISTS data (
                                    key TEXT PRIMARY KEY,
                                    dtype,
                                    data_clocks TEXT,
                                    last_writer TEXT,
                                    data
                                );
                            """
        )
    # Put raw data into memory
    def put(self, key, data, causal_metadata, last_writer, persist=True):
        self.data[key] = data
        self.data_clocks[key] = causal_metadata
        self.last_writer[key] = last_writer
        if persist:
            self._persist_data(key)

    # Get data for a given key
    def get(self, key, check_disk=True):
        # Check if data is stored in memory (most up-to date copy)
        if key in self.data:
            return dict(
                val=self.data[key],
                clock=self.data_clocks[key],
                last_writer=self.last_writer[key]
                )
        # Otherwise check on disk
        elif check_disk:
            return self._get_from_disk(key)

    # Search and get data from disk for a given key
    def _get_from_disk(self, key):
        # returns a tuple in format (key, data, data_clocks, last_writer)
        query_result = execute_read_query(self.db_connection, f"SELECT * FROM data WHERE key='{key}'")
        if not query_result:
            return None
        query_result = query_result[0]
        # Put the newly retrieved data into memory
        data = dict(val=dict(data=query_result[4], dtype=query_result[1]),
                    clock=json.loads(query_result[2]),
                    last_writer=json.loads(query_result[3]))
        self.put(query_result[0], data['val'], data['clock'], data['last_writer'], persist=False)
        return data
    
    # Write all available data from memory to disk
    def _persist_all_data(self):
        data_tuples = [(key, self.data[key]["dtype"], json.dumps(self.data_clocks[key]), json.dumps(self.last_writer[key]), self.data[key]["data"]) for key in self.data.keys()]
        if data_tuples:
            for t in data_tuples:
                # INSERT query
                execute_query(self.db_connection,
                                """
                                    REPLACE INTO
                                    data (key, dtype, data_clocks, last_writer, data)
                                    VALUES (?, ?, ?, ?, ?);
                                """, t)
                
    # Write data for a given key from memory to disk
    def _persist_data(self, key):
        data_tuple = (key, self.data[key]["dtype"], json.dumps(self.data_clocks[key]), json.dumps(self.last_writer[key]), self.data[key]["data"])
        # INSERT query
        execute_query(self.db_connection,
                        """
                            REPLACE INTO
                            data (key, dtype, data_clocks, last_writer, data)
                            VALUES (?, ?, ?, ?, ?);
                        """, data_tuple)
        
    # Retrieve all available keys
    def get_keys(self):
        query_result = execute_read_query(self.db_connection, f"SELECT DISTINCT(key) FROM data")
        if not query_result:
            return []
        query_result = [i[0] for i in query_result]
        return query_result
    
    # Cache causal-metadata for a given key into memory
    # returns data_clock and last writer
    def cache_causal_metadata(self, key):
        if key in self.data_clocks:
            return self.data_clocks[key]
        # returns a tuple in format (key, data, data_clocks, last_writer)
        query_result = execute_read_query(self.db_connection, f"SELECT data_clocks, last_writer FROM data WHERE key='{key}'")
        if not query_result:
            return [None, None]
        query_result = query_result[0]
        # Put the newly retrieved data into memory
        clock = json.loads(query_result[0])
        last_writer = json.dumps(query_result[1])
        return clock, last_writer
