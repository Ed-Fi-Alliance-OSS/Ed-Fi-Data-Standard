"""
Command-line interface for the Ed-Fi JSON validator.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from json_validator.validator import DataLakeValidator, ValidationResult


def setup_logging(log_level: str) -> None:
    """Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def print_validation_results(results: List[ValidationResult]) -> None:
    """Print detailed validation results.

    Args:
        results: List of validation results
    """
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)

    # Group results by status
    valid_results = [r for r in results if r.is_valid]
    invalid_results = [r for r in results if not r.is_valid]

    if valid_results:
        print(f"\n✓ VALID FILES ({len(valid_results)}):")
        for result in valid_results:
            print(f"  {result.file_path} → {result.schema_name}")

    if invalid_results:
        print(f"\n✗ INVALID FILES ({len(invalid_results)}):")
        for result in invalid_results:
            print(f"  {result.file_path} → {result.schema_name}")
            for error in result.errors:
                print(f"    ERROR: {error}")


def print_summary(summary: dict) -> None:
    """Print validation summary statistics.

    Args:
        summary: Dictionary containing summary statistics
    """
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Total files processed: {summary['total_files']}")
    print(f"Valid files: {summary['valid_files']}")
    print(f"Invalid files: {summary['invalid_files']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    print("="*80)


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Validate JSON files in Ed-Fi data lake against OpenAPI schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate using local OpenAPI spec
  %(prog)s --data-lake-root /path/to/datalake --openapi-spec /path/to/spec.json

  # Validate using remote OpenAPI spec
  %(prog)s --data-lake-root /path/to/datalake --openapi-spec https://api.ed-fi.org/spec.json

  # Validate single file
  %(prog)s --data-lake-root /path/to/datalake --openapi-spec spec.json --file student-1.json
        """
    )

    parser.add_argument(
        "--data-lake-root",
        required=True,
        help="Root directory of the data lake containing JSON files"
    )

    parser.add_argument(
        "--openapi-spec",
        required=True,
        help="Path or URL to the OpenAPI specification file (JSON or YAML)"
    )

    parser.add_argument(
        "--file",
        help="Validate a specific file instead of all files"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output summary, suppress detailed results"
    )

    parser.add_argument(
        "--list-schemas",
        action="store_true",
        help="List available schemas and exit"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Validate arguments
        data_lake_path = Path(args.data_lake_root)
        if not data_lake_path.exists():
            print(
                f"Error: Data lake root directory does not exist: "
                f"{data_lake_path}"
            )
            sys.exit(1)

        # Initialize validator
        logger.info("Initializing Ed-Fi JSON validator...")
        validator = DataLakeValidator(
            args.data_lake_root, args.openapi_spec
        )

        # List schemas if requested
        if args.list_schemas:
            schemas = validator.get_available_schemas()
            print(f"\nAvailable schemas ({len(schemas)}):")
            for schema in sorted(schemas):
                print(f"  {schema}")
            sys.exit(0)

        # Validate files
        if args.file:
            # Validate single file
            file_path = data_lake_path / args.file
            if not file_path.exists():
                print(f"Error: File does not exist: {file_path}")
                sys.exit(1)

            result = validator.validate_file(str(file_path))
            results = [result]
            summary = {
                "total_files": 1,
                "valid_files": 1 if result.is_valid else 0,
                "invalid_files": 0 if result.is_valid else 1,
                "success_rate": 100.0 if result.is_valid else 0.0
            }
        else:
            # Validate all files
            results, summary = validator.validate_all()

        # Output results
        if not args.quiet:
            print_validation_results(results)

        print_summary(summary)

        # Exit with error code if any files failed validation
        if summary["invalid_files"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
