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
    global ip, port
    if key == "*":

        url = "http://{}:{}/queryAll".format(ip,port)
        r = requests.get(url)

        if r.status_code == 200:
            keys = r.json()["keys"]
            print(*keys,sep="\n")

    else:
        url = "http://{}:{}/query".format(ip,port)
        r = requests.get(url, params={"key":key})
        click.echo(r.text)

@cli_group.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
@click.argument('value', metavar='<value>')
def insert(key, value):
    """
        Inserts the pair (<key>, <value>).
    """
    global ip, port
    url = "http://{}:{}/insert".format(ip,port)
    r = requests.post(url, params={"key":key,"value":value})
    click.echo(r.text)

@cli_group.command(context_settings=CONTEXT_SETTINGS)
@click.argument('key', metavar='<key>')
def delete(key):
    """
        Deletes the specified <key>.
    """
    global ip, port
    url = "http://{}:{}/delete".format(ip,port)
    r = requests.delete(url, params={"key":key})
    click.echo(r.text)

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

@cli_group.command(context_settings=CONTEXT_SETTINGS)
def info():
    """
        Displays info for current node.
    """
    click.echo("Node Info")
    url = "http://{}:{}/info".format(ip,port)
    r = requests.get(url)
    data = r.json()
    click.echo("== Primary Keys ==")
    print(*data["keys"],sep="\n")
    click.echo("== Replicas Keys ==")
    print(*data["replicas"],sep="\n")
    click.echo("Previous Node")
    click.echo(data["previous"])
    click.echo("Next Node")
    click.echo(data["next"])   

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
