from cleo.io.io import IO
from cleo.events.console_events import COMMAND
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event_dispatcher import EventDispatcher

from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand

from poetry.plugins.application_plugin import ApplicationPlugin
from pathlib import Path

import datetime

class VersionPlugin(ApplicationPlugin):
    def __init__(self):
        self.command = None
        self.io: IO = None

    @property
    def poetry(self):
        return self.command.poetry

    @property
    def config(self):
        return self.poetry.pyproject.data.get('tool', {}).get('version-plugin', None)

    @property
    def regex(self):
        if self.config:
            return self.config.get('regex', '__version__ = "{version}"\n')

    @property
    def out_file(self):
        destination = self.config.get('write_to', None)
        if destination:
            return Path(destination).absolute()

    def write_line(self, msg):
        if self.io and self.io.is_debug():
            self.io.write_line(f"<debug>{msg}</debug>")

    def write_file(self, version):
        if self.regex and self.out_file:
            if not self.out_file.exists():
                self.out_file.write_text(self.regex.format(version=version))
                return

            lines = self.out_file.read_text().splitlines()
            with open(self.out_file, 'w') as fp:
                for line in lines:
                    fp.write(line if not line.strip().startswith(self.regex.split('=')[0].strip()) else self.regex.format(version=version))


    def activate(self, application: Application):
        application.event_dispatcher.add_listener(COMMAND, self.set_custom_version)

    def set_custom_version(self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher) -> None:
        self.command = event.command
        if not isinstance(self.command, BuildCommand):
            return

        self.io = event.io

        version = self.get_custom_version()
        self.write_line(f"Setting package version to <b>{version}</b>")
        self.command.poetry.package.set_version(version)
        self.poetry.pyproject.poetry_config['version'] = version
        self.command.poetry.pyproject.save()

        self.write_file(version)

    def get_custom_version(self) -> str:
        project_version = self.poetry.pyproject.poetry_config['version']

        current_version, daily_patches = self.__parse_version(project_version)
        now = datetime.date.today()
        if now > current_version:
            return now.strftime('%Y.%-m.%-d')
        elif not daily_patches:
            return f"{current_version.strftime('%Y.%-m.%-d')}"
        else:
            return f"{current_version.strftime('%Y.%-m.%-d')}-{daily_patches + 1}"

    def __parse_version(self, version: str):
        if '-' in version:
            version, daily_patches = version.split('-', 1)
        else:
            daily_patches = 0

        try:
            return_version = datetime.datetime.strptime(version, '%Y.%m.%d').date()
        except ValueError:
            return_version = datetime.date.today()

        return return_version, int(daily_patches)