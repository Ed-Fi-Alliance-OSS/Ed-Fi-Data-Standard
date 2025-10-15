#!/usr/bin/env python3
"""
Example usage of the Ed-Fi JSON validator.

This script demonstrates how to use the DataLakeValidator programmatically
to validate JSON files against Ed-Fi OpenAPI specifications.
"""

import json
import logging
import tempfile
from pathlib import Path

from json_validator.validator import DataLakeValidator


def main() -> None:
    """Demonstrate the JSON validator functionality."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    print("Ed-Fi JSON Validator Example")
    print("=" * 40)

    # Create sample data
    data_lake_root = "./sample"
    openapi_spec_file = "https://api.ed-fi.org/v7.2/api/metadata/data/v3/resources/swagger.json"

    # Initialize validator
    print("\n1. Initializing validator...")
    validator = DataLakeValidator(str(data_lake_root), str(openapi_spec_file))

    # List available schemas
    print("\n2. Available schemas:")
    schemas = validator.get_available_schemas()
    for schema in sorted(schemas):
        print(f"   - {schema}")

    # Validate all files
    print("\n3. Validating all JSON files...")
    results, summary = validator.validate_all()

    # Print results
    print("\n4. Validation Results:")
    print("-" * 40)

    for result in results:
        status = "✓" if result.is_valid else "✗"
        print(f"{status} {result.file_path}")
        print(f"   Schema: {result.schema_name}")
        if result.errors:
            for error in result.errors:
                print(f"   Error: {error}")
        print()

    # Print summary
    print("5. Summary:")
    print("-" * 40)
    print(f"Total files: {summary['total_files']}")
    print(f"Valid files: {summary['valid_files']}")
    print(f"Invalid files: {summary['invalid_files']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")

    # Validate a single file
    print("\n6. Validating single file...")
    student_file = data_lake_root / "ed-fi" / "students" / "student-1.json"
    single_result = validator.validate_file(str(student_file))

    status = "✓" if single_result.is_valid else "✗"
    print(f"{status} {single_result.file_path}")
    print(f"   Schema: {single_result.schema_name}")
    if single_result.errors:
        for error in single_result.errors:
            print(f"   Error: {error}")


if __name__ == "__main__":
    main()
