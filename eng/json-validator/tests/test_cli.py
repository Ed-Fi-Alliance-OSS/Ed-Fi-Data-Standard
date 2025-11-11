# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""
Tests for the CLI module.
"""

from unittest.mock import Mock, patch

import pytest

from json_validator.__main__ import main, print_summary, print_validation_results
from json_validator.validator import ValidationResult


class TestCLI:
    """Test cases for the CLI functionality."""

    def test_print_validation_results_valid_only(self, capsys) -> None:
        """Test printing results with only valid files."""
        results = [
            ValidationResult("/path/file1.json", "edFi_student", True),
            ValidationResult("/path/file2.json", "edFi_academicWeek", True)
        ]

        print_validation_results(results)
        captured = capsys.readouterr()

        assert "VALIDATION RESULTS" in captured.out
        assert "✓ VALID FILES (2):" in captured.out
        assert "/path/file1.json → edFi_student" in captured.out
        assert "/path/file2.json → edFi_academicWeek" in captured.out
        assert "✗ INVALID FILES" not in captured.out

    def test_print_validation_results_with_errors(self, capsys) -> None:
        """Test printing results with invalid files."""
        results = [
            ValidationResult("/path/file1.json", "edFi_student", True),
            ValidationResult("/path/file2.json", "edFi_student", False, ["Missing required field"])
        ]

        print_validation_results(results)
        captured = capsys.readouterr()

        assert "✓ VALID FILES (1):" in captured.out
        assert "✗ INVALID FILES (1):" in captured.out
        assert "ERROR: Missing required field" in captured.out

    def test_print_summary(self, capsys) -> None:
        """Test printing summary statistics."""
        summary = {
            "total_files": 10,
            "valid_files": 8,
            "invalid_files": 2,
            "success_rate": 80.0
        }

        print_summary(summary)
        captured = capsys.readouterr()

        assert "VALIDATION SUMMARY" in captured.out
        assert "Total files processed: 10" in captured.out
        assert "Valid files: 8" in captured.out
        assert "Invalid files: 2" in captured.out
        assert "Success rate: 80.0%" in captured.out

    @patch("sys.argv", ["validate-json", "--data-lake-root", "/tmp/test", "--openapi-spec", "spec.json", "--list-schemas"])
    @patch("json_validator.cli.DataLakeValidator")
    @patch("pathlib.Path.exists", return_value=True)
    def test_list_schemas(self, mock_exists: Mock, mock_validator_class: Mock, capsys) -> None:
        """Test listing available schemas."""
        # Mock validator instance
        mock_validator = Mock()
        mock_validator.get_available_schemas.return_value = ["edFi_student", "edFi_academicWeek"]
        mock_validator_class.return_value = mock_validator

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Available schemas (2):" in captured.out
        assert "edFi_student" in captured.out
        assert "edFi_academicWeek" in captured.out

    @patch("sys.argv", ["validate-json", "--data-lake-root", "/nonexistent", "--openapi-spec", "spec.json"])
    def test_nonexistent_data_lake(self, capsys) -> None:
        """Test error handling for non-existent data lake directory."""
        with patch("sys.argv", ["validate-json", "--data-lake-root", "/nonexistent", "--openapi-spec", "spec.json"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Data lake root directory does not exist" in captured.out

    @patch("sys.argv", ["validate-json", "--data-lake-root", "/tmp", "--openapi-spec", "spec.json", "--file", "nonexistent.json"])
    @patch("pathlib.Path.exists")
    def test_nonexistent_file(self, capsys) -> None:
        """Test error handling for non-existent file."""
        with patch("sys.argv", ["validate-json", "--data-lake-root", "/tmp", "--openapi-spec", "spec.json", "--file", "nonexistent.json"]):
            with patch("pathlib.Path.exists") as mock_exists:
                # Mock directory exists but file doesn't
                def side_effect_exists(self):
                    path_str = str(self)
                    if path_str == "/tmp":
                        return True
                    elif "nonexistent.json" in path_str:
                        return False
                    return True

                mock_exists.side_effect = side_effect_exists

                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1    @patch("sys.argv", ["validate-json", "--data-lake-root", "/tmp/test", "--openapi-spec", "spec.json"])
    @patch("json_validator.cli.DataLakeValidator")
    @patch("pathlib.Path.exists", return_value=True)
    def test_validation_with_failures(self, mock_exists: Mock, mock_validator_class: Mock, capsys) -> None:
        """Test CLI with validation failures."""
        # Mock validator instance
        mock_validator = Mock()
        mock_validator.validate_all.return_value = (
            [ValidationResult("/path/file1.json", "edFi_student", False, ["Error"])],
            {"total_files": 1, "valid_files": 0, "invalid_files": 1, "success_rate": 0.0}
        )
        mock_validator_class.return_value = mock_validator

        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with error code 1 when validation fails
        assert exc_info.value.code == 1

    @patch("sys.argv", ["validate-json", "--data-lake-root", "/tmp/test", "--openapi-spec", "spec.json", "--quiet"])
    @patch("json_validator.cli.DataLakeValidator")
    @patch("pathlib.Path.exists", return_value=True)
    def test_quiet_mode(self, mock_exists: Mock, mock_validator_class: Mock, capsys) -> None:
        """Test CLI in quiet mode."""
        # Mock validator instance
        mock_validator = Mock()
        mock_validator.validate_all.return_value = (
            [ValidationResult("/path/file1.json", "edFi_student", True)],
            {"total_files": 1, "valid_files": 1, "invalid_files": 0, "success_rate": 100.0}
        )
        mock_validator_class.return_value = mock_validator

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()

        # Should show summary but not detailed results
        assert "VALIDATION SUMMARY" in captured.out
        assert "VALIDATION RESULTS" not in captured.out

    @patch("sys.argv", ["validate-json", "--help"])
    def test_help_message(self, capsys) -> None:
        """Test help message display."""
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Validate JSON files in Ed-Fi data lake" in captured.out
        assert "--data-lake-root" in captured.out
        assert "--openapi-spec" in captured.out
