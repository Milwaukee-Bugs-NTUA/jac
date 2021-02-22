#!/usr/bin/env python3
import click

CONTEXT_SETTINGS = dict(help_option_names=['--help','-h'])

@click.group(add_help_option=False,options_metavar="",subcommand_metavar="COMMAND [OPTIONS] [ARGS]")
def cli():
    pass

@cli.command(context_settings=CONTEXT_SETTINGS)
def join():
    """
        Inserts a new node.
    """
    click.echo("New node joined")
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
def query(key):
    """
        Finds the value of <key>.
    """
    click.echo("Query for key {}".format(key))
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
@click.argument('value', metavar='<value>')
def insert(key, value):
    """
        Inserts the pair (<key>, <value>).
    """
    click.echo("Insert key {} with value {}".format(key,value))
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
def delete(key):
    """
        Deletes the specified <key>.
    """
    click.echo("Delete key {}".format(key))
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
def depart():
    """
        Makes current node to depart.
    """
    click.echo("Departure of node")
    raise NotImplementedError

@cli.command(context_settings=CONTEXT_SETTINGS)
def overlay():
    """
        Displays current network topology.
    """
    click.echo("Overlay")
    raise NotImplementedError

#   Dummy command, just for
#   showing up in cli help message
@cli.command(context_settings=CONTEXT_SETTINGS, short_help="Prints this message and exits.")
def help():
    """
        Prints a help message for all jac commands.
    """
    with click.Context(cli) as ctx:
        click.echo(cli.get_help(ctx))
    return 0

if __name__ == "__main__":
    cli()
