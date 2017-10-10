#!/usr/bin/env python3

import sqlite3
import datetime
import sys
import logging
from pprint import pprint
class MinoriShows:
    def __init__(self, db='database.db'):
        self.db = db
        self.connection = sqlite3.connect(self.db)
        self.logger = logging.getLogger('Minori')

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def initialize(self):
        self.connection.execute('''CREATE TABLE IF NOT EXISTS shows
             (name text primary key, max_episodes integer, most_recent_episode integer,\
                     keywords text, date_added timestamp)''')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS rss
             (name text primary key, url text, date_added timestamp)''')
        self.logger.info("Initialized database")

    def add_show(self, name, max_ep, keywords, current=0):
        date = datetime.datetime.now()
        sql_statement = 'INSERT INTO shows VALUES (?, ?, ?, ?, ?)'
        try:
            self.connection.execute(sql_statement, (name, int(max_ep), int(current), keywords, date))
        except sqlite3.IntegrityError:
            self.logger.warning("Show already exists in database")
            return
        self.logger.info("Added show!")

    def rm_show(self, name):
        sql_statement = 'DELETE FROM shows WHERE name=?'
        try:
            for i in name:
                self.connection.execute(sql_statement, (i,))
        except sqlite3.IntegrityError:
            self.logger.warning("Show doesn't exist in database")
            return
        self.logger.info("Removed show!")

    def get_all_shows(self):
        try:
            sql_statement = 'SELECT * FROM shows'
            shows = [r for r in self.connection.execute(sql_statement)]
            print("SHOWNAME | MAX_EPS | CURRENT_EP | DATE_ADDED")
            pprint(shows)
        except sqlite3.OperationalError:
            self.logger.error("Database not initialized")
