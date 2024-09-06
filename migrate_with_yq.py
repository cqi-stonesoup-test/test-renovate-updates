
import argparse
import sys
import migrate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inplace", action="store_true", help="Set --inplace command line option.")
    args = parser.parse_args()

    diff = migrate.convert_difference(sys.stdin.read())
    yq_expressions = migrate.generate_yq_commands(diff)

    opts = "-i" if args.inplace else ""
    for expr in yq_expressions:
        cmd = f"yq {opts} e '{expr}' \"$pipeline\""
        print(cmd)


if __name__ == "__main__":
    main()
