import argparse
import re
import sys
import yaml
import pathlib
import logging
import datetime
from src import constants
from yaml import CLoader
from src.singleton import SingletonMeta


class Config:
    version = 1
    config_template = {
        "config_version": version,
        "logger": {
            "file_logger_format": constants.FILE_LOGGER_FORMAT,
            "console_logger_format": constants.CONSOLE_LOGGER_FORMAT
        }
    }

    def __init__(self, ):
        w = Workspace()
        logger = w.get_logger()
        self._config_path = w.get_workspace_path() / 'config.yaml'
        logger.info(f"init config, config path={self._config_path}")
        if not self._config_path.exists():
            logger.info("config file doesn't exists, creating a new one")
            self.dump_config()
        logger.info("loading configuration file")
        self._config = self.load_config()

    def get_config_content(self):
        return self._config

    def load_config(self):
        with open(str(self._config_path), 'r') as f:
            config = yaml.load(f, Loader=CLoader)
            if config['config_version'] != Config.version:
                w = Workspace()
                template_file_path = w.get_workspace_path() / 'config-template.yaml'
                msg = f"configuration file version={config['config_version']} isn't the same as " \
                      f"latest version={Config.version}, use the latest version. A template file will be saved to " \
                      f"{str(template_file_path)}"
                w.get_logger().error(msg)
                self.dump_config(template_file_path)
                raise ValueError(msg)
        return config

    def dump_config(self, path: pathlib.Path = None):
        with open(str(path or self._config_path), 'w') as f:
            yaml.dump(Config.config_template, f)


class Workspace(metaclass=SingletonMeta):
    def __init__(self, workspace_path: str, project_name: str, config: Config = None, args: argparse.Namespace = None):
        self._project_name = re.sub('[\s,]', '', project_name)
        self._logger = logging.getLogger(project_name)
        self._config = config
        self._args = args
        self._workspace_path = pathlib.Path(workspace_path).absolute()
        self.setup_logger()
        self.setup_workspace()

    def set_config(self, config):
        self._config = config

    def get_config(self):
        return self._config

    def set_args(self, args):
        self._args = args

    def get_args(self):
        return self._args

    def get_logger(self):
        return self._logger

    def get_workspace_path(self):
        return self._workspace_path

    def create_workspace_dir(self):
        workspace_indicator = self._project_name + ".workspace.txt"
        self._workspace_path.mkdir(parents=True, exist_ok=True)
        with open(str(self._workspace_path / workspace_indicator), 'w') as f:
            f.write(f"created at {datetime.datetime.now()}")

    def setup_workspace(self):
        workspace_indicator = self._project_name + ".workspace.txt"
        if not self._workspace_path.exists():
            self._logger.info("workspace doesn't exist, creating the workspace directory")
            self.create_workspace_dir()
        else:
            if not self._workspace_path.is_dir():
                msg = "Workspace path exists and isn't a directory, double check your path"
                self._logger.error(msg)
                raise ValueError(msg)
            # check if the existing directory belongs to this project, if so, we can use it
            if (self._workspace_path / workspace_indicator).exists():
                self._logger.debug("workspace exists, continue")
            else:
                msg = "Workspace path exists but doesn't seem to belong to this project, please remove the directory"
                self._logger.error(msg)
                raise ValueError(msg)
        self._logger.info("setup_workspace finished")

    def setup_logger(self):
        self._logger.setLevel(logging.DEBUG)
        format_ = self._config.get_config_content()['logger'][
            'console_logger_format'] if self._config and 'console_logger_format' in self._config.get_config_content()[
            'logger'].keys() else constants.CONSOLE_LOGGER_FORMAT
        stdout_formatter = logging.Formatter(format_)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(stdout_formatter)
        format_ = self._config.get_config_content()['logger'][
            'file_logger_format'] if self._config and 'file_logger_format' in self._config.get_config_content()[
            'logger'].keys() else constants.FILE_LOGGER_FORMAT
        file_formatter = logging.Formatter(format_)
        if not self._workspace_path.exists():
            self.create_workspace_dir()
        file_handler = logging.FileHandler(str(self._workspace_path / (self._project_name + '.log')))
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        self._logger.addHandler(stdout_handler)
        self._logger.info("logger finished setup")
