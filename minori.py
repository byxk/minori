#!/usr/bin/env python3

import logging
import shelve
import feedparser

# TODO: move these later
IN_PROGRESS = 0
FINISHED = 1


logger = logging.getLogger('Minori')


class MinoriDatabase:
    # this is just a wrapper for a shelve file...
    def __init__(self, db=None):
        self.db = shelve.open(db if db else 'db.shelve', 'c', writeback=True)

        if 'version' not in self.db.keys():
            # init
            self.db['version'] = 1
            self.db['shows'] = {}
            self.db['feeds'] = {}
            self.db['dl_commands'] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.sync()
        self.db.close()

    def get_dl_commands(self) -> dict:
        return self.db.get('dl_commands', {})

    def add_dl_command(self, name, dl_command) -> dict:
        self.db['dl_commands'][name] = dl_command
        logger.info("Added command {}".format(name))

    def get_shows(self) -> dict:
        return self.db.get('shows')

    def get_feeds(self) -> dict:
        return self.db.get('feeds')

    def add_feed(self, title, url, dl_command, path):
        # $ENTRY_NO should be a variable
        if dl_command not in self.db['dl_commands'].keys():
            logger.error("dl_command {} not found, please add it first".format(dl_command))
            return
        try:
            feed_path = path.split(',')
            feed = feedparser.parse(url)
            self.db['feeds'][title] = {'url': url,
                                       'dl_command': dl_command,
                                       'feed_path': feed_path}
            # try to see if there's a path to a link
            if path != '':
                start = feed
                for x in range(0, len(feed_path)):
                    if feed_path[x] == "$ENTRY_NO":
                        start = start[0]
                    else:
                        start = feed[feed_path[x]]
                if type(start) != str:
                    logger.error("feed path did not lead to a valid dl string")
                    import pdb
                    pdb.set_trace()
                    return
            else:
                # hope the rss feed follows the usual path of
                # feed, entries, [x], link
                dl_link = feed['entries'][0]['link']
                if type(dl_link) != str:
                    logger.error("no dl string found")
                    import pdb
                    pdb.set_trace()
                    return

        except Exception as e:
            logger.error("Unable to parse feed, is it valid?")
            import pdb
            pdb.set_trace()
            return

        logger.info("Added feed {}".format(title))

    def add_show(self, name, title_format, feed, max_eps, current_ep):
        if feed not in self.db['feeds'].keys():
            logger.error("Feed {} not found, please add it first".format(feed))
            return

        self.db['shows'][name] = {'title_format': title_format,
                                  'feed': feed,
                                  'max_eps': max_eps,
                                  'current_ep': current_ep,
                                  'status': IN_PROGRESS if max_eps != current_ep else FINISHED}
        logger.info("Added show {}".format(name))

    def check_for_shows():
        ''' 1. gather shows that are in progress
            2. for each show, assemble the title_format
            3. use the associated feed to check for a link
            4. gather all links, and pass that over the downloader
        '''
        pass
