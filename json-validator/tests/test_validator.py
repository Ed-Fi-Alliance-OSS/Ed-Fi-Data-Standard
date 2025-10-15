"""
Tests for the DataLakeValidator class.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from json_validator.validator import DataLakeValidator, ValidationResult


class TestDataLakeValidator:
    """Test cases for the DataLakeValidator class."""

    def test_init_with_valid_inputs(self, temp_data_lake: Path, temp_openapi_file: Path) -> None:
        """Test validator initialization with valid inputs."""
        validator = DataLakeValidator(str(temp_data_lake), str(temp_openapi_file))

        assert validator.data_lake_root == temp_data_lake
        assert validator.openapi_spec_path == str(temp_openapi_file)
        assert len(validator.schemas) > 0
        assert "edFi_academicWeek" in validator.schemas
        assert "edFi_student" in validator.schemas
        assert "tpdm_candidate" in validator.schemas

    def test_get_schema_name_from_path(self, temp_data_lake: Path, temp_openapi_file: Path) -> None:
        """Test schema name extraction from file paths."""
        validator = DataLakeValidator(str(temp_data_lake), str(temp_openapi_file))

        # Test ed-fi paths
        academic_week_path = temp_data_lake / "ed-fi" / "academicWeeks" / "week-1.json"
        assert validator._get_schema_name_from_path(academic_week_path) == "edFi_academicWeek"

        student_path = temp_data_lake / "ed-fi" / "students" / "student-1.json"
        assert validator._get_schema_name_from_path(student_path) == "edFi_student"

        # Test tpdm paths
        candidate_path = temp_data_lake / "tpdm" / "candidates" / "candidate-1.json"
        assert validator._get_schema_name_from_path(candidate_path) == "tpdm_candidate"

        # Test invalid path
        invalid_path = temp_data_lake / "invalid.json"
        assert validator._get_schema_name_from_path(invalid_path) is None

    def test_pluralize_to_singular(self, temp_data_lake: Path, temp_openapi_file: Path) -> None:
        """Test pluralization logic."""
        validator = DataLakeValidator(str(temp_data_lake), str(temp_openapi_file))

        assert validator._pluralize_to_singular("academicWeeks") == "academicWeek"
        assert validator._pluralize_to_singular("students") == "student"
        assert validator._pluralize_to_singular("candidates") == "candidate"
        assert validator._pluralize_to_singular("categories") == "category"  # ies -> y rule
        assert validator._pluralize_to_singular("courses") == "course"

    def test_validate_file_success(self, temp_data_lake: Path, temp_openapi_file: Path) -> None:
        """Test successful file validation."""
        validator = DataLakeValidator(str(temp_data_lake), str(temp_openapi_file))

        student_file = temp_data_lake / "ed-fi" / "students" / "student-1.json"
        result = validator.validate_file(str(student_file))

        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert result.schema_name == "edFi_student"
        assert len(result.errors) == 0

    def test_validate_file_failure(self, temp_data_lake: Path, temp_openapi_file: Path) -> None:
        """Test file validation failure."""
        validator = DataLakeValidator(str(temp_data_lake), str(temp_openapi_file))

        # This file has missing required field
        student_file = temp_data_lake / "ed-fi" / "students" / "student-2.json"
        result = validator.validate_file(str(student_file))

        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert result.schema_name == "edFi_student"
        assert len(result.errors) > 0

    def test_validate_all(self, temp_data_lake: Path, temp_openapi_file: Path) -> None:
        """Test validation of all files."""
        validator = DataLakeValidator(str(temp_data_lake), str(temp_openapi_file))

        results, summary = validator.validate_all()

        assert len(results) == 4  # 4 JSON files in test data
        assert summary["total_files"] == 4
        assert summary["valid_files"] == 3  # only student-2.json is invalid
        assert summary["invalid_files"] == 1
        assert summary["success_rate"] == 75.0

    def test_get_available_schemas(self, temp_data_lake: Path, temp_openapi_file: Path) -> None:
        """Test getting available schemas."""
        validator = DataLakeValidator(str(temp_data_lake), str(temp_openapi_file))

        schemas = validator.get_available_schemas()

        assert isinstance(schemas, list)
        assert "edFi_academicWeek" in schemas
        assert "edFi_student" in schemas
        assert "tpdm_candidate" in schemas
        assert "edFi_schoolReference" in schemas

    @patch("requests.get")
    def test_load_openapi_spec_from_url(self, mock_get: Mock, temp_data_lake: Path, sample_openapi_spec: dict) -> None:
        """Test loading OpenAPI spec from URL."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.text = str(sample_openapi_spec).replace("'", '"').replace("True", "true")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        validator = DataLakeValidator(str(temp_data_lake), "https://api.example.com/spec.json")

        assert len(validator.schemas) > 0
        mock_get.assert_called_once()

    def test_init_with_nonexistent_file(self, temp_data_lake: Path) -> None:
        """Test initialization with non-existent OpenAPI file."""
        with pytest.raises(Exception):
            DataLakeValidator(str(temp_data_lake), "/nonexistent/spec.json")


class TestValidationResult:
    """Test cases for the ValidationResult class."""

    def test_validation_result_creation(self) -> None:
        """Test ValidationResult object creation."""
        result = ValidationResult(
            file_path="/path/to/file.json",
            schema_name="edFi_student",
            is_valid=True
        )

        assert result.file_path == "/path/to/file.json"
        assert result.schema_name == "edFi_student"
        assert result.is_valid is True
        assert result.errors == []

    def test_validation_result_with_errors(self) -> None:
        """Test ValidationResult with error messages."""
        errors = ["Missing required field", "Invalid format"]
        result = ValidationResult(
            file_path="/path/to/file.json",
            schema_name="edFi_student",
            is_valid=False,
            errors=errors
        )

        assert result.file_path == "/path/to/file.json"
        assert result.schema_name == "edFi_student"
        assert result.is_valid is False
        assert result.errors == errors
