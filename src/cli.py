#!/usr/bin/env python3
import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(add_help_option=False,options_metavar="",subcommand_metavar="COMMAND [OPTIONS] [ARGS]")
def cli():
    pass

@cli.command(context_settings=CONTEXT_SETTINGS)
def join():
    """
        Inserts a new node
    """
    click.echo("New node joined")
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
def query(key):
    """
        Find the value of <key>
    """
    click.echo("Query for key {}".format(key))
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
@click.argument('value', metavar='<value>')
def insert(key, value):
    """
        Inserts the pair (<key>, <value>)
    """
    click.echo("Insert key {} with value {}".format(key,value))
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
def delete(key):
    """
        Deletes the specified <key>
    """
    click.echo("Delete key {}".format(key))
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
def depart():
    """
        Makes current node to depart
    """
    click.echo("Departure of node")
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
def overlay():
    """
        Displays current network topology
    """
    click.echo("Overlay")
    raise NotImplementedError

#   Dummy command, just for
#   showing up in cli help message
@cli.command(add_help_option=False)
def help():
    """
        Prints this help message and exits.
    """
    with click.Context(cli) as ctx:
        click.echo(cli.get_help(ctx))

if __name__ == "__main__":
    cli()
