#!/usr/bin/env python3
import logging
import datetime
import sqlite3
from pprint import pprint

import feedparser


class MinoriRss:
    def __init__(self, db='database.db'):
        self.db = db
        self.connection = sqlite3.connect(self.db)
        self.logger = logging.getLogger('Minori')

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def add_rss(self, name, url):
        date = datetime.datetime.now()
        sql_statement = 'INSERT INTO rss VALUES (?, ?, ?)'
        try:
            self.connection.execute(sql_statement, (name, url, date))
        except sqlite3.IntegrityError:
            self.logger.warning("RSS already exists in database")
            return
        self.logger.info("Added RSS")

    def rm_rss(self, name):
        sql_statement = 'DELETE FROM rss WHERE name=?'
        try:
            for i in name:
                self.connection.execute(sql_statement, (i,))
        except sqlite3.IntegrityError:
            self.logger.warning("RSS doesn't exist in database")
            return
        self.logger.info("Removed RSS")

    def get_all_rss(self):
        try:
            sql_statement = 'SELECT * FROM rss'
            rss = [{'name': n,
                    'url': url} for (n, url) in self.connection.execute(sql_statement)]
            return rss
        except sqlite3.OperationalError:
            self.logger.error("Database not initialized")
