#!/usr/bin/env python3
import click
import shelve
import logging
import subprocess


logger = logging.getLogger('Minori')


class Action:
    def __init__(self, db: shelve, context: dict):
        self.context = context
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def get_dl_commands(self) -> dict:
        return self.db.get('dl_commands', {})

    def add_dl_command(self, name: str, dl_command: str, feed: str) -> dict:
        self.db['dl_commands'][name] = {'cmd': dl_command,
                                        'feed': feed}
        logger.info("Added command {}".format(name))

    def rm_dl_command(self, name: str):
        try:
            del self.db['dl_commands'][name]
            logger.info('Command deleted')
        except KeyError:
            logger.error('Command not in database')
            pass

    def download(self):
        dl_cmd = ''
        for cmd, cmd_info in self.db['dl_commands'].items():
            if cmd_info['feed'] == self.context['feed_name']:
                dl_cmd = cmd_info['cmd']
                break
        if dl_cmd == '':
            # find the first generic cmd
            for cmd, cmd_info in self.db['dl_commands'].items():
                if cmd_info['feed'] == '':
                    dl_cmd = cmd_info['cmd']
                    break

        if dl_cmd == '':
            # give up
            logger.debug('No command found for feed {}'.format(self.context['feed_name']))
            return
        dl_cmd = dl_cmd.replace("@@LINK_VAR@@", self.context['dl_link'])
        dl_cmd = dl_cmd.replace("@@EP_NAME@@", self.context['feed_show_title'])
        logger.info('Download command: {}'.format(dl_cmd))
        # TODO: run this through a string replacer?
        stdout = subprocess.check_output(
            [dl_cmd],
            shell=True)
        logger.info(stdout)


def execute(db, context):
    if 'dl_commands' not in db.keys():
        db['dl_commands'] = {}
    with Action(db, context) as a:
        a.download()


@click.group()
@click.pass_context
def manage_dl(ctx):
    with shelve.open(ctx.obj['db'], writeback=True) as db:
        if 'dl_commands' not in db.keys():
            db['dl_commands'] = {}
        pass


@manage_dl.command()
@click.argument('name')
@click.pass_context
def rm_dl(ctx, name):
    with shelve.open(ctx.obj['db'], writeback=True) as db:
        with Action(db, {}) as a:
            a.rm_dl_command(name)


@manage_dl.command()
@click.pass_context
@click.argument('name')
@click.argument('dl_command')
@click.option('--feed', default='', help='feed to attach download command to')
def add_dl(ctx, name, dl_command, feed):
    with shelve.open(ctx.obj['db'], writeback=True) as db:
        with Action(db, {}) as a:
            a.add_dl_command(name, dl_command, feed)


@manage_dl.command()
@click.pass_context
def list_dl(ctx):
    with shelve.open(ctx.obj['db'], writeback=True) as db:
        with Action(db, {}) as a:
            logger.info("Commands:")
            logger.info(a.get_dl_commands())


def early_execute(cli):
    """ cli is the top level click command """
    cli.add_command(manage_dl)
