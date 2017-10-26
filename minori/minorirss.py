#!/usr/bin/env python3
import logging
import datetime
import sqlite3
import feedparser
from .minoridb import MinoriDatabase


class MinoriRss:
    def __init__(self):
        self.logger = logging.getLogger('Minori')

    def add_rss(self, name, url):
        date = datetime.datetime.now()
        sql_statement = 'INSERT INTO rss VALUES (?, ?, ?)'
        try:
            with MinoriDatabase()
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
                    'url': url,
                    'timestamp': t} for (n, url, t) in self.connection.execute(sql_statement)]
            return rss
        except sqlite3.OperationalError:
            self.logger.error("Database not initialized")

    # attempt to gather all rss feeds into a list of dicts {title, link, rss_title}
    def parse_rss(self):
        rss = self.get_all_rss()
        compiled = []
        for feed in rss:
            parsed = feedparser.parse(feed['url'])
            self.logger.debug("Parsed feed {} with {} entries".format(parsed.feed.title,
                                                                      len(parsed.entries)))
            for entry in parsed.entries:
                compiled.append({"rss": parsed.feed.title,
                                 "name": entry.title,
                                 "link": entry.link})
        self.logger.debug("Parsed all entries, ended up with compiled length {}"
                          .format(len(compiled)))
        return compiled
