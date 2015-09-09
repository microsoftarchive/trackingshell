import argparse
import sys
import os
import subprocess
import logging
from .decorators import *

logger = logging.getLogger('trackingshell')
logger.addHandler(logging.NullHandler())

class MakeTarget(object):
    WITHOUT_TARGET = 'no-target'

    # MakeTarget
    def __init__(self, target, command, **kwargs):
        self.target = target or self.WITHOUT_TARGET
        self.command = command
        self.__dict__.update(kwargs)
        self.logger = logger
        self.set_logger()

    # void
    def set_logger(self):
        pass

    # bool
    def has_target(self):
        return self.target != self.WITHOUT_TARGET

    # bool
    def has_makelevel(self):
        return "MAKELEVEL" in os.environ

    # int
    def execute_command(self):
        return subprocess.call(["/bin/bash", "-e", "-o", "pipefail", "-c",
            self.command])

    # void
    def logger_fn_for_exit_code(self, exit_code, success = None, failure = None):
        return getattr(self.logger, (success or 'info') \
            if exit_code == 0 \
            else (failure or 'error'))

    # dict
    def as_dict(self):
        return dict(self.__dict__)

    # str
    def __repr__(self):
        if not self.has_makelevel():
            return '<{module}.{cls} with command `{command}` and without target>'.format(
                module=self.__module__, cls=self.__class__.__name__,
                command=self.command)

        return '<{module}.{cls} with command `{command}` and `{target}` target>'.format(
            module=self.__module__, cls=self.__class__.__name__,
            target=self.target, command=self.command)

# int
@plugin
def execute_command(mt, next_plugin_fn):
    assert next_plugin_fn is None
    return mt.execute_command()

class PluginRegistry(object):
    # PluginRegistry
    def __init__(self, plugins = None):
        self.plugins = plugins or []

    # function
    def _wraps(self, plugins):
        next_plugin_fn, rest = plugins[0], plugins[1:]
        return lambda mt: next_plugin_fn(mt, self._wraps(rest) if rest else None)

    # void
    def register(self, plugin_fn):
        self.plugins.insert(len(self.plugins)-1, plugin_fn)

    # void
    def unregister(self, plugin_fn):
        self.plugins.remove(plugin_fn)

    # function
    def wraps(self):
        return self._wraps(self.plugins)

class Shell(object):
    # Shell
    def __init__(self, argv = None):
        self._set_parser()
        self._set_plugins()
        self.argv = argv
        self.cls = MakeTarget

    # void
    def _set_parser(self):
        self.parser = argparse.ArgumentParser(
            prog='%(prog)s',
            description="Tracks makefiles targets"
        )
        self.parser.add_argument('-t', '--target', help="name of the make target", nargs="?")
        self.parser.add_argument('-c', '--command', help="command to execute", required=True)

    # void
    def _set_plugins(self):
        self.plugins = PluginRegistry([execute_command])

    # void
    def delegate(self, return_exit_code = False):
        # Construct a MakeTarget object
        mt = self.cls(**vars(self.parser.parse_args(self.argv)))

        # Execute the command
        exit_code = self.plugins.wraps()(mt)

        # Set a message.
        exit_message = 'Command execution is finished with exit code {}'.format(exit_code)
        logger_fn = mt.logger_fn_for_exit_code(exit_code, success='info')
        logger_fn(exit_message, extra = mt.as_dict())

        # Quit
        if return_exit_code:
            self.mt = mt
            return exit_code

        sys.exit(exit_code)

# void
def main(argv=sys.argv[1:]):
    Shell(argv).delegate()