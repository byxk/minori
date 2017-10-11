#!/usr/bin/env python3

import logging
from .minorirss import MinoriRss
from .minorishows import MinoriShows


class MinoriMain:
    def __init__(self):
        self.logger = logging.getLogger('Minori')

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

            # TODO: do we short circuit on first find?
            for feed in rss:
                rss_name = feed['rss']
                rss_show_title = feed['name']
                if all(keyword in rss_show_title for keyword in keywords):
                    compiled.append({'rss_name': rss_name,
                                     'show_title': rss_show_title,
                                     'link': feed['link']})
                    break

        self.logger.debug("Compiled a filtered list of length {}".format(len(compiled)))
        return compiled
