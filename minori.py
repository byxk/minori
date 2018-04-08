#!/usr/bin/env python3

import sys
import logging
import shelve
import click
import feedparser

logging.basicConfig(filename='minori.log',
                    filemode='a',
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger('Minori')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
logger.addHandler(ch)

# TODO: move these later
IN_PROGRESS = 0
FINISHED = 1


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

        except Exception as e:
            logger.error("Unable to parse feed, is it valid?")

        logger.info("Added feed!")

    def add_show(self, name, title_format, feed, max_eps=25, current_ep=0):
        if feed not in self.db['feeds'].keys():
            logger.error("Feed {} not found, please add it first".format(feed))
            return

        self.db['shows'][name] = {'title_format': title_format,
                                  'feed': feed,
                                  'max_eps': max_eps,
                                  'current_ep': current_ep,
                                  'status': IN_PROGRESS}
        logger.info("Added show!")

    def check_for_shows():
        ''' 1. gather shows that are in progress
            2. for each show, assemble the title_format
            3. use the associated feed to check for a link
            4. gather all links, and pass that over the downloader
        '''
        pass


@click.group()
@click.option('--db', default='db.shelve', help='name of db')
@click.pass_context
def cli(ctx, db):
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj['db'] = db


@cli.command()
@click.pass_context
def list_shows(ctx):
    with MinoriDatabase(ctx.obj['db']) as m:
        logger.info("Shows:")
        logger.info(m.get_shows())


@cli.command()
@click.argument('name')
@click.argument('title_format')
@click.argument('feed')
@click.option('--max-eps',  default=-1, help='max # of eps if known, default is -1')
@click.option('--current-ep', default=0, help='episode currently on, e.g default 0 (not started)')
@click.pass_context
def add_show(ctx, name, title_format, feed, max_eps, current_ep):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.add_show(name, title_format, feed, max_eps=max_eps, current_ep=current_ep)


@cli.command()
@click.pass_context
def list_feeds(ctx):
    with MinoriDatabase(ctx.obj['db']) as m:
        logger.info("Feeds:")
        logger.info(m.get_feeds())


@cli.command()
@click.argument('title')
@click.argument('url')
@click.argument('dl_command')
@click.option('--feed-path', default='', help='advanced usage: feedparser path to link')
@click.pass_context
def add_feed(ctx, title, url, dl_command, feed_path):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.add_feed(title, url, dl_command, feed_path)


@cli.command()
@click.pass_context
def list_dl_commands(ctx):
    with MinoriDatabase(ctx.obj['db']) as m:
        logger.info("Commands:")
        logger.info(m.get_dl_commands())


@cli.command()
@click.pass_context
@click.argument('name')
@click.argument('dl_command')
def add_dl_command(ctx, name, dl_command):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.add_dl_command(name, dl_command)
