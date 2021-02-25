import argparse

from src import workspace

PROJECT_NAME = "template"


def main():
    logger.info("main")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(PROJECT_NAME)
    parser.add_argument('-w', '--workspace', help='Workspace Path')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    gen_config_parser = subparsers.add_parser('gen-config', help='Generate Configuration')
    run_parser = subparsers.add_parser('run', help='run help')

    args = parser.parse_args()

    print(args.__dict__)

    if args.command == 'gen-config':
        w = workspace.Workspace(args.workspace, PROJECT_NAME)
        config = workspace.Config()
        w.set_config(config)
    elif args.command == 'run':
        w = workspace.Workspace(args.workspace, PROJECT_NAME)
        logger = w.get_logger()
        logger.info("Start Running")
        main()
