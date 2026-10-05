import sys

from luna.cli import Program

from .commands import Build, Create


class Eden(Program):
	name = "eden"
	commands = (Build, Create)


def main():
	Eden.main(sys.argv)
