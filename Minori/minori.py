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
    def __init__(self, db=None, actions=[]):
        self.db = shelve.open(db if db else 'db.shelve', 'c', writeback=True)

        if 'version' not in self.db.keys():
            # init
            self.db['version'] = 1
            self.db['shows'] = {}
            self.db['feeds'] = {}

        self.actions = actions
        self.vars = {'ep_no': '@@EP_VAR@@',
                     'link': '@@LINK_VAR@@',
                     'name': '@@SHOW_NAME@@'}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.sync()
        self.db.close()

    def mvars(self, string: str, show_ctx: dict) -> str:
        """ takes a string and performs a bunch of .replace()
            gotta be a better way to do this... """
        new_string = string
        for key in show_ctx.keys():
            mvar = self.vars[key]
            new_string = new_string.replace(mvar, show_ctx[key])
        return new_string

    def get_shows(self) -> dict:
        return self.db.get('shows')

    def get_feeds(self) -> dict:
        return self.db.get('feeds')

    def add_feed(self, title: str, url: str, path: str):
        # $ENTRY_NO should be a variable
        try:
            feed_path = path.split(',')
            feed = feedparser.parse(url)
            self.db['feeds'][title] = {'url': url,
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

    def rm_feed(self, name: str):
        try:
            del self.db['feeds'][name]
            logger.info('Feed deleted')
        except KeyError:
            logger.error('Feed not in database')
            pass

    def rm_show(self, name: str):
        try:
            del self.db['shows'][name]
            logger.info('Show deleted')
        except KeyError:
            logger.error('Show not in database')
            pass

    def add_show(self, name: str, title_format: str, feed: str, max_eps: int, current_ep: int):
        if feed not in self.db['feeds'].keys():
            logger.warning("Warning, no feed provided, will not be checked for new episodes")
            return

        self.db['shows'][name] = {'title_format': title_format,
                                  'feed': feed,
                                  'max_eps': max_eps,
                                  'current_ep': current_ep,
                                  'status': IN_PROGRESS if max_eps != current_ep else FINISHED}
        logger.info("Added show {}".format(name))

    def check_for_shows(self):
        ''' 1. gather shows that are in progress
            2. for each show, assemble the title_format
            3. use the associated feed to check for a link
            4. gather all links, and pass that over the downloader
        '''
        for show, info in self.db['shows'].items():
            if info['status'] == IN_PROGRESS and info['feed'] is not None:
                search_title = self.mvars(info['title_format'],
                                          {'ep_no': '{0:02d}'.format(int(info['current_ep']) +
                                                                     1)})
                logger.info('Looking for {} with title_format {}'.format(show,
                                                                         search_title))
                feed_info = self.db['feeds'][info['feed']]
                feed = feedparser.parse(feed_info['url'])
                # default search
                for entry in feed['entries']:
                    if entry['title'] == search_title:
                        logger.info('Found entry for {}'.format(show))

                        # construct context
                        context = {'show_name': show,
                                   'feed_name': info['feed'],
                                   'dl_link': entry['link'],
                                   'show_no': info['current_ep'] + 1,
                                   'feed_show_title': entry['title']}
                        try:
                            for action in self.actions:
                                action.execute(self.db, context)
                        except Exception as e:
                            logger.error("Error kicking off action {}".format(str(action)))
                            raise e
                        finally:
                            # increment
                            self.db['shows'][show]['current_ep'] += 1
                            if self.db['shows'][show]['current_ep'] == self.db['shows'][show]['max_eps']:
                                self.db['shows'][show]['status'] = FINISHED

                            logger.info("Finished all actions for {}".format(show))
