#!/usr/bin/env python

import click
import requests
import socket
import os
import time

CONTEXT_SETTINGS = dict(help_option_names=['--help','-h'])
ip = socket.gethostbyname(socket.gethostname())
port = None

@click.group(add_help_option=False,options_metavar="",subcommand_metavar="COMMAND [OPTIONS] [ARGS]")
def cli_group():
    pass

@cli_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('-b','--bootstrap-node','bnode',required=False, nargs=2,type=str,metavar='<ip> <port>', help='Specify bootstrap node of chord')
def join(bnode):
    """
        Inserts a new node.
    """
    global ip, port
    url = "http://{}:{}/".format(ip,port)
    if not bnode == ():
        with open(".jacserver.cfg","w") as f:
                f.write("{} {}".format(bnode[0],bnode[1]))
        params = {'ip' : bnode[0], 'port' : bnode[1]}
    else:
        if os.path.exists(".jacserver.cfg"):
            with open(".jacserver.cfg","r") as f:
                line = f.readline().split()
                if line == []:
                    click.echo("Please provide a bootstrap node")
                    return
                bnode_ip = line[0]
                bnode_port = line[1]
            params = {'ip' : bnode_ip, 'port' : bnode_port}
        else:
            click.echo("Please provide a bootstrap node")
            return
    
    r = requests.put(url + "join", params=params)
    click.echo(r.text)

@cli_group.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
def query(key):
    """
        Finds the value of <key>.
    """
    click.echo("Query for key {}".format(key))
    raise NotImplementedError

@cli_group.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
@click.argument('value', metavar='<value>')
def insert(key, value):
    """
        Inserts the pair (<key>, <value>).
    """
    click.echo("Insert key {} with value {}".format(key,value))
    raise NotImplementedError

@cli_group.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
def delete(key):
    """
        Deletes the specified <key>.
    """
    click.echo("Delete key {}".format(key))
    raise NotImplementedError

@cli_group.command(context_settings=CONTEXT_SETTINGS)
def depart():
    """
        Makes current node to depart.
    """
    global ip, port
    url = "http://{}:{}/depart".format(ip,port)
    r = requests.delete(url)
    click.echo(r.text)

@cli_group.command(context_settings=CONTEXT_SETTINGS)
def exit():
    """
        Makes current node to depart & exits from shell.
    """
    global ip, port
    url = "http://{}:{}/shutdown".format(ip,port)
    r = requests.post(url)
    click.echo(r.text)

@cli_group.command(context_settings=CONTEXT_SETTINGS)
def overlay():
    """
        Displays current network topology.
    """
    click.echo("Chord Architecture")
    url = "http://{}:{}/overlay".format(ip,port)
    r = requests.get(url)
    click.echo(r.text)

#   Dummy command, just for
#   showing up in cli help message
@cli_group.command(context_settings=CONTEXT_SETTINGS, short_help="Prints this message and exits.")
def help():
    """
        Prints a help message for all jac commands.
    """
    with click.Context(cli_group) as ctx:
        click.echo(cli_group.get_help(ctx))
    return 0

if __name__ == "__main__":
    cli_group()
