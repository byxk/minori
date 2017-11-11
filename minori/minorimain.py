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
        self.logger = logging.getLogger('Minori')
        config = configparser.ConfigParser()
        config.read('minori.conf')
        self.config = config['MINORI']
        self.scan_interval = self.config.getint('ScanInterval', 3600)
        self.download_hook = self.config.get('DownloadHook', None)

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
        if self.download_hook:
            self._exec(self._replace_text(self.download_hook, replace_text))
            self.logger.info("Kicking off DownloadHook...")

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
            update_statement = 'UPDATE shows SET most_recent_episode=? WHERE name=?'
            self.logger.info("Added {} to downloads".format(i['show_title']))
            with MinoriDatabase() as md:
                md.execute(update_statement, (i['current'], i['user_title']))
            self._download_shows(i)

    def minorin(self):
        self.logger.debug("Starting watch...")
        while True:
            self.download()
            self.logger.debug("Done download, sleeping for {}".format(self.scan_interval))
            time.sleep(self.scan_interval)
