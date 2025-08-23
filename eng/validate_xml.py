#!/usr/bin/env python3
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

    def validate_schema(self, xml_file: Path) -> None:
        """Validate an XML file against its corresponding XSD schema."""
        try:
            # Find corresponding schema file
            schema_file = self._find_schema_file(xml_file)
            if not schema_file:
                self.add_error(
                    ValidationError(
                        str(xml_file), 1, "No corresponding schema file found"
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
            xml_doc = None
            try:
                with open(xml_file, "rb") as xml_f:
                    xml_doc = etree.parse(xml_f)

                if not schema.validate(xml_doc):
                    for error in schema.error_log:
                        self.add_error(
                            ValidationError(
                                str(xml_file),
                                error.line,
                                error.message,
                            )
                        )
            finally:
                # Explicitly clean up XML document
                if xml_doc is not None:
                    xml_doc = None

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

    def _find_schema_file(self, xml_file: Path) -> Path:
        """Find the corresponding XSD schema file for an XML file and return its absolute path."""
        xml_name = xml_file.stem

        # For descriptor files, they all use the Descriptors schema (quick check first)
        if xml_name.endswith("Descriptor"):
            schema_file = self.schemas_dir / "Descriptors.xsd"
            if schema_file.exists():
                return schema_file.resolve()

        # Special mappings for complex file names (as instance variable for better performance)
        if not hasattr(self, "_special_mappings"):
            self._special_mappings = {
                "AssessmentMetadata-SAT": "AssessmentMetadata",
                "AssessmentMetadata-ACT": "AssessmentMetadata",
                "AssessmentMetadata-Benchmarks-3rdGradeMath": "AssessmentMetadata",
                "AssessmentMetadata-Benchmarks-3rdGradeMathModified": "AssessmentMetadata",
                "AssessmentMetadata-Benchmarks-3rdGradeReading": "AssessmentMetadata",
                "AssessmentMetadata-Benchmarks-3rdGradeReadingModified": "AssessmentMetadata",
                "AssessmentMetadata-Benchmarks-3rdGradeReadingSpanish": "AssessmentMetadata",
                "AssessmentMetadata-EdPrep": "AssessmentMetadata",
                "AssessmentMetadata-LearningStandardsMastery": "AssessmentMetadata",
                "AssessmentMetadata-StateAssessment": "AssessmentMetadata",
                "StudentAssessment-ACT": "StudentAssessment",
                "StudentAssessment-Benchmarks-3rdGradeMath": "StudentAssessment",
                "StudentAssessment-Benchmarks-3rdGradeMathModified": "StudentAssessment",
                "StudentAssessment-Benchmarks-3rdGradeReading": "StudentAssessment",
                "StudentAssessment-Benchmarks-3rdGradeReadingModified": "StudentAssessment",
                "StudentAssessment-Benchmarks-3rdGradeReadingSpanish": "StudentAssessment",
                "StudentAssessment-EdPrep": "StudentAssessment",
                "StudentAssessment-LearningStandardsMastery": "StudentAssessment",
                "StudentAssessment-SAT": "StudentAssessment",
                "StudentAssessment-StateAssessment": "StudentAssessment",
                "EducationOrgCalendar-EdPrep": "EducationOrgCalendar",
                "EducationOrganization-EdPrep": "EducationOrganization",
                "MasterSchedule-EdPrep": "MasterSchedule",
                "StaffAssociation-EdPrep": "StaffAssociation",
                "StudentGrade-1stSixWeeks": "StudentGrade",
                "StudentGrade-2ndSixWeeks": "StudentGrade",
                "StudentGrade-3rdSixWeeks": "StudentGrade",
                "StudentGrade-4thSixWeeks": "StudentGrade",
                "StudentGrade-5thSixWeeks": "StudentGrade",
                "StudentGrade-6thSixWeeks": "StudentGrade",
                "StudentGradebook-EdPrep": "StudentGradebook",
                "StudentSectionAttendance-Tardy": "StudentAttendance",
                "Survey-EdPrep": "Survey",
            }

        # Check if there's a special mapping
        base_name = self._special_mappings.get(xml_name, xml_name)

        # Try direct mapping (e.g., Student.xml -> Interchange-Student.xsd)
        schema_candidates = [
            self.schemas_dir / f"Interchange-{base_name}.xsd",
            self.schemas_dir / f"{base_name}.xsd",
        ]

        for candidate in schema_candidates:
            if candidate.exists():
                return candidate.resolve()

        return None

    def validate_descriptors(self, xml_file: Path) -> None:
        """Validate descriptor URIs in an XML file against descriptor definitions."""
        content = None
        try:
            # Read file content once
            with open(xml_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Find all descriptor URIs using finditer for better performance
            for match in self.DESCRIPTOR_PATTERN.finditer(content):
                # Calculate line number by counting newlines up to match position
                line_number = content[: match.start()].count("\n") + 1

                namespace = match.group("namespace")
                descriptor = match.group("descriptor")
                code_value = match.group("codeValue").strip()

                # Validate the descriptor
                self._validate_descriptor_reference(
                    xml_file, line_number, namespace, descriptor, code_value
                )

        except Exception as e:
            self.add_error(
                ValidationError(
                    str(xml_file),
                    1,
                    f"Error reading file for descriptor validation: {str(e)}",
                )
            )
        finally:
            # Explicitly clear content to free memory
            content = None

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
                temp_validator.validate_schema(xml_file)
                temp_validator.validate_descriptors(xml_file)

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
