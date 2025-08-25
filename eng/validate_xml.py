#!/usr/bin/env python3

# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""
XML Validation Script for Ed-Fi Data Standard

This script performs two types of validation:
1. Schema validation: Validates Sample XML files against XSD schema definitions
2. Descriptor validation: Validates descriptor URIs in sample data against descriptor XML files

Usage:
    python validate_xml.py [--samples-dir SAMPLES_DIR] [--schemas-dir SCHEMAS_DIR] [--descriptors-dir DESCRIPTORS_DIR]

Exit codes:
    0: No validation errors found
    1: Validation errors found
    2: Script execution error
"""

import argparse
import os
import re
from lxml import etree
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import xml.etree.ElementTree as ET


class ValidationError:
    """Represents a validation error with file, line number, and message."""

    def __init__(self, file_path: str, line_number: int, message: str):
        self.file_path = file_path
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return f"{os.path.basename(self.file_path)}\t{self.line_number}\t{self.message}"


class XMLValidator:
    """Main validation class for XML files."""

    # Regex pattern to match descriptor URIs - captures everything until XML closing tag
    DESCRIPTOR_PATTERN = re.compile(
        r"uri://(?P<namespace>[^/]+)/(?P<descriptor>[^#]+)#(?P<codeValue>[^<]+)"
    )

    def __init__(self, samples_dir: str, schemas_dir: str, descriptors_dir: str):
        self.samples_dir = Path(samples_dir)
        self.schemas_dir = Path(schemas_dir)
        self.descriptors_dir = Path(descriptors_dir)
        self.errors: Dict[str, List[ValidationError]] = {}

        # Cache for loaded descriptor data
        self._descriptor_cache: Dict[str, Set[Tuple[str, str]]] = {}
        # Cache for loaded schema objects to avoid reloading
        self._schema_cache: Dict[str, etree.XMLSchema] = {}
        # Precompiled regex for line number extraction
        self._line_pattern = re.compile(r", line (\d+)")

    def clear_caches(self):
        """Clear all caches to free memory."""
        self._descriptor_cache.clear()
        self._schema_cache.clear()
        self.errors.clear()

    def add_error(self, error: ValidationError):
        """Add a validation error to the error collection."""
        file_key = os.path.basename(error.file_path)
        if file_key not in self.errors:
            self.errors[file_key] = []
        self.errors[file_key].append(error)

    def validate_schema(self, xml_file: Path, xml_doc: etree._ElementTree) -> None:
        """Validate an XML file against its corresponding XSD schema."""
        try:
            # Find corresponding schema file
            schema_file = self._find_schema_file(xml_file, xml_doc)
            if not schema_file:
                self.add_error(
                    ValidationError(
                        str(xml_file), 1, f"No corresponding schema file found"
                    )
                )
                return

            schema_path_str = str(schema_file)

            # Use cached schema if available
            if schema_path_str in self._schema_cache:
                schema = self._schema_cache[schema_path_str]
            else:
                # Change to schemas directory to resolve includes
                cwd = os.getcwd()
                try:
                    os.chdir(self.schemas_dir)
                    with open(schema_file, "rb") as xsd_f:
                        schema_root = etree.XML(xsd_f.read())
                        schema = etree.XMLSchema(schema_root)
                    self._schema_cache[schema_path_str] = schema
                finally:
                    os.chdir(cwd)

            # Parse and validate XML - use context manager to ensure cleanup

            if not schema.validate(xml_doc):
                for error in schema.error_log:
                    self.add_error(
                        ValidationError(
                            str(xml_file),
                            error.line,
                            error.message,
                        )
                    )

        except (etree.XMLSchemaError, etree.DocumentInvalid) as e:
            # Extract line number from error string if available
            error_str = str(e)
            match = self._line_pattern.search(error_str)
            if match:
                line_number = int(match.group(1))
            else:
                line_number = 0
            self.add_error(
                ValidationError(
                    str(xml_file),
                    line_number,
                    str(e),
                )
            )
        except Exception as e:
            self.add_error(ValidationError(str(xml_file), 1, str(e)))

    def _find_schema_file(self, xml_file: Path, xml_doc: etree._ElementTree) -> Path:
        """Find the corresponding XSD schema file by extracting the path from xsi:schemaLocation attribute."""
        try:
            root = xml_doc.getroot()

            # Get the xsi:schemaLocation attribute
            schema_location = root.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation')

            if schema_location:
                # The schemaLocation attribute contains pairs of namespace URI and schema location
                # Split by whitespace and get the schema location (second part)
                parts = schema_location.split()
                if len(parts) >= 2:
                    schema_path = parts[1]  # The schema file path

                    # Resolve relative path from the XML file's directory
                    xml_dir = xml_file.parent
                    absolute_schema_path = (xml_dir / schema_path).resolve()

                    if absolute_schema_path.exists():
                        return absolute_schema_path

            return None

        except Exception:
            return None

    def validate_descriptors(self, xml_file: Path, xml_doc: etree._ElementTree) -> None:
        """Validate descriptor URIs in an XML file against descriptor definitions."""
        try:
            # Recursively iterate through all elements in the XML
            self._validate_element_descriptors(xml_doc.getroot(), xml_file, 1)

        except Exception as e:
            self.add_error(
                ValidationError(
                    str(xml_file),
                    1,
                    f"Error parsing XML file for descriptor validation: {str(e)}",
                )
            )

    def _validate_element_descriptors(self, element, xml_file: Path, line_number: int) -> None:
        """Recursively validate descriptor URIs in XML elements."""
        # Check element text for descriptor URIs
        if element.text:
            self._validate_text_for_descriptors(element.text, xml_file, line_number)

        # Check element tail text for descriptor URIs
        if element.tail:
            self._validate_text_for_descriptors(element.tail, xml_file, line_number)

        # Check attribute values for descriptor URIs
        for attr_name, attr_value in element.attrib.items():
            if attr_value:
                self._validate_text_for_descriptors(attr_value, xml_file, line_number)

        # Recursively process child elements
        for child in element:
            # Get approximate line number (lxml provides this)
            child_line = getattr(child, 'sourceline', line_number)
            self._validate_element_descriptors(child, xml_file, child_line)

    def _validate_text_for_descriptors(self, text: str, xml_file: Path, line_number: int) -> None:
        """Validate descriptor URIs found in text content."""
        for match in self.DESCRIPTOR_PATTERN.finditer(text):
            namespace = match.group("namespace")
            descriptor = match.group("descriptor")
            code_value = match.group("codeValue").strip()

            # Validate the descriptor
            self._validate_descriptor_reference(
                xml_file, line_number, namespace, descriptor, code_value
            )

    def _validate_descriptor_reference(
        self,
        xml_file: Path,
        line_number: int,
        namespace: str,
        descriptor: str,
        code_value: str,
    ) -> None:
        """Validate a single descriptor reference."""
        # Check if descriptor file exists
        descriptor_file = self.descriptors_dir / f"{descriptor}.xml"
        if not descriptor_file.exists():
            # Also check in the sample XML files
            sample_descriptor_file = self.samples_dir / f"{descriptor}.xml"
            if sample_descriptor_file.exists():
                descriptor_file = sample_descriptor_file
            else:
                self.add_error(
                    ValidationError(
                        str(xml_file),
                        line_number,
                        f"No matching descriptor file for {descriptor}",
                    )
                )
                return

        # Load descriptor data if not cached
        if descriptor not in self._descriptor_cache:
            self._load_descriptor_data(descriptor_file, descriptor)

        # Check if the specific code value and namespace combination exists
        expected_namespace = f"uri://{namespace}/{descriptor}"
        descriptor_key = (code_value, expected_namespace)

        if descriptor_key not in self._descriptor_cache[descriptor]:
            self.add_error(
                ValidationError(
                    str(xml_file),
                    line_number,
                    f"No matching code value {code_value} for {descriptor}",
                )
            )

    def _load_descriptor_data(self, descriptor_file: Path, descriptor: str) -> None:
        """Load descriptor data from XML file into cache."""
        tree = None
        try:
            tree = ET.parse(str(descriptor_file))
            root = tree.getroot()

            # Remove namespace prefix for easier searching
            # Handle namespace-aware parsing
            descriptor_data = set()

            # Find all descriptor elements (handle namespace)
            for elem in root.iter():
                # Get local name without namespace
                local_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

                if local_name == descriptor:
                    code_value = None
                    namespace = None

                    # Extract CodeValue and Namespace
                    for child in elem:
                        child_local_name = (
                            child.tag.split("}")[-1] if "}" in child.tag else child.tag
                        )
                        if child_local_name == "CodeValue":
                            code_value = child.text
                        elif child_local_name == "Namespace":
                            namespace = child.text

                    if code_value and namespace:
                        descriptor_data.add((code_value, namespace))

            self._descriptor_cache[descriptor] = descriptor_data

        except Exception as e:
            print(
                f"Warning: Error loading descriptor file {descriptor_file}: {e}",
                file=sys.stderr,
            )
            self._descriptor_cache[descriptor] = set()
        finally:
            # Explicitly clean up the tree to prevent memory leaks
            if tree is not None:
                tree = None

    def validate_all(self) -> bool:
        """Validate all XML files in the samples directory."""
        if not self.samples_dir.exists():
            print(
                f"Error: Samples directory {self.samples_dir} does not exist",
                file=sys.stderr,
            )
            return False

        if not self.schemas_dir.exists():
            print(
                f"Error: Schemas directory {self.schemas_dir} does not exist",
                file=sys.stderr,
            )
            return False

        if not self.descriptors_dir.exists():
            print(
                f"Error: Descriptors directory {self.descriptors_dir} does not exist",
                file=sys.stderr,
            )
            return False

        # Find all XML files in samples directory
        xml_files = list(self.samples_dir.glob("*.xml"))

        if not xml_files:
            print(f"Warning: No XML files found in {self.samples_dir}", file=sys.stderr)
            return True

        print(f"Validating {len(xml_files)} XML files...")

        # Use parallel processing for better performance
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading

        # Thread-safe error collection
        error_lock = threading.Lock()

        def process_file(xml_file):
            temp_validator = None
            xml_doc = None
            try:
                # Create a temporary validator for thread safety
                temp_validator = XMLValidator(
                    str(self.samples_dir),
                    str(self.schemas_dir),
                    str(self.descriptors_dir),
                )
                temp_validator._schema_cache = self._schema_cache  # Share schema cache
                temp_validator._descriptor_cache = (
                    self._descriptor_cache
                )  # Share descriptor cache

                # Perform validation

                with open(xml_file, "rb") as xml_f:
                    xml_doc = etree.parse(xml_f)

                    temp_validator.validate_schema(xml_file, xml_doc)
                    temp_validator.validate_descriptors(xml_file, xml_doc)

                    # Merge errors thread-safely
                    with error_lock:
                        for file_key, errors in temp_validator.errors.items():
                            if file_key not in self.errors:
                                self.errors[file_key] = []
                            self.errors[file_key].extend(errors)

            except Exception as e:
                with error_lock:
                    file_key = os.path.basename(str(xml_file))
                    if file_key not in self.errors:
                        self.errors[file_key] = []
                    self.errors[file_key].append(
                        ValidationError(str(xml_file), 1, f"Processing error: {str(e)}")
                    )
            finally:
                xml_doc = None

                # Explicitly clean up temp validator to prevent memory leaks
                if temp_validator is not None:
                    temp_validator.errors.clear()
                    temp_validator = None

        # Process files in parallel
        with ThreadPoolExecutor(max_workers=min(4, len(xml_files))) as executor:
            futures = [
                executor.submit(process_file, xml_file) for xml_file in xml_files
            ]

            for i, future in enumerate(as_completed(futures)):
                print(f"Completed {i+1}/{len(xml_files)} files...")
                try:
                    future.result()  # This will raise any exceptions that occurred
                except Exception as e:
                    print(f"Error processing file: {e}", file=sys.stderr)

        return len(self.errors) == 0

    def print_errors(self) -> None:
        """Print all validation errors grouped by file."""
        if not self.errors:
            print("No validation errors found.")
            return

        for file_name in sorted(self.errors.keys()):
            print(f"\nErrors in {file_name}:")
            for error in self.errors[file_name]:
                print(f"  {error}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Validate XML files against schemas and descriptor definitions"
    )
    parser.add_argument(
        "--samples-dir",
        default="Samples/Sample XML",
        help="Directory containing sample XML files (default: Samples/Sample XML)",
    )
    parser.add_argument(
        "--schemas-dir",
        default="Schemas/Bulk",
        help="Directory containing XSD schema files (default: Schemas/Bulk)",
    )
    parser.add_argument(
        "--descriptors-dir",
        default="Descriptors",
        help="Directory containing descriptor XML files (default: Descriptors)",
    )

    args = parser.parse_args()

    # Convert relative paths to absolute paths based on script location
    script_dir = Path(__file__).parent.parent  # Go up one level from eng/ to root

    # Handle both relative and absolute paths
    if Path(args.samples_dir).is_absolute():
        samples_dir = Path(args.samples_dir)
    else:
        # For relative paths, resolve from the current working directory
        # if it looks like a relative path starting with ../, otherwise from script dir
        if args.samples_dir.startswith("../"):
            samples_dir = (Path.cwd() / args.samples_dir).resolve()
        else:
            samples_dir = script_dir / args.samples_dir

    if Path(args.schemas_dir).is_absolute():
        schemas_dir = Path(args.schemas_dir)
    else:
        if args.schemas_dir.startswith("../"):
            schemas_dir = (Path.cwd() / args.schemas_dir).resolve()
        else:
            schemas_dir = script_dir / args.schemas_dir

    if Path(args.descriptors_dir).is_absolute():
        descriptors_dir = Path(args.descriptors_dir)
    else:
        if args.descriptors_dir.startswith("../"):
            descriptors_dir = (Path.cwd() / args.descriptors_dir).resolve()
        else:
            descriptors_dir = script_dir / args.descriptors_dir

    try:
        validator = XMLValidator(
            str(samples_dir), str(schemas_dir), str(descriptors_dir)
        )

        success = validator.validate_all()
        validator.print_errors()

        if success:
            print("\nValidation completed successfully!")
            # Clear caches before exit to free memory
            validator.clear_caches()
            sys.exit(0)
        else:
            print(
                f"\nValidation failed with {len(validator.errors)} files containing errors."
            )
            # Clear caches before exit to free memory
            validator.clear_caches()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nValidation interrupted by user.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
