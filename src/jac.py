#!/usr/bin/env python3
import click
import cmd
from pyfiglet import Figlet
import subprocess as sp

from cli import *

class JACShell(cmd.Cmd):

    prompt = click.style("jac-cli@ntua",fg='cyan') + "$ "

    def do_help(self, line):
        # Don't use default help of cmd library
        self.default("help " + line)

    def do_exit(self, inp):
        click.echo("\nExiting jac shell...")
        return True

    def default(self, line):
        args = line.split()
        subcommand = cli.commands.get(args[0])
        if subcommand:
            try:
                res = subcommand.main(args[1:],prog_name=args[0],standalone_mode = False)
                if not res == 0:
                    click.echo("Something went wrong")
            except click.UsageError as usage_error:
                usage_error.show()
            except click.BadParameter as bad_parameter:
                bad_parameter.show()
            except click.Abort as abort_error:
                abort_error.show()
            except:
                click.echo("Command ended unexpectedly")
        else:
            return cmd.Cmd.default(self, line)

    # For using Ctrl-D as exit shortcut
    do_EOF = do_exit

def main():
    f = Figlet(font='slant')
    click.echo(f.renderText('J. A. C.'))
    click.echo("🎯 Just Another Chord implementation. 🎯\n")

    jacshell = JACShell()
    try:
        jacshell.cmdloop()
    except KeyboardInterrupt:
        jacshell.do_exit(None)

if __name__ == "__main__":
    main()
