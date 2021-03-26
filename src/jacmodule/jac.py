#!/usr/bin/env python

import click
import cmd
from pyfiglet import Figlet
import socket
import sys
import requests
import shlex
import os

import cli

def shlex_friendly(string):
    
    found = False
    l = list(string)

    n = string.count("'")
    if n == 1:
        return string.replace("'", "")
    else:

        for index, s in enumerate(l):
            if s == "'":
                if found == False:
                    found = True
                    first = index
                else:
                    last = index

    l[first] = '"'
    l[last] = '"'
    return "".join(l).replace("'", "")

class JacShell(cmd.Cmd):

    prompt = click.style("jac-cli@ntua",fg='cyan') + "$ "

    def do_help(self, line):
        # Don't use default help of cmd library
        self.default("help " + line)

    def do_exit(self, line):
        #Not working for edge case
        self.default("exit " + line)
        click.echo("Exiting jac shell...")
        return True

    def default(self, line):
        try:
            args = shlex.split(line)
        except ValueError:
            args = shlex.split(shlex_friendly(line))
        subcommand = cli.cli_group.commands.get(args[0])
        if subcommand:
            try:
                subcommand.main(args[1:],prog_name=args[0],standalone_mode = False)
            except click.NoSuchOption as option_error:
                option_error.show()
            except click.BadOptionUsage as bad_option:
                bad_option.show()
            except click.BadArgumentUsage as bad_argument:
                bad_argument.show()
            except click.UsageError as usage_error:
                usage_error.show()
            except click.BadParameter as bad_parameter:
                bad_parameter.show()
            except click.FileError as file_error:
                file_error.show()
            except click.Abort:
                click.echo("Command ended unexpectedly")
            except NotImplementedError:
                click.echo("Not Implemented Yet")

        else:
            return cmd.Cmd.default(self, line)

    # For using Ctrl-D as exit shortcut
    do_EOF = do_exit

def port_in_use(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0

def start_server(kfactor, consistency_type):
    ip = socket.gethostbyname(socket.gethostname())
    # Find available port
    port = None
    for p in range(5000,5100):
        if port_in_use(ip, p) == 0:
            port = p
            break

    if port == None:
        click.echo("Couldn't find available port for jac server.")
        click.echo("Please try again later. Exit program with ctrl + C")
        return False

    # Set enviromentals for cli commands
    os.environ['JACSERVER_IP'] = ip
    os.environ['JACSERVER_PORT'] = str(port)

    pid = os.fork()
    if pid == 0:
        os.execle("./server.py","server.py",str(port),str(kfactor),consistency_type,os.environ)
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
    
    return True

def check_jac_parameters():

    if len(sys.argv) < 2:
        return 1,""

    try:
        kfactor = int(sys.argv[1])
    except ValueError:
        click.echo("k factor must be a positive integer!")
        exit()

    if kfactor <= 0:
        click.echo("k factor must be a positive integer!")
        exit()
    elif kfactor == 1:
        return kfactor,""
    elif len(sys.argv) < 3:
        click.echo("Please, provide a consistency policy:")
        click.echo("(*) chain-replication (*) eventually")
        exit()
    else:
        consistency_type = sys.argv[2]
        if not consistency_type in {"chain-replication","eventually"}:
            click.echo("Not supported policy!")
            exit()
        return kfactor,consistency_type

def main():

    kfactor, consistency_type = check_jac_parameters()

    f = Figlet(font='slant')
    click.echo(f.renderText('J. A. C.'))
    click.echo("🎯 Just Another Chord implementation. 🎯\n")

    if not start_server(kfactor, consistency_type):
        exit() 
    jacshell = JacShell()
    try:
        jacshell.cmdloop()
    except KeyboardInterrupt:
        jacshell.do_exit(None)

if __name__ == "__main__":
    main()
