import argparse

from src import workspace

PROJECT_NAME = "template"


def main():
    w = workspace.Workspace()
    logger.info("main")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(PROJECT_NAME)
    parser.add_argument('-w', '--workspace', required=True, help='Workspace Path')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    gen_config_parser = subparsers.add_parser('gen-config', help='Generate Configuration')
    run_parser = subparsers.add_parser('run', help='run help')
    args = parser.parse_args()
    w = workspace.Workspace()
    w.initialize(args.workspace, PROJECT_NAME, args=args)
    logger = w.get_logger()
    if args.command == 'gen-config':
        logger.info("Generate Configuration")
        config = workspace.Config()
        w.set_config(config)
    elif args.command == 'run':
        logger.info("Start Running")
        main()
