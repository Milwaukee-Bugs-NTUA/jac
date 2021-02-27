#!/usr/bin/env python3
import click
import cmd
from pyfiglet import Figlet
import subprocess as sp

from cli import *

class JacShell(cmd.Cmd):

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

def main():
    f = Figlet(font='slant')
    click.echo(f.renderText('J. A. C.'))
    click.echo("🎯 Just Another Chord implementation. 🎯\n")

    jacshell = JacShell()
    try:
        jacshell.cmdloop()
    except KeyboardInterrupt:
        jacshell.do_exit(None)

if __name__ == "__main__":
    main()
