#!/usr/bin/env python3

import sqlite3
import datetime
import logging
from .minoridb import MinoriDatabase


class MinoriShows:
    def __init__(self, db='database.db'):
        self.logger = logging.getLogger('Minori')

    def add_show(self, name, max_ep, keywords, current=0):
        date = datetime.datetime.now()
        sql_statement = 'INSERT INTO shows VALUES (?, ?, ?, ?, ?)'
        try:
            with MinoriDatabase() as md:
                md.execute(sql_statement, (name, int(max_ep), int(current), keywords, date))
        except sqlite3.IntegrityError:
            self.logger.warning("Show already exists in database")
            return
        self.logger.info("Added show!")

    def rm_show(self, name):
        # TODO: do remove properly, check all databases. (use sql relations here?)
        shows_sql_statement = 'DELETE FROM shows WHERE name=?'
        download_sql_statement = 'DELETE FROM downloads WHERE name=?'
        try:
            for i in name:
                with MinoriDatabase() as md:
                    md.execute(shows_sql_statement, (i,))
                    md.execute(download_sql_statement, (i,))
        except sqlite3.IntegrityError:
            self.logger.warning("Show doesn't exist in database")
            return
        self.logger.info("Removed show!")

    def get_all_shows(self):
        try:
            sql_statement = 'SELECT * FROM shows'
            shows = [{'name': n,
                      'max_ep': m,
                      'current': r,
                      'keywords': k,
                      'date_added': d} for (n, m, r, k, d) in MinoriDatabase().execute(sql_statement)]
            return shows
        except sqlite3.OperationalError:
            self.logger.error("Database not initialized")
