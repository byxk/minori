#!/usr/bin/env python3

import sys
import logging
import dbm
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
        self.db = dbm.open(db, 'c') if db else dbm.open('db.gnu', 'c')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

    def get_shows(self) -> dict:
        return self.db.get('shows', {})

    def get_feeds(self) -> dict:
        return self.db.get('feeds', {})

    def add_feed(self, title, url, path_to_dl_url):
        import pdb
        pdb.set_trace()

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
@click.argument('dl_url')
@click.pass_context
def add_feed(ctx, title, url, dl_url):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.add_feed(title, url, dl_url)
