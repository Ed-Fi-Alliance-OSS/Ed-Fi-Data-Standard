"""
Test fixtures and sample data for testing the JSON validator.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def sample_openapi_spec() -> Dict[str, Any]:
    """Sample OpenAPI specification for testing."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Ed-Fi API",
            "version": "1.0.0"
        },
        "components": {
            "schemas": {
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
                            "type": "string",
                            "description": ""
                        },
                        "weekIdentifier": {
                            "maxLength": 80,
                            "minLength": 5,
                            "type": "string",
                            "description": "The school label for the week.",
                            "x-Ed-Fi-isIdentity": True
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
                            "type": "string",
                            "description": ""
                        },
                        "studentUniqueId": {
                            "maxLength": 32,
                            "type": "string",
                            "description": "A unique alphanumeric code assigned to a student.",
                            "x-Ed-Fi-isIdentity": True
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
                            "type": "string",
                            "description": ""
                        },
                        "candidateIdentifier": {
                            "maxLength": 32,
                            "minLength": 1,
                            "type": "string",
                            "description": "A unique alphanumeric code assigned to a candidate.",
                            "x-Ed-Fi-isIdentity": True
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


@pytest.fixture
def sample_valid_academic_week() -> Dict[str, Any]:
    """Valid academic week JSON data."""
    return {
        "id": "week-001",
        "weekIdentifier": "Week 1 Fall 2023",
        "beginDate": "2023-09-01",
        "endDate": "2023-09-05",
        "totalInstructionalDays": 5,
        "schoolReference": {
            "schoolId": 123
        }
    }


@pytest.fixture
def sample_valid_student() -> Dict[str, Any]:
    """Valid student JSON data."""
    return {
        "id": "student-001",
        "studentUniqueId": "ST12345",
        "birthDate": "2010-05-15",
        "firstName": "Jane",
        "lastSurname": "Doe"
    }


@pytest.fixture
def sample_invalid_student() -> Dict[str, Any]:
    """Invalid student JSON data (missing required field)."""
    return {
        "id": "student-002",
        "studentUniqueId": "ST67890",
        "birthDate": "2011-03-20",
        "firstName": "John"
        # Missing required lastSurname
    }


@pytest.fixture
def temp_data_lake(
    sample_valid_academic_week: Dict[str, Any],
    sample_valid_student: Dict[str, Any],
    sample_invalid_student: Dict[str, Any]
) -> Path:
    """Create a temporary data lake structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_lake_root = Path(temp_dir)

        # Create ed-fi structure
        ed_fi_dir = data_lake_root / "ed-fi"
        academic_weeks_dir = ed_fi_dir / "academicWeeks"
        students_dir = ed_fi_dir / "students"

        academic_weeks_dir.mkdir(parents=True)
        students_dir.mkdir(parents=True)

        # Create tpdm structure
        tpdm_dir = data_lake_root / "tpdm"
        candidates_dir = tpdm_dir / "candidates"
        candidates_dir.mkdir(parents=True)

        # Write sample files
        with open(academic_weeks_dir / "academicWeek-1.json", "w") as f:
            json.dump(sample_valid_academic_week, f)

        with open(students_dir / "student-1.json", "w") as f:
            json.dump(sample_valid_student, f)

        with open(students_dir / "student-2.json", "w") as f:
            json.dump(sample_invalid_student, f)

        # Add a candidate file
        candidate_data = {
            "id": "candidate-001",
            "candidateIdentifier": "CD12345",
            "birthDate": "1990-01-01",
            "firstName": "Teacher",
            "lastSurname": "Candidate"
        }
        with open(candidates_dir / "candidate-1.json", "w") as f:
            json.dump(candidate_data, f)

        yield data_lake_root


@pytest.fixture
def temp_openapi_file(sample_openapi_spec: Dict[str, Any]) -> Path:
    """Create a temporary OpenAPI specification file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_openapi_spec, f)
        temp_file_path = Path(f.name)

    yield temp_file_path

    # Cleanup
    if temp_file_path.exists():
        temp_file_path.unlink()
