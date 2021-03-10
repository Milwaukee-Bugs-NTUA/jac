#!/usr/bin/env python

import click
import cmd
from pyfiglet import Figlet
import socket
import requests
import os

import cli

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
        args = line.split()
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

def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((cli.ip, port)) == 0

def start_server():
    # Find available port
    for p in range(5000,5100):
        if port_in_use(p) == 0:
            cli.port = p
            break

    if cli.port == None:
        click.echo("Couldn't find available port for jac server.")
        click.echo("Please try again later")
        return False

    pid = os.fork()
    if pid == 0:
        os.execle("./server.py","server.py",str(cli.port),os.environ)
        # Unreachable statement. 
        # Executed only if exec fails
        click.echo("Couldn't start jac server")     
    else:
        url = "http://{}:{}/".format(cli.ip,cli.port)
        while True:
            try:
                r = requests.get(url)
                break
            except requests.exceptions.ConnectionError:
                pass
        click.echo(r.text)
    
    return True

def main():
    f = Figlet(font='slant')
    click.echo(f.renderText('J. A. C.'))
    click.echo("🎯 Just Another Chord implementation. 🎯\n")

    if not start_server():
        exit() 
    jacshell = JacShell()
    try:
        jacshell.cmdloop()
    except KeyboardInterrupt:
        jacshell.do_exit(None)

if __name__ == "__main__":
    main()
