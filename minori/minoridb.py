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
        self.logger.debug('Connecting to db file {}'.format(self.db_file))
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
            self.connection.execute(query, args)
        else:
            self.connection.execute(query)
        self.connection.commit()
        return self.cur
