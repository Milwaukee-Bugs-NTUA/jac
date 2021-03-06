#!/usr/bin/env python

import click
import requests
import socket
import os
import time

CONTEXT_SETTINGS = dict(help_option_names=['--help','-h'])
ip = socket.gethostbyname(socket.gethostname())
port = None

def port_in_use(port):
    global ip
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0

@click.group(add_help_option=False,options_metavar="",subcommand_metavar="COMMAND [OPTIONS] [ARGS]")
def cli():
    pass

@cli.command(context_settings=CONTEXT_SETTINGS)
def join():
    """
        Inserts a new node.
    """
    global port
    # Find available port
    for p in range(5000,5100):
        if port_in_use(p) == 0:
            port = p
            break
    
    if port == None:
        click.echo("Could find available port. Couldn't start jac server.")
        return

    pid = os.fork()
    if pid == 0:
        os.execle("./server.py","server.py",str(port),os.environ)
        # Unreachable statement. 
        # Executed only if exec fails
        click.echo("Couldn't start jac server")     
    else:
        url = "http://{}:{}/".format(ip,port)
        while True:
            try:
                r = requests.get(url)
                break
            except requests.exceptions.ConnectionError:
                pass
        click.echo(r.text)

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
    # Need to fix address
    global port
    ip = socket.gethostbyname(socket.gethostname())
    url = "http://{}:{}/shutdown".format(ip,port)
    requests.post(url)
    click.echo("Departure of node")

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
