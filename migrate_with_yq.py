
import argparse
import sys
import migrate
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(asctime)s:%(message)s")
logger = logging.getLogger("migration-with-yq")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inplace", action="store_true", help="Set --inplace command line option.")
    args = parser.parse_args()

    try:
        diff = migrate.convert_difference(sys.stdin.read())
        commands = migrate.generate_yq_commands(diff)
        for cmd in commands:
            print(cmd)
    except Exception as e:
        logger.exception("failed to generate yq commands: %r", e)


if __name__ == "__main__":
    main()
