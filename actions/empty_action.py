#!/usr/bin/env python3
import click
import shelve
import logging


class Action:
    def __init__(self, context: dict, db: shelve, **kwargs):
        self.context = context
        self.db = db
        self.logger = logging.getLogger('Minori')

    def execute(self, **kwargs):
        self.logger.debug(str(self.context))
        self.logger.debug(str(self.db))

    @staticmethod
    def early_execute(cli):
        """ cli is the top level click command """
        cli.add_command(Action.empty_cmd)

    @staticmethod
    @click.command()
    @click.pass_context
    def empty_cmd(ctx):
        print("weeee")
