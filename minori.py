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


class MinoriDatabase:
    def __init__(self, db=None):
        self.db = shelve.open(db, 'c', writeback=True) if db else shelve.open('db.shelve', 'c', writeback=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.sync()
        self.db.close()

    def get_dl_commands(self) -> dict:
        return self.db.get('dl_commands', {})

    def add_dl_command(self, name, dl_command) -> dict:
        if 'dl_commands' not in self.db.keys():
            self.db['dl_commands'] = {}
        self.db['dl_commands'][name] = dl_command
        logger.info("Added command!")


    def get_shows(self) -> dict:
        return self.db.get('shows', {})

    def get_feeds(self) -> dict:
        return self.db.get('feeds', {})

    def add_feed(self, title, url, dl_command):
        if dl_command not in self.db['dl_commands'].keys():
            logger.error("dl_command {} not found, please add it first".format(dl_command))
            return
        try:
            feed = feedparser.parse(url)
            if 'feeds' not in self.db.keys():
                self.db['feeds'] = {}

            self.db['feeds'][title] = { 'url': url,
                                        'dl_command': dl_command }
        except Exception as e:
            import pdb;pdb.set_trace()


        logger.info("Added feed!")

    def add_show(self, max_eps=25, current_ep=1, keywords=[]):
        logger.info("Added show!")
        pass


@click.group()
@click.option('--db', default='db.gnu', help='name of db')
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
@click.pass_context
def list_feeds(ctx):
    with MinoriDatabase(ctx.obj['db']) as m:
        logger.info("Feeds:")
        logger.info(m.get_feeds())


@cli.command()
@click.argument('title')
@click.argument('url')
@click.argument('dl_command')
@click.pass_context
def add_feed(ctx, title, url, dl_command):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.add_feed(title, url, dl_command)

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
