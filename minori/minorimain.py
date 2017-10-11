#!/usr/bin/env python3

import logging
import datetime
import sqlite3
from .minorirss import MinoriRss
from .minorishows import MinoriShows


class MinoriMain:
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

        self.connection.execute('''CREATE TABLE IF NOT EXISTS downloads
             (name text primary key, torrent text, date_added timestamp)''')
        self.logger.info("Initialized database")

    def _feed_rss(self, rss, keywords, current):
        for feed in rss:
            rss_name = feed['rss']
            rss_show_title = feed['name']
            if all(keyword in rss_show_title for keyword in keywords):
                return {'rss_name': rss_name,
                        'show_title': rss_show_title,
                        'link': feed['link'],
                        'current': current}
        return None

    def scan_rss(self):
        rss = MinoriRss().parse_rss()
        shows = MinoriShows().get_all_shows()
        compiled = []
        for show in shows:
            keywords = show['keywords'].split(",")
            # first increment the currently watching episode to next
            # then do some padding, eg 1 becomes 01 cause thats the format lol
            keywords.append(str(show['current'] + 1).zfill(len(str(show['max_ep']))))
            keywords.append(show['name'])
            self.logger.debug("Compiled this list of keywords: {}".format(keywords))

            find = self._feed_rss(rss, keywords, show['current'] + 1)
            if find is not None:
                compiled.append(find)

        self.logger.debug("Compiled a filtered list of length {}".format(len(compiled)))
        return compiled

    def download(self):
        to_download = self.scan_rss()
        for i in to_download:
            date = datetime.datetime.now()
            sql_statement = 'INSERT INTO downloads VALUES (?, ?, ?)'
            try:
                self.connection.execute(sql_statement, (i['show_title'], i['link'], date))
                self.logger.info("Added {} to downloads".format(i['show_title']))
                # TODO: kick off link to torrent client
                # TODO: update list in shows to reflect current ep
            except sqlite3.IntegrityError:
                self.logger.debug("Show already exists in downloads")
