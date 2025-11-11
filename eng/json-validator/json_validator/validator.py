"""
Ed-Fi JSON Data Lake Validator.

This module provides functionality to validate JSON files in a data lake
structure against Ed-Fi OpenAPI schema definitions.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import jsonschema
import requests
import yaml


logger = logging.getLogger(__name__)


class ValidationResult:
    """Represents the result of validating a single JSON file."""

    def __init__(
        self,
        file_path: str,
        schema_name: str,
        is_valid: bool,
        errors: Optional[List[str]] = None
    ) -> None:
        """Initialize validation result.

        Args:
            file_path: Path to the validated file
            schema_name: Name of the schema used for validation
            is_valid: Whether validation passed
            errors: List of validation error messages
        """
        self.file_path = file_path
        self.schema_name = schema_name
        self.is_valid = is_valid
        self.errors = errors or []


class DataLakeValidator:
    """Validates JSON files in a data lake against Ed-Fi OpenAPI schemas."""

    def __init__(self, data_lake_root: str, openapi_spec_path: str) -> None:
        """Initialize the validator.

        Args:
            data_lake_root: Root directory of the data lake
            openapi_spec_path: Path or URL to the OpenAPI specification
        """
        self.data_lake_root = Path(data_lake_root)
        self.openapi_spec_path = openapi_spec_path
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self._load_openapi_spec()

    def _load_openapi_spec(self) -> None:
        """Load and parse the OpenAPI specification."""
        try:
            if self._is_url(self.openapi_spec_path):
                logger.info(
                    f"Loading OpenAPI spec from URL: {self.openapi_spec_path}"
                )
                response = requests.get(self.openapi_spec_path, timeout=30)
                response.raise_for_status()
                spec_content = response.text
            else:
                logger.info(
                    f"Loading OpenAPI spec from file: {self.openapi_spec_path}"
                )
                with open(self.openapi_spec_path, "r", encoding="utf-8") as f:
                    spec_content = f.read()

            # Try JSON first, then YAML
            try:
                openapi_spec = json.loads(spec_content)
                logger.debug("Successfully parsed OpenAPI spec as JSON")
            except json.JSONDecodeError:
                try:
                    openapi_spec = yaml.safe_load(spec_content)
                    logger.debug("Successfully parsed OpenAPI spec as YAML")
                except yaml.YAMLError as yaml_err:
                    raise ValueError(
                        f"Failed to parse OpenAPI spec as either JSON or YAML. "
                        f"YAML error: {yaml_err}"
                    )

            # Extract schemas from components section
            components = openapi_spec.get("components", {})
            self.schemas = components.get("schemas", {})

            logger.info(
                f"Loaded {len(self.schemas)} schemas from OpenAPI specification"
            )

        except Exception as e:
            logger.error(f"Failed to load OpenAPI specification: {e}")
            raise

    def _is_url(self, path: str) -> bool:
        """Check if the given path is a URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _get_schema_name_from_path(self, file_path: Path) -> Optional[str]:
        """Determine the schema name from the file path.

        Args:
            file_path: Path to the JSON file

        Returns:
            Schema name or None if no mapping found
        """
        relative_path = file_path.relative_to(self.data_lake_root)
        path_parts = relative_path.parts

        if len(path_parts) < 2:
            return None

        namespace = path_parts[0]  # e.g., "ed-fi", "tpdm"
        entity_type = path_parts[1]  # e.g., "academicWeeks", "students"

        # Convert entity type to singular and apply naming convention
        singular_entity = self._pluralize_to_singular(entity_type)

        # Map to schema naming convention
        if namespace == "ed-fi":
            schema_name = f"edFi_{singular_entity}"
        else:
            schema_name = f"{namespace}_{singular_entity}"

        return schema_name

    def _pluralize_to_singular(self, plural_word: str) -> str:
        """Convert plural entity names to singular form.

        Args:
            plural_word: Plural form of the entity name

        Returns:
            Singular form using camelCase
        """
        # Handle specific Ed-Fi entity names
        if plural_word == "candidates":
            return "candidate"
        elif plural_word == "courses":
            return "course"
        elif plural_word == "academicWeeks":
            return "academicWeek"
        elif plural_word == "students":
            return "student"

        # General pluralization rules
        if plural_word.endswith("ies"):
            singular = plural_word[:-3] + "y"
        elif (plural_word.endswith("ches") or
              plural_word.endswith("shes") or
              plural_word.endswith("xes")):
            singular = plural_word[:-2]
        elif plural_word.endswith("ses"):
            # Handle cases like "courses" and "addresses"
            if plural_word.endswith("eses"):
                singular = plural_word[:-2]
            else:
                singular = plural_word[:-1]
        elif plural_word.endswith("s") and not plural_word.endswith("ss"):
            singular = plural_word[:-1]
        else:
            singular = plural_word

        return singular

    def _validate_json_file(self, file_path: Path) -> ValidationResult:
        """Validate a single JSON file against its schema.

        Args:
            file_path: Path to the JSON file to validate

        Returns:
            ValidationResult object
        """
        schema_name = self._get_schema_name_from_path(file_path)

        if not schema_name:
            return ValidationResult(
                str(file_path),
                "unknown",
                False,
                ["Cannot determine schema from file path"]
            )

        if schema_name not in self.schemas:
            return ValidationResult(
                str(file_path),
                schema_name,
                False,
                [f"Schema '{schema_name}' not found in OpenAPI specification"]
            )

        try:
            # Load JSON file
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # Get schema definition
            schema = self.schemas[schema_name]

            # Create a resolver for handling $ref in schemas
            resolver = jsonschema.RefResolver(
                base_uri="",
                referrer={"components": {"schemas": self.schemas}}
            )

            # Validate against schema
            jsonschema.validate(
                instance=json_data,
                schema=schema,
                resolver=resolver
            )

            logger.debug(f"✓ {file_path} validated successfully against {schema_name}")
            return ValidationResult(str(file_path), schema_name, True)

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {e}"
            logger.error(f"✗ {file_path}: {error_msg}")
            return ValidationResult(str(file_path), schema_name, False, [error_msg])

        except jsonschema.ValidationError as e:
            error_msg = f"Schema validation failed: {e.message}"
            logger.error(f"✗ {file_path}: {error_msg}")
            return ValidationResult(str(file_path), schema_name, False, [error_msg])

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(f"✗ {file_path}: {error_msg}")
            return ValidationResult(str(file_path), schema_name, False, [error_msg])

    def _find_json_files(self) -> List[Path]:
        """Find all JSON files in the data lake.

        Returns:
            List of Path objects for JSON files
        """
        json_files = []

        for root, dirs, files in os.walk(self.data_lake_root):
            for file in files:
                if file.lower().endswith(".json"):
                    json_files.append(Path(root) / file)

        logger.info(f"Found {len(json_files)} JSON files to validate")
        return json_files

    def validate_all(self) -> Tuple[List[ValidationResult], Dict[str, int]]:
        """Validate all JSON files in the data lake.

        Returns:
            Tuple of (validation results, summary statistics)
        """
        json_files = self._find_json_files()
        results = []

        logger.info("Starting validation of all JSON files...")

        for file_path in json_files:
            result = self._validate_json_file(file_path)
            results.append(result)

        # Generate summary statistics
        total_files = len(results)
        valid_files = sum(1 for r in results if r.is_valid)
        invalid_files = total_files - valid_files

        summary = {
            "total_files": total_files,
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "success_rate": (valid_files / total_files * 100) if total_files > 0 else 0
        }

        logger.info(
            f"Validation complete: {valid_files}/{total_files} files valid "
            f"({summary['success_rate']:.1f}%)"
        )

        return results, summary

    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a single JSON file.

        Args:
            file_path: Path to the JSON file to validate

        Returns:
            ValidationResult object
        """
        return self._validate_json_file(Path(file_path))

    def get_available_schemas(self) -> List[str]:
        """Get list of available schema names.

        Returns:
            List of schema names from the OpenAPI specification
        """
        return list(self.schemas.keys())
