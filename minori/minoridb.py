#!/usr/bin/env python3

import logging
import configparser
import sqlite3


class MinoriDatabase:
    def __enter__(self):
        return self

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('minori.conf')
        self.db_file = str(config['MINORI']['Database']) if str(
            config['MINORI']['Database']) else 'database.db'
        self.logger = logging.getLogger('Minori')
        self.connection = sqlite3.connect(self.db_file)
        self.cur = self.connection.cursor()

    def __exit__(self, *exc):
        self.connection.close()
        return False

    def execute(self, query, args=None):
        """ execute a query on the db

        query = SQL string
        args  = tuple of substitutes for the query
        """
        if args:
            self.cur = self.connection.execute(query, args)
        else:
            self.cur = self.connection.execute(query)
        self.connection.commit()
        return self.cur

    def initialize(self):
            self.execute('''CREATE TABLE IF NOT EXISTS shows
                (name text primary key, max_episodes integer, most_recent_episode integer,\
                keywords text, date_added timestamp)''')
            self.execute('''CREATE TABLE IF NOT EXISTS rss
                (name text primary key, url text, date_added timestamp)''')
            self.logger.info("Initialized database {}".format(self.db_file))
