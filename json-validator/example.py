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


def create_sample_data_lake() -> Path:
    """Create a sample data lake structure for demonstration."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create directory structure
    ed_fi_dir = temp_dir / "ed-fi"
    students_dir = ed_fi_dir / "students"
    academic_weeks_dir = ed_fi_dir / "academicWeeks"

    tpdm_dir = temp_dir / "tpdm"
    candidates_dir = tpdm_dir / "candidates"

    students_dir.mkdir(parents=True)
    academic_weeks_dir.mkdir(parents=True)
    candidates_dir.mkdir(parents=True)

    # Create sample student files
    student_data = {
        "id": "student-123",
        "studentUniqueId": "ST123456",
        "birthDate": "2010-05-15",
        "firstName": "Jane",
        "lastSurname": "Doe"
    }

    with open(students_dir / "student-1.json", "w") as f:
        json.dump(student_data, f, indent=2)

    # Create invalid student (missing required field)
    invalid_student = {
        "id": "student-456",
        "studentUniqueId": "ST789012",
        "birthDate": "2011-03-20",
        "firstName": "John"
        # Missing required lastSurname
    }

    with open(students_dir / "student-2.json", "w") as f:
        json.dump(invalid_student, f, indent=2)

    # Create sample academic week
    academic_week_data = {
        "id": "week-001",
        "weekIdentifier": "Week 1 Fall 2023",
        "beginDate": "2023-09-01",
        "endDate": "2023-09-05",
        "totalInstructionalDays": 5,
        "schoolReference": {
            "schoolId": 123
        }
    }

    with open(academic_weeks_dir / "academicWeek-1.json", "w") as f:
        json.dump(academic_week_data, f, indent=2)

    # Create sample candidate
    candidate_data = {
        "id": "candidate-001",
        "candidateIdentifier": "CD12345",
        "birthDate": "1990-01-01",
        "firstName": "Teacher",
        "lastSurname": "Candidate"
    }

    with open(candidates_dir / "candidate-1.json", "w") as f:
        json.dump(candidate_data, f, indent=2)

    print(f"Created sample data lake at: {temp_dir}")
    return temp_dir


def create_sample_openapi_spec() -> Path:
    """Create a sample OpenAPI specification file."""
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Ed-Fi API",
            "version": "1.0.0"
        },
        "components": {
            "schemas": {
                "edFi_student": {
                    "required": [
                        "birthDate",
                        "firstName",
                        "lastSurname",
                        "studentUniqueId"
                    ],
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "studentUniqueId": {
                            "maxLength": 32,
                            "type": "string",
                            "description": "A unique alphanumeric code assigned to a student."
                        },
                        "birthDate": {
                            "type": "string",
                            "format": "date"
                        },
                        "firstName": {
                            "type": "string"
                        },
                        "lastSurname": {
                            "type": "string"
                        }
                    }
                },
                "edFi_academicWeek": {
                    "required": [
                        "weekIdentifier",
                        "beginDate",
                        "endDate",
                        "totalInstructionalDays",
                        "schoolReference"
                    ],
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "weekIdentifier": {
                            "maxLength": 80,
                            "minLength": 5,
                            "type": "string",
                            "description": "The school label for the week."
                        },
                        "beginDate": {
                            "type": "string",
                            "format": "date"
                        },
                        "endDate": {
                            "type": "string",
                            "format": "date"
                        },
                        "totalInstructionalDays": {
                            "type": "integer"
                        },
                        "schoolReference": {
                            "$ref": "#/components/schemas/edFi_schoolReference"
                        }
                    }
                },
                "tpdm_candidate": {
                    "required": [
                        "candidateIdentifier",
                        "birthDate",
                        "firstName",
                        "lastSurname"
                    ],
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "candidateIdentifier": {
                            "maxLength": 32,
                            "minLength": 1,
                            "type": "string",
                            "description": "A unique alphanumeric code assigned to a candidate."
                        },
                        "birthDate": {
                            "type": "string",
                            "format": "date"
                        },
                        "firstName": {
                            "type": "string"
                        },
                        "lastSurname": {
                            "type": "string"
                        }
                    }
                },
                "edFi_schoolReference": {
                    "type": "object",
                    "properties": {
                        "schoolId": {
                            "type": "integer"
                        }
                    },
                    "required": ["schoolId"]
                }
            }
        }
    }

    temp_file = Path(tempfile.mktemp(suffix=".json"))
    with open(temp_file, "w") as f:
        json.dump(openapi_spec, f, indent=2)

    print(f"Created sample OpenAPI spec at: {temp_file}")
    return temp_file


def main() -> None:
    """Demonstrate the JSON validator functionality."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    print("Ed-Fi JSON Validator Example")
    print("=" * 40)

    # Create sample data
    data_lake_root = create_sample_data_lake()
    openapi_spec_file = create_sample_openapi_spec()

    try:
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

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(data_lake_root)
        openapi_spec_file.unlink()
        print(f"\nCleaned up temporary files")


if __name__ == "__main__":
    main()
