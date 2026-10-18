import sys

from luna.cli import Program

from .commands import New


class Eden(Program):
	name = "eden"
	commands = (New,)


def main():
	Eden.main(sys.argv)


if __name__ == "__main__":
	main()
