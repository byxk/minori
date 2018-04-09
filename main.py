#!/usr/bin/env python3

import logging
import sys
import click
from minori import MinoriDatabase


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


@click.group()
@click.option('--db', default='db.shelve', help='name of db')
@click.pass_context
def cli(ctx, db):
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj['db'] = db


@click.group()
@click.pass_context
def manage_shows(ctx):
    pass


@click.group()
@click.pass_context
def manage_feeds(ctx):
    pass


@click.group()
@click.pass_context
def manage_dl(ctx):
    pass


@manage_shows.command()
@click.pass_context
def list_shows(ctx):
    with MinoriDatabase(ctx.obj['db']) as m:
        logger.info("Shows:")
        logger.info(m.get_shows())


@manage_shows.command()
@click.argument('name')
@click.argument('title_format')
@click.argument('feed')
@click.option('--max-eps',  default=-1, help='max # of eps if known, default is -1')
@click.option('--current-ep', default=0, help='episode currently on, e.g default 0 (not started)')
@click.pass_context
def add_show(ctx, name, title_format, feed, max_eps, current_ep):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.add_show(name, title_format, feed, max_eps=max_eps, current_ep=current_ep)


@manage_shows.command()
@click.argument('name')
@click.pass_context
def rm_show(ctx, name):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.rm_show(name)


@manage_feeds.command()
@click.pass_context
def list_feeds(ctx):
    with MinoriDatabase(ctx.obj['db']) as m:
        logger.info("Feeds:")
        logger.info(m.get_feeds())


@manage_feeds.command()
@click.argument('title')
@click.argument('url')
@click.argument('dl_command')
@click.option('--feed-path', default='', help='advanced usage: feedparser path to link')
@click.pass_context
def add_feed(ctx, title, url, dl_command, feed_path):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.add_feed(title, url, dl_command, feed_path)


@manage_feeds.command()
@click.argument('name')
@click.pass_context
def rm_feed(ctx, name):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.rm_feed(name)


@manage_dl.command()
@click.pass_context
def list_dl(ctx):
    with MinoriDatabase(ctx.obj['db']) as m:
        logger.info("Commands:")
        logger.info(m.get_dl_commands())


@manage_dl.command()
@click.pass_context
@click.argument('name')
@click.argument('dl_command')
def add_dl(ctx, name, dl_command):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.add_dl_command(name, dl_command)


@cli.command()
@click.pass_context
def check_for_shows(ctx):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.check_for_shows()


@manage_dl.command()
@click.argument('name')
@click.pass_context
def rm_dl(ctx, name):
    with MinoriDatabase(ctx.obj['db']) as m:
        m.rm_dl(name)


cli.add_command(manage_shows)
cli.add_command(manage_feeds)
cli.add_command(manage_dl)
