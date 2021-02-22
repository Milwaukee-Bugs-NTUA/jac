#!/usr/bin/env python3
import click

@click.group()
def cli():
    pass

@cli.command()
def join():
    click.echo("New node joined")
    raise NotImplementedError

@cli.command()
@click.argument('key')
def query(key):
    click.echo("Query for key {}".format(key))
    raise NotImplementedError

@cli.command()
@click.argument('key')
@click.argument('value')
def insert(key, value):
    click.echo("Insert key {} with value {}".format(key,value))
    raise NotImplementedError

@cli.command()
@click.argument('key')
def delete(key):
    click.echo("Delete key {}".format(key))
    raise NotImplementedError

@cli.command()
def depart():
    click.echo("Departure of node")
    raise NotImplementedError

@cli.command()
def overlay():
    click.echo("Overlay")
    raise NotImplementedError

#   Dummy command, just for
#   showing up in cli help message
@cli.command()
def help():
    """
        Prints this help message and exits.
    """
    pass

if __name__ == "__main__":
    cli()
