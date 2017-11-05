#!/usr/bin/env python3

import logging
import datetime
import time
import sqlite3
import subprocess
import configparser
from .minorirss import MinoriRss
from .minorishows import MinoriShows
from .minoridb import MinoriDatabase


class MinoriMain:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('minori.conf')
        self.logger = logging.getLogger('Minori')
        self.scan_interval = int(config['MINORI']['ScanInterval'])
        self.download_exec = str(config['MINORI']['DownloadExec'])
        self.download_pre = str(config['MINORI']['DownloadPre'])
        self.download_post = str(config['MINORI']['DownloadPost'])

    def _exec(self, command):
        subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True)
        return

    def _replace_text(self, text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text

    def _download_shows(self, info):
        # TODO: document this dictionary of variables
        replace_text = {"$LINK": info['link'],
                        "$TITLE": info['show_title']
                        }
        self.logger.info("Kicking off DownloadPre...")
        self._exec(self._replace_text(self.download_pre, replace_text))
        self.logger.info("Kicking off DownloadExec...")
        self._exec(self._replace_text(self.download_exec, replace_text))
        self.logger.info("Kicking off DownloadPost...")
        self._exec(self._replace_text(self.download_post, replace_text))

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
                find['user_title'] = show['name']
                compiled.append(find)

        self.logger.debug("Compiled a filtered list of length {}".format(len(compiled)))
        return compiled

    def download(self):
        to_download = self.scan_rss()
        for i in to_download:
            date = datetime.datetime.now()
            insert_statement = 'INSERT INTO downloads VALUES (?, ?, ?)'
            update_statement = 'UPDATE shows SET most_recent_episode=? WHERE name=?'
            try:
                # TODO: move download stuff into its own module? support other stuff?
                self.logger.info("Added {} to downloads".format(i['show_title']))
                with MinoriDatabase() as md:
                    md.execute(update_statement, (i['current'], i['user_title']))
                    md.execute(insert_statement, (i['user_title'], i['link'], date))
                self._download_shows(i)
            except sqlite3.IntegrityError as e:
                self.logger.debug("{} already in downloads database, skipping."
                                  .format(i['show_title']))

    def minorin(self):
        self.logger.debug("Starting watch...")
        while True:
            self.download()
            self.logger.debug("Done download, sleeping...")
            time.sleep(self.scan_interval)
