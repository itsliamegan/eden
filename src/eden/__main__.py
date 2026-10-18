import sys

from luna.cli import Program

from .commands import Build, New, Serve


class Eden(Program):
	name = "eden"
	commands = (New, Build, Serve)


def main():
	Eden.main(sys.argv)


if __name__ == "__main__":
	main()
