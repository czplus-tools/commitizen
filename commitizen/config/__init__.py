from __future__ import annotations

from pathlib import Path

from commitizen import defaults, git
from commitizen.exceptions import InvalidConfigurationError

from .base_config import BaseConfig
from .json_config import JsonConfig
from .toml_config import TomlConfig
from .yaml_config import YAMLConfig


def read_cfg(
    cfg_path: Path | None = None,
) -> BaseConfig | TomlConfig | JsonConfig | YAMLConfig:
    """
    Read and load a configuration based on the provided path or defaults.

    Args:
        cfg_path (Path | None): The path to the configuration file passed from CLI args,
            or None if no specific path is provided. Defaults to None.

    Returns:
        BaseConfig: An instance of `BaseConfig` (included TomlConfig | JsonConfig | YAMLConfig)
            containing the loaded configuration.

    Raises:
        InvalidConfigurationError: If the specified configuration file path does not exist.
        InvalidConfigurationError: If the loaded configuration is empty, indicating that
            the file does not contain any valid configuration data.

    Note:
        If `cfg_path` is provided, the function attempts to load the configuration from
        that path. If the path does not exist or the configuration is empty, an exception
        is raised. If `cfg_path` is not provided, the function searches for a configuration
        in default locations using `_find_config_from_defaults()`.
    """
    conf = BaseConfig()

    if cfg_path:
        if not cfg_path.exists():
            raise InvalidConfigurationError(f"File {cfg_path} not exists.")
        _conf = _load_config_from_file(cfg_path)
        if _conf.is_empty_config:
            raise InvalidConfigurationError(
                f"File {cfg_path} doesn't contain any configuration. "
                f"Fill it or don't use --config-file option."
            )
    else:
        _conf = _find_config_from_defaults()

    if _conf:
        conf = _conf

    return conf


def _find_config_from_defaults():
    """
    Find and load a configuration from default search paths.

    This function looks for configuration files in default locations and loads the first
    non-empty configuration it encounters. If no suitable configuration is found, it returns None.

    Returns:
        TomlConfig | JsonConfig | YAMLConfig | None
    """
    git_project_root = git.find_git_project_root()
    cfg_search_paths = [Path(".")]
    if git_project_root:
        cfg_search_paths.append(git_project_root)
    cfg_paths = (
        path / Path(filename)
        for path in cfg_search_paths
        for filename in defaults.config_files
    )
    for filename in cfg_paths:
        if not filename.exists():
            continue
        _conf = _load_config_from_file(path=filename)
        if not _conf.is_empty_config:
            return _conf
    return None


def _load_config_from_file(path: Path) -> TomlConfig | JsonConfig | YAMLConfig:
    """
    Load configuration data from a file based on its extension.

    Args:
        path (Path): The path to the configuration file.

    Returns:
        TomlConfig | JsonConfig | YAMLConfig: An instance of a configuration class
        corresponding to the file's extension (TomlConfig for .toml, JsonConfig for .json,
        or YAMLConfig for .yaml).

    Raises:
        ValueError: If the file extension is not one of the expected formats (toml, json, yaml).

    Note:
        We expect that any object in defaults.py -> config_files
        definitely falls under the conditions above. Therefore,
        this error may occur when using an arbitrary configuration file path.
    """
    _conf: TomlConfig | JsonConfig | YAMLConfig

    with open(path, "rb") as f:
        data: bytes = f.read()

    if "toml" in path.suffix:
        _conf = TomlConfig(data=data, path=path)
    elif "json" in path.suffix:
        _conf = JsonConfig(data=data, path=path)
    elif "yaml" in path.suffix:
        _conf = YAMLConfig(data=data, path=path)
    else:
        # We expect that any object in defaults.py -> config_files
        # definitely falls under the conditions above. Therefore,
        # this error may occur when using an arbitrary configuration file path.
        raise InvalidConfigurationError(
            "Config file should have a valid extension: toml, yaml or json"
        )
    return _conf
