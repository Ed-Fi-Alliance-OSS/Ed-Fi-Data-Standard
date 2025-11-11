#!/usr/bin/env python3
"""
Simple test script to demonstrate the JSON validator functionality.
"""

import json
import tempfile
from pathlib import Path

from json_validator.validator import DataLakeValidator


def main():
    """Run a simple validation test."""
    # Create temporary OpenAPI spec
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "components": {
            "schemas": {
                "edFi_student": {
                    "required": ["studentUniqueId", "firstName", "lastSurname"],
                    "type": "object",
                    "properties": {
                        "studentUniqueId": {"type": "string"},
                        "firstName": {"type": "string"},
                        "lastSurname": {"type": "string"}
                    }
                }
            }
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(spec, f)
        spec_path = f.name

    # Create temporary data lake
    with tempfile.TemporaryDirectory() as temp_dir:
        data_path = Path(temp_dir)

        # Create structure
        students_dir = data_path / "ed-fi" / "students"
        students_dir.mkdir(parents=True)

        # Create valid student
        valid_student = {
            "studentUniqueId": "12345",
            "firstName": "John",
            "lastSurname": "Doe"
        }

        with open(students_dir / "student-1.json", "w") as f:
            json.dump(valid_student, f)

        # Test validation
        validator = DataLakeValidator(str(data_path), spec_path)
        results, summary = validator.validate_all()

        print(f"Validation Results:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Valid files: {summary['valid_files']}")
        print(f"  Success rate: {summary['success_rate']:.1f}%")

        for result in results:
            status = "✓" if result.is_valid else "✗"
            print(f"  {status} {Path(result.file_path).name} → {result.schema_name}")

        # Cleanup
        Path(spec_path).unlink()

        print("Test completed successfully!")


if __name__ == "__main__":
    main()
