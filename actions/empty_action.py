#!/usr/bin/env python3
import click
import logging


logger = logging.getLogger('Minori')


def execute(*args, **kwargs):
    logger.info("empty execute")


def early_execute(cli):
    """ cli is the top level click command """
    cli.add_command(empty_cmd)


@click.command()
@click.pass_context
def empty_cmd(ctx):
    print("weeee")
