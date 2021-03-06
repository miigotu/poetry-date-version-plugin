This plugin is intended to allow you to use the day you commit as the release version, with the number of individual pushes being the patch level.
This matches well with semver, and allows you and users to see very easily when the last update was and if they are out of date.
The version in pyproject.toml is updated automatically when you run `poetry build`

This currently requires an alpha version of poetry, and likely is not easy to implement for most users out of the box just yet.
You can solve installation by first calling `pip install git+https://github.com/python-poetry/poetry@master` to test and hack on it.

__TODO:__ 

Make sure subsequent builds in between commits and pushes do not increment the patch level.
Add tests and make error handling more robust.
Add support for development patch levels such as `.dev\d*` or a short hash.
Further implement the `poetry version` command.
___

All contribution is welcome, and if you use my code or idea elsewhere please give credits. I hope for this project to be precise and uncomplicated, so the feature set should be fairly targeted (I even debated not allowing an external write_to version file and only supporting toml.)

```bash
pip install cleo==1.0.0a1
pip install git+https://github.com/python-poetry/poetry
pip install git+https://github.com/miigotu/poetry-date-version-plugin

```
```toml
[tool.poetry.plugins."poetry.application.plugin"]
plugin = "poetry_date_version_plugin.plugin:VersionPlugin"

[tool.version-plugin]
write_to = 'yourproject/version.py'
regex = '__version__ = "{version}"'
```