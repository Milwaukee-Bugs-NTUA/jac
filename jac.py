#!/usr/bin/env python3
import click
from pyfiglet import Figlet
import subprocess as sp

def main():
    f = Figlet(font='slant')
    click.echo(f.renderText('J. A. C.'))
    click.echo("🎯 Just Another Chord implementation. 🎯\n")
    while True:
        try:
            command = click.prompt(click.style("jac-cli@ntua",fg='cyan'),type=str,prompt_suffix=': ')
            sp.run(['./cli.py'] + command.split(' '))
            if command == "depart":
                click.echo("\n\nExiting jac cli")
                exit(0)
        except click.Abort:
            # Need to call depart command
            click.echo("\n\nExiting jac cli")
            exit(0)

if __name__ == "__main__":
    main()
