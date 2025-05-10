"""
Module to handle the processing of configuration for the application.
"""

import argparse
import json
import logging
import os
from typing import Callable, Optional

import tomli
import yaml
from application_properties import (
    ApplicationProperties,
    ApplicationPropertiesJsonLoader,
    ApplicationPropertiesTomlLoader,
    ApplicationPropertiesYamlLoader,
)

from pyshell.file_path_helpers import FilePathHelpers

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class ApplicationConfigurationHelper:
    """
    Class to handle the processing of configuration for the application.
    """

    DEFAULT_CONFIGURATION_PATH = os.path.join("~", ".pyshell.cfg")

    @staticmethod
    def apply_configuration_layers(
        args: argparse.Namespace,
        properties: ApplicationProperties,
        handle_error: Callable[[str, Optional[Exception]], None],
    ) -> None:
        """
        Apply any general python configuration files followed by any configuration
        files specific to this project.
        """

        LOGGER.debug("Looking for application specific configuration files.")
        ApplicationConfigurationHelper.__process_project_specific_json_configuration(
            args,
            properties,
            handle_error,
        )

        try:
            if args.strict_configuration or properties.get_boolean_property(
                "mode.strict-config", strict_mode=True
            ):
                properties.enable_strict_mode()
        except ValueError as this_exception:
            handle_error(
                "The value for property 'mode.strict-config' must be of type 'bool'.",
                this_exception,
            )

    @staticmethod
    def __apply_default_configuration(
        application_properties: ApplicationProperties,
    ) -> None:
        application_properties.clear()
        application_properties.load_from_dict(
            {
                "items": {
                    "user-name": {
                        "type": "property",
                        "data_source": "system",
                        "data_item": "user_name",
                        "prefix": "[",
                        "suffix": "@",
                    },
                    "host-name": {
                        "type": "property",
                        "data_source": "system",
                        "data_item": "host_name",
                        "prefix": "",
                        "suffix": "]",
                    },
                    "directory": {
                        "type": "property",
                        "data_source": "system",
                        "data_item": "full_cwd",
                        "prefix": " [",
                        "suffix": "]",
                    },
                    "git-branch": {
                        "type": "property",
                        "data_source": "git",
                        "data_item": "branch",
                        "prefix": " br[",
                        "suffix": "]",
                    },
                    "project-root-directory": {
                        "type": "property",
                        "data_source": "project",
                        "data_item": "root_directory",
                        "prefix": " prd[",
                        "suffix": "]",
                    },
                    "prompt": {"type": "text", "text": "\n$ "},
                }
            }
        )

    @staticmethod
    def __process_project_specific_json_configuration(
        args: argparse.Namespace,
        application_properties: ApplicationProperties,
        handle_error_fn: Callable[[str, Optional[Exception]], None],
    ) -> None:
        """
        Load configuration information from the different types of configuration files.
        """
        configuration_file = (
            args.configuration_file
            or ApplicationConfigurationHelper.DEFAULT_CONFIGURATION_PATH
        )
        LOGGER.info("Looking for configuration file: %s", configuration_file)
        configuration_file = FilePathHelpers.normalize_path(configuration_file)
        if not os.path.isfile(configuration_file):
            if not args.configuration_file:
                ApplicationConfigurationHelper.__apply_default_configuration(
                    application_properties
                )
                return
            handle_error_fn(
                f"Specified configuration file `{configuration_file}` does not exist.",
                None,
            )

        LOGGER.debug(
            "Determining file type for specified configuration file '%s'.",
            configuration_file,
        )
        try:
            with open(configuration_file, encoding="utf-8") as infile:
                json.load(infile)
            did_load_as_json = True
        except json.decoder.JSONDecodeError:
            did_load_as_json = False

        try:
            with open(configuration_file, "rb") as infile:
                loaded_document = yaml.safe_load(infile)
            did_load_as_yaml = not isinstance(loaded_document, str)
        except yaml.MarkedYAMLError:
            did_load_as_yaml = False

        try:
            with open(configuration_file, "rb") as infile:
                tomli.load(infile)
            did_load_as_toml = True
        except tomli.TOMLDecodeError:
            did_load_as_toml = False

        if did_load_as_json:
            LOGGER.debug(
                "Attempting to load configuration file '%s' as a JSON file.",
                configuration_file,
            )
            ApplicationPropertiesJsonLoader.load_and_set(
                application_properties,
                configuration_file,
                handle_error_fn=handle_error_fn,
                clear_property_map=False,
                check_for_file_presence=False,
            )
        elif did_load_as_yaml:
            LOGGER.debug(
                "Attempting to load configuration file '%s' as a YAML file.",
                configuration_file,
            )
            ApplicationPropertiesYamlLoader.load_and_set(
                application_properties,
                configuration_file,
                handle_error_fn=handle_error_fn,
                clear_property_map=False,
                check_for_file_presence=False,
            )
        elif did_load_as_toml:
            LOGGER.debug(
                "Attempting to load configuration file '%s' as a TOML file.",
                configuration_file,
            )
            ApplicationPropertiesTomlLoader.load_and_set(
                application_properties,
                configuration_file,
                handle_error_fn=handle_error_fn,
                clear_property_map=False,
                check_for_file_presence=False,
            )
        else:
            formatted_error = f"Specified configuration file '{configuration_file}' was not parseable as a JSON, YAML, or TOML file."
            LOGGER.warning(formatted_error)
            handle_error_fn(formatted_error, None)

        # A specific setting applied on the command line has the highest precedence.
        if args.set_configuration:
            LOGGER.debug(
                "Attempting to set one or more provided manual properties '%s'.",
                args.set_configuration,
            )
            application_properties.set_manual_property(args.set_configuration)


# pylint: enable=too-few-public-methods
