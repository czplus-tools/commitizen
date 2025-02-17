from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from commitizen import config, defaults, git
from commitizen.exceptions import InvalidConfigurationError

PYPROJECT = """
[tool.commitizen]
name = "cz_jira"
version = "1.0.0"
version_files = [
    "commitizen/__version__.py",
    "pyproject.toml"
]
style = [
    ["pointer", "reverse"],
    ["question", "underline"]
]
pre_bump_hooks = [
    "scripts/generate_documentation.sh"
]
post_bump_hooks = ["scripts/slack_notification.sh"]

[tool.black]
line-length = 88
target-version = ['py36', 'py37', 'py38']
"""

DICT_CONFIG = {
    "commitizen": {
        "name": "cz_jira",
        "version": "1.0.0",
        "version_files": ["commitizen/__version__.py", "pyproject.toml"],
        "style": [["pointer", "reverse"], ["question", "underline"]],
        "pre_bump_hooks": ["scripts/generate_documentation.sh"],
        "post_bump_hooks": ["scripts/slack_notification.sh"],
    }
}


_settings: dict[str, Any] = {
    "name": "cz_jira",
    "version": "1.0.0",
    "version_provider": "commitizen",
    "version_scheme": None,
    "tag_format": "$version",
    "bump_message": None,
    "allow_abort": False,
    "allowed_prefixes": ["Merge", "Revert", "Pull request", "fixup!", "squash!"],
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
    "changelog_format": None,
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "changelog_merge_prerelease": False,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
    "major_version_zero": False,
    "pre_bump_hooks": ["scripts/generate_documentation.sh"],
    "post_bump_hooks": ["scripts/slack_notification.sh"],
    "prerelease_offset": 0,
    "encoding": "utf-8",
    "always_signoff": False,
    "template": None,
    "extras": {},
}

_new_settings: dict[str, Any] = {
    "name": "cz_jira",
    "version": "2.0.0",
    "version_provider": "commitizen",
    "version_scheme": None,
    "tag_format": "$version",
    "bump_message": None,
    "allow_abort": False,
    "allowed_prefixes": ["Merge", "Revert", "Pull request", "fixup!", "squash!"],
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
    "changelog_format": None,
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "changelog_merge_prerelease": False,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
    "major_version_zero": False,
    "pre_bump_hooks": ["scripts/generate_documentation.sh"],
    "post_bump_hooks": ["scripts/slack_notification.sh"],
    "prerelease_offset": 0,
    "encoding": "utf-8",
    "always_signoff": False,
    "template": None,
    "extras": {},
}


@pytest.fixture
def config_files_manager(request, tmpdir):
    with tmpdir.as_cwd():
        filename = request.param
        with open(filename, "w", encoding="utf-8") as f:
            if "toml" in filename:
                f.write(PYPROJECT)
            elif "json" in filename:
                json.dump(DICT_CONFIG, f)
            elif "yaml" in filename:
                yaml.dump(DICT_CONFIG, f)
        yield


def test_find_git_project_root(tmpdir):
    assert git.find_git_project_root() == Path(os.getcwd())

    with tmpdir.as_cwd() as _:
        assert git.find_git_project_root() is None


@pytest.mark.parametrize(
    "config_files_manager", defaults.config_files.copy(), indirect=True
)
def test_set_key(config_files_manager):
    _conf = config.read_cfg()
    _conf.set_key("version", "2.0.0")
    cfg = config.read_cfg()
    assert cfg.settings == _new_settings


class TestReadCfg:
    @pytest.mark.parametrize(
        "config_files_manager", defaults.config_files.copy(), indirect=True
    )
    def test_load_conf(_, config_files_manager):
        cfg = config.read_cfg()
        assert cfg.settings == _settings

    def test_conf_returns_default_when_no_files(_, tmpdir):
        with tmpdir.as_cwd():
            cfg = config.read_cfg()
            assert cfg.settings == defaults.DEFAULT_SETTINGS

    def test_load_empty_pyproject_toml_and_cz_toml_with_config(_, tmpdir):
        with tmpdir.as_cwd():
            p = tmpdir.join("pyproject.toml")
            p.write("")
            p = tmpdir.join(".cz.toml")
            p.write(PYPROJECT)

            cfg = config.read_cfg()
            assert cfg.settings == _settings


class TestTomlConfig:
    def test_init_empty_config_content(self, tmpdir):
        path = tmpdir.mkdir("commitizen").join(".cz.toml")
        toml_config = config.TomlConfig(data="", path=path)
        toml_config.init_empty_config_content()

        with open(path, encoding="utf-8") as toml_file:
            assert toml_file.read() == "[tool.commitizen]\n"

    def test_init_empty_config_content_with_existing_content(self, tmpdir):
        existing_content = "[tool.black]\n" "line-length = 88\n"

        path = tmpdir.mkdir("commitizen").join(".cz.toml")
        path.write(existing_content)
        toml_config = config.TomlConfig(data="", path=path)
        toml_config.init_empty_config_content()

        with open(path, encoding="utf-8") as toml_file:
            assert toml_file.read() == existing_content + "\n[tool.commitizen]\n"

    def test_init_with_invalid_config_content(self, tmpdir):
        existing_content = "invalid toml content"
        path = tmpdir.mkdir("commitizen").join(".cz.toml")

        with pytest.raises(InvalidConfigurationError, match=r"\.cz\.toml"):
            config.TomlConfig(data=existing_content, path=path)


class TestJsonConfig:
    def test_init_empty_config_content(self, tmpdir):
        path = tmpdir.mkdir("commitizen").join(".cz.json")
        json_config = config.JsonConfig(data="{}", path=path)
        json_config.init_empty_config_content()

        with open(path, encoding="utf-8") as json_file:
            assert json.load(json_file) == {"commitizen": {}}

    def test_init_with_invalid_config_content(self, tmpdir):
        existing_content = "invalid json content"
        path = tmpdir.mkdir("commitizen").join(".cz.json")

        with pytest.raises(InvalidConfigurationError, match=r"\.cz\.json"):
            config.JsonConfig(data=existing_content, path=path)


class TestYamlConfig:
    def test_init_empty_config_content(self, tmpdir):
        path = tmpdir.mkdir("commitizen").join(".cz.yaml")
        yaml_config = config.YAMLConfig(data="{}", path=path)
        yaml_config.init_empty_config_content()

        with open(path) as yaml_file:
            assert yaml.safe_load(yaml_file) == {"commitizen": {}}

    def test_init_with_invalid_content(self, tmpdir):
        existing_content = "invalid: .cz.yaml: content: maybe?"
        path = tmpdir.mkdir("commitizen").join(".cz.yaml")

        with pytest.raises(InvalidConfigurationError, match=r"\.cz\.yaml"):
            config.YAMLConfig(data=existing_content, path=path)


@pytest.mark.czplus
class TestCustomFileConfig:
    @pytest.fixture
    def empty_files_manager(self, request, tmpdir):
        with tmpdir.as_cwd():
            with open(request.param, "w", encoding="utf-8") as f:
                f.write("")
            yield

    def test_custom_file_not_exist(self):
        with pytest.raises(InvalidConfigurationError, match=".*not exists.*"):
            config.read_cfg(cfg_path=Path("file.yaml"))

    @pytest.mark.parametrize("empty_files_manager", ["file.toml"], indirect=True)
    def test_custom_file_is_empty_config(self, empty_files_manager):
        with pytest.raises(InvalidConfigurationError, match=".*Fill it.*"):
            config.read_cfg(cfg_path=Path("file.toml"))

    @pytest.mark.parametrize("empty_files_manager", ["file.txt"], indirect=True)
    def test_load_config_from_file_incorrect_extension(self, empty_files_manager):
        assert Path("file.txt").exists()
        with pytest.raises(
            InvalidConfigurationError, match=".*should have a valid extension.*"
        ):
            config._load_config_from_file(path=Path("file.txt"))

    @pytest.mark.parametrize("config_files_manager", ["file.toml"], indirect=True)
    def test_load_config_from_custom_file(self, config_files_manager):
        cfg = config.read_cfg(cfg_path=Path("file.toml"))
        assert cfg.settings == _settings
